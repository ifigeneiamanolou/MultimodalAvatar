from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from pathlib import Path
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import pyloudnorm as pyln
import soundfile as sf
import os
import base64
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
import pandas as pd
# import time

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
HF_TOKEN = os.environ["HF_TOKEN"]

# Servers
app = FastAPI()
tts = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)
client = OpenAI(api_key = OPENAI_API_KEY)
backend = EspeakBackend(preserve_punctuation = True, 
                        language = "en-us")
# Load the whisper model
model = WhisperModel(model_size_or_path="small", device="cpu", compute_type="int8")        # Connect to strong GPU

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8081",
                     "http://localhost:8082"],          # Change in production    
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True      
)

# Templates
template_path1 = os.path.join(BASE_DIR, "../data/templates/interview1.md")      # Bot : interviewer
with open(template_path1, "r") as f:
    prompt1 = f.read()

template_path2= os.path.join(BASE_DIR, "../data/templates/interview2.md")       # Bot : interviewee
with open(template_path2, "r") as f:
    prompt2 = f.read()

feedback_path = os.path.join(BASE_DIR, "../data/templates/feedback.md")
with open(feedback_path, "r") as f:
    feedback_prompt = f.read()

# Dictionaries
try:
    db = read_csv(os.path.join(BASE_DIR, "../data/PhoBlendDataset.csv"))
except Exception as e:
    raise HTTPException(status_code = 500, detail = f"Error when loading the PhoBlendDataset : {e}")

# ================== Pydantic models ===================

# Request body pydantic models
class UserInput(BaseModel):
    input : str
    session_id : str = "default"

class UserInputWithType(UserInput):
    interview_type : int            # 1 corresponds to user being the interviewer and 2 to user being the interviewee

# Response Body pydantic models
class ResponseModel(BaseModel):
    success : bool
    data : str | dict
    message : str
    meta : dict = {}

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
def get_answer(input : str, instructions : str) -> str:

    try:
        answer = client.responses.create(
            model="gpt-4o-mini",                   # To change during production
            instructions = instructions,
            input = input,
            prompt_cache_retention = "24h",         # extended prompt cache retention  
        )
        return answer.output_text
    except RateLimitError as e:
        return "No API credit"
    except Exception as e:
        return f"Error when generating the response : {e}"

# Generate artkit coefficients from input text using phonemization and the PhoBlendDataset
async def generateAnimations(text : str) -> DataFrame:
    try:
        result = backend.phonemize(
            text = list(text),
            separator = Separator(phone = " ", syllable = "|", word = None),
        )       # returns list[str]
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error when phonemizing the text : {e}")

    # Extract the list of phonemes
    phonemes = [p.split(" ") for p in result]
    phonemes = sum(phonemes, [])
    phonemes = [p for p in phonemes if p != '']
    _, c = db.shape
    artkit = DataFrame()       # Empty dataframe to store the coefficients

    for pho in phonemes:
        # Row number for the given phoneme
        index = np.where(db.iloc[:, 1] ==  pho)[0]

        # Handle the case the phoneme is not found in the dictionary
        if index.size <= 0:
            coeff = pd.Series([0] * c)

        # Blendhsape coeffiecients for the given phoneme
        coeff = db.iloc[index, 2 : c].reset_index(drop = True)

        # Add coefficients to the dataframe
        artkit = concat([artkit, coeff], ignore_index = True)

    # Return the blendshape coefficients
    return artkit

# Finds the next available path using binary search
def next_path(path_pattern : str) -> str:
    i = 1
    while os.path.exists(path_pattern % i):
        i = i * 2
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

    return path_pattern % b

# ================= Web sockets ================

# Perform automatic speech recognition using Whisper and generate a response from OpenAI
@app.websocket("/asr")
async def speechRecognition(websocket : WebSocket):
    await manager.connect(websocket)        # Connect the client to the websocket manager
    path = next_path(os.path.join(BASE_DIR, "../data/raw/audio-%s.webm"))
    chunks = []

    try:
        # Save raw audio into a webm file   
        with open(path, "wb") as f:
            while True:
                # Receive data from the client
                data = await websocket.receive_bytes()

                # Write the data
                f.write(data)

            # data, rate = sf.read(path)                          # load audio 
            # meter = pyln.Meter(rate)                            # BS.1770 meter (maximum peak level)
            # loudness = meter.integrated_loudness(data)          # measure loudness

            # if(loudness <= -70):
            #     print("silent")
            #     await manager.send_personal(websocket, "")
            #     return
            
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
        print(f"Error during WebSocket connection : {e}")
    finally:
        await manager.disconnect(websocket)

# Endpoint to connect to the remote server (pixel streaming) and send back the blendshape coefficients in real time
@app.websocket("/blendshapes")
async def sendBlendshapes(websocket : WebSocket):
    pass

# ================= API endpoints ================

# Generate an NLP response as part of the interview and save it to a txt file
@app.post("/response")
async def generateTextResponse(user_input : UserInputWithType):
    # Retrieve file name to save the response
    path = next_path(os.path.join(BASE_DIR, "../data/raw/response-%s.txt"))

    # Generate response from OpenAI
    response = get_answer(
        user_input.input,
        prompt1 if user_input.interview_type == 1 else prompt2
    )

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
async def generateAudio(user_input : UserInput) -> ResponseModel:
    text = user_input.input

    # ================= Blendshape generation ===============
    try:
        artkit = await generateAnimations(text)
        path = next_path(os.path.join(BASE_DIR, "../data/processed/blendshape-%s.csv"))
        artkit.to_csv(path, header = False)
    except Exception as e:
        return {
            "success" : False,
            "data" : "",
            "message" : f"Error during coefficient generation : {e}"
        }

    # ================ TTS generation =================
    try:
        audio = tts.text_to_speech.convert(
            text = text,
            voice_id = "JBFqnCBsd6RMkjVDRZzb",  # "George" 
            model_id = "eleven_flash_v2_5",            
            language_code = "en",
            output_format = "mp3_22050_32",
        )
    except Exception as e:
        return {
            "success" : False,
            "data" : "", 
            "message" : f"Error during TTS conversion : {e}"
        }
    
    # ================ Audio upload ===================
    try:
        pathAudio = next_path(os.path.join(BASE_DIR, "../data/processed/tts-%s.mp3"))
        audio_chunks = b"".join(chunk for chunk in audio if chunk)
        with open(pathAudio, "wb") as f:
            f.write(audio_chunks)
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during audio upload : {e}"
        }
    
    return {
        "success" : True,
        "data" : {
            "audio_path" : pathAudio, 
            "blendshape_path" : path, 
            "audio" : base64.b64encode(audio_chunks).decode("utf-8")}, 
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