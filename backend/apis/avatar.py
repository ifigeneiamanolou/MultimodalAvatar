from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from pathlib import Path
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
from phonemizer.separator import Separator
from phonemizer.backend import EspeakBackend
from pandas import DataFrame, read_csv, concat
import numpy as np
from phonemizer.backend.espeak.wrapper import EspeakWrapper

# ================ Configuration ================

# Espeak configuration for phoneme detection
EspeakWrapper.set_library(
    r"C:/Program Files/eSpeak NG/libespeak-ng.dll"
)

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   

# Environment variables
load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]

# Servers
app = FastAPI()
tts = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)
client = OpenAI(api_key = OPENAI_API_KEY)
backend = EspeakBackend(preserve_punctuation = True, 
                        with_stress = True,
                        language = "en-us")
# Load the whisper model
model = WhisperModel(model_size_or_path="small", device="cpu", compute_type="int8")        # Connect to strong GPU

# Request body pydantic models
class UserInput(BaseModel):
    input : str
    session_id : str = "default"

class UserInputWithType(UserInput):
    interview_type : int               # 1 corresponds to user being the interviewer and 2 to user being the interviewee

# Response Body pydantic models
class ResponseModel(BaseModel):
    success : bool
    data : str
    message : str
    meta : dict = {}

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code = 422,
        content = jsonable_encoder({"detail": exc.errors(), "body" : exc.body}),
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8081"],          # Change in production    
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True      
)

# ================ Custom classes ================
class ConnectionManager:        # Class to manage mutliple web socket clients
    def __init__(self):
        self.active_connections : list[WebSocket] = []

    async def connect(self, connection : WebSocket):
        await connection.accept()
        self.active_connections.append(connection)

    async def disconnect(self, connection : WebSocket):
        self.active_connections.remove(connection)

    async def send_personal(self, connection : WebSocket, data : str):      # Send data to a single client / websocket
        await connection.send_text(data)

    async def broadcast(self, data : str):
        for connection in self.active_connections:
            await connection.send_text(data)

manager = ConnectionManager()

# ================ Helper functions ================

# Generate an NL response given the user input and the template file
def get_answer(input : str, template_path : Path) -> str:
    # Read the template 
    with open(template_path, "r") as f:
        prompt = f.read()

    try:
        answer = client.chat.completions.create(
            model="gpt-4o-mini",                    # To change during production
            input = prompt + input,
            prompt_cache_retention = "24h",         # extended prompt cache retention  
        )
        return answer.choices[0].message.content
    except RateLimitError as e:
        raise HTTPException(status_code = 429, detail = f"Rate limit exceeded: {e}")
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error when making an OpenAI call : {e}")

# Generate artkit coefficients from input text using phonemization and the PhoBlendDataset
async def generateAnimations(text : str) -> DataFrame:
    try:
        result = backend.phonemize(
            text, 
            separator = Separator(phone = None, syllable = "|", word = " "),
            njobs = 4
        )       # returns list[str]
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error when phonemizing the text : {e}")

    # Load the dictionary of phonemes to blendhapes
    try:
        db = read_csv(os.path.join(BASE_DIR, "../data/PhoBlendDataset.csv"))
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error when loading the PhoBlendDataset : {e}")

    # Extract the list of phonemes
    phonemes = result[0].replace("|", " ").split()
    phoCol = db["Phoneme"]
    _, c = db.shape
    artkit = DataFrame(dtype = float)

    for pho in phonemes:
        # Row number for the given phoneme
        index = np.where(phoCol ==  pho)[0]

        # Blendhsape coeffiecients
        coeff = db.iloc[index, 2 : c - 1]

        # Add coefficients to the dataframe
        artkit = concat([artkit, DataFrame([coeff])], ignore_index = True)

    # Save the blendshape coeffients
    path = next_path(os.path.join(BASE_DIR, "../data/processed/blendshape-%s.csv"))
    try:
        artkit.to_csv(path, index=False)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error when saving the blendshape coefficients : {e}")

    return artkit

# Finds the next available path using binary search
def next_path(path_pattern : str) -> str:
    i = 1
    while os.path.exists(path_pattern % i):
        i = i * 2
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) 
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

    return path_pattern % b

# ================= Web sockets ================

# Perform automatic speech recognition using Whisper
@app.websocket("/asr")
async def speechRecognition(websocket : WebSocket):
    await manager.connect(websocket)        # Connect the client to the websocket manager

    try:
        while True:
            # Receive data from the client
            data = await websocket.receive_bytes()  
            
            # Save raw audio into a webm file   
            path = next_path(os.path.join(BASE_DIR, "../data/raw/audio-%s.webm"))
            with open(path, "wb") as f:
                f.write(data)
            
            try:
                # Perform audio transcription
                segments, _ = model.transcribe(
                    path,                     # Absolute path to webm file stored locally
                    language = "en",
                    no_speech_threshold=0.4,  # default is 0.6
                    log_prob_threshold=-1.0,
                    condition_on_previous_text=False
                )
                text = " ".join([segment.text for segment in segments])

                # Save the transcription result
                path = next_path(os.path.join(BASE_DIR, "../data/processed/transcription-%s.txt"))
                with open(path, "w") as f:
                    f.write(text)

                # Send back the result of the transcription to the frontend
                await manager.send_personal(websocket, text)
            except Exception as e:
                await manager.send_personal(websocket, f"Error {e}")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error when performing speech recognition : {e}")
    finally:
        await manager.disconnect(websocket)

# Endpoint to connect to the remote server (pixel streaming) and send back the blendshape coefficients in real time
@app.websocket("/blendshapes")
async def sendBlendshapes(websocket : WebSocket):
    pass

# ================= API endpoints ================

# Generate an NLP response as part of the interview
@app.post("/response")
async def generateTextResponse(user_input : UserInputWithType):
    # Retrieve file name to save the response
    path = next_path(os.path.join(BASE_DIR, "../data/raw/response-%s.txt"))

    # Retrieve template file for the prompt
    interview_type = user_input.interview_type
    template_path = os.path.join(BASE_DIR, f"../data/templates/interview{interview_type}.md")

    # Generate response from OpenAI
    response = get_answer(user_input.input, template_path)

    # Save the response to a file                               
    with open(path, "w") as f:
        f.write(response)

    # Return the response to the frontend server
    return {
        "success" : True,
        "data" : response, 
        "message" : "Successful answer generation"
    }
    
# Generate audio from text using ElevanLabs TTS and generate blendshape coefficients from the text
@app.post("/tts")
async def generateAudio(user_input : UserInput):
    # Generate animations
    text = user_input.input
    artkit = await generateAnimations(text)

    # Generate audio
    try:
        audio = tts.text_to_speech.with_raw_response.convert(
            text = text,
            voice_id = "JBFqnCBsd6RMkjVDRZzb",  # "George" 
            model_id = "eleven_flash_v2_5",            
            output_format = "mp3_44100_128",
            language_code = "en",
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error during TTS : {e}")

    # Save the audio
    path = next_path(os.path.join(BASE_DIR, "../data/processed/tts-%s.mp3"))
    with open(path, "wb") as f:
        f.write(audio.data)

    # Save the coefficients
    pathArtKit = next_path(os.path.join(BASE_DIR, "../data/processed/blendshape-%s.csv"))
    with open(pathArtKit, "w") as f:
        f.write(artkit.to_csv(index = False))

    return {
        "success" : True,
        "data" : "", 
        "message" : "Audio and ArtKit coefficients generated successfully"
    }

# Generate an NLP response as feedback to the user after the interview and send it back to the frontend
@app.post("/feedback")
async def generateFeedback(user_input : UserInput) -> ResponseModel:         # User input is the whole conversation history in text form
    conv = user_input.input
    template_path = os.path.join(BASE_DIR, "../data/templates/feedback.md")
    feedback = get_answer(conv, template_path)
    return {
        "success" : True,
        "data" : feedback, 
        "message" : "Successful feedback generation"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "127.0.0.1", port = 8000, ws_ping_interval = 20, ws_ping_timeout = 60)