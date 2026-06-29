import json
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
from apis.models import Messages, ResponseModel, UserInput, UserInputWithType
from apis.dependancies import router as DepRouter
from apis.database import router as DbRouter
from apis.databaseConnection import router as DbConnRouter

# ================ Configuration ================

# Espeak configuration for phoneme detection
EspeakWrapper.set_library(
    r"C:/Program Files/eSpeak NG/libespeak-ng.dll"
)

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
SAMPLE_RATE = 16000
CHUNK_SAMPLES = 4 * SAMPLE_RATE    # 4 seconds
OVERLAP_SAMPLES = int(0.5 * SAMPLE_RATE)  # 0.5 seconds

# Environment variables
load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
HF_TOKEN = os.environ["HF_TOKEN"]       # For Whisper

# Servers
app = FastAPI()
tts = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)
client = OpenAI(api_key = OPENAI_API_KEY)
backend = EspeakBackend(preserve_punctuation = True, 
                        language = "en-us")
# Load the whisper model
model = WhisperModel(model_size_or_path="small", device="cpu", compute_type="int8")       
# With access to a GPU
# model = WhisperModel(model_size_or_path="large-v3-turbo", device = "cuda", compute_type = "int8")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8081",
                     "http://localhost:8082"],          # Change in production    
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True      
)

# Templates
template_path1 = os.path.join(BASE_DIR, "../../data/templates/interview1.md")      # Bot : interviewer
with open(template_path1, "r") as f:
    prompt1 = f.read()

template_path2= os.path.join(BASE_DIR, "../../data/templates/interview2.md")       # Bot : interviewee
with open(template_path2, "r") as f:
    prompt2 = f.read()

feedback_path1 = os.path.join(BASE_DIR, "../../data/templates/feedback1.md")         # Bot : interviewer
with open(feedback_path1, "r") as f:
    feedback_prompt1 = f.read()

feedback_path2 = os.path.join(BASE_DIR, "../../data/templates/feedback2.md")         # Bot : interviewee
with open(feedback_path2, "r") as f:
    feedback_prompt2 = f.read()

# Dictionaries
try:
    db = read_csv(os.path.join(BASE_DIR, "../../data/PhoBlendDataset.csv"))
except Exception as e:
    raise HTTPException(status_code = 500, detail = f"Error when loading the PhoBlendDataset : {e}")

# Connected FastAPI routers
app.include_router(DbConnRouter)
app.include_router(DbRouter)
app.include_router(DepRouter)

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

# Generate an NLP response given the user input and the template file
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
        raise HTTPException(status_code = 500, detail = {e})

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
    path = next_path(os.path.join(BASE_DIR, "../../data/raw/audio-%s.webm"))

    try:
        while True:
            # Receive data from the client
            data = await websocket.receive_bytes()  
            
            # Save raw audio into a webm file   
            path = next_path(os.path.join(BASE_DIR, "../../data/raw/audio-%s.webm"))
            with open(path, "wb") as f:
                f.write(data)

            try:
                # Perform audio transcription
                segments, _ = model.transcribe(
                    path,                     # Absolute path to webm file stored locally
                    language = "en",
                    vad_filter = True,        # Address hallucination
                    vad_parameters = dict(
                        min_silence_duration_ms=500,
                        speech_pad_ms=400
                    ),
                    condition_on_previous_text=False,
                    beam_size = 1             # Faster inference
                )
                text = " ".join([segment.text for segment in segments])

                # Save the transcription result
                path = next_path(os.path.join(BASE_DIR, "../../data/processed/transcription-%s.txt"))
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
# Perform ASR using chunk streaming with overlap
@app.post("/asrChunks")
async def transcribe_chunk(data: bytes) -> str:
    # Convert input raw data into a numpy array
    np_array = np.frombuffer(data, dtype = np.int16)

    # Normalize data between -1 and 1
    normalized = np_array / np.linang.norm(np_array)

    path = next_path(os.path.join(BASE_DIR, "../../data/raw/audio-%s.webm"))
            
    # Save raw audio into a webm file   
    path = next_path(os.path.join(BASE_DIR, "../../data/raw/audio-%s.webm"))
    with open(path, "wb") as f:
        f.write(data)

    # Split raw binary data into 4 second chunks with 0.5 second overlap
    total_size = len(normalized)
    start = 0
    audio_chunks = np.empty(shape = ())

    while start < total_size:
        end = min(start + CHUNK_SAMPLES, total_size)
        chunk = data[start : end]
        audio_chunks.append(chunk)
    
    # Perform audio transcription
    segments, _ = model.transcribe(
        audio_chunks,
        language = "en",                                        # To remove in production
        no_speech_threshold=0.6,                                # Discard segments with no speech confidence higher than 0.6
        beam_size=1,                                            # Improved latency
        condition_on_previous_text=False,                       # Eliminate hallucination drift
        vad_filter=True,                                        # Voice activity detection
        vad_parameters=dict(min_silence_duration_ms = 500)
    )
    overlap_sec = OVERLAP_SAMPLES / SAMPLE_RATE
    chunk_sec = CHUNK_SAMPLES / SAMPLE_RATE
    text =  " ".join(
        seg.text.strip() for seg in segments
        if seg.start >= overlap_sec and seg.start < chunk_sec - overlap_sec
    )

    # Save the transcription result
    path = next_path(os.path.join(BASE_DIR, "../../data/processed/transcription-%s.txt"))
    with open(path, "w") as f:
        f.write(text)

    return text

# Generate an NLP response as part of the interview and save it to a txt file
@app.post("/response")
async def generateTextResponse(user_input : UserInputWithType) -> ResponseModel:
    # Retrieve file name to save the response
    path = next_path(os.path.join(BASE_DIR, "../../data/raw/response-%s.txt"))

    # Generate response from OpenAI
    try:
        response = get_answer(
            input = [
                {
                    "role" : "user",
                    "content" : [
                        {
                            "type": "input_text",
                            "text": user_input.input
                        }
                    ]
                }
            ],
            instructions = prompt1 if user_input.interview_type == 1 else prompt2
        )
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during response generation : {e}"
        }
    
    # Save the response to a file 
    try:                              
        with open(path, "w") as f:
            f.write(response)
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during response upload : {e}"
        }

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
        path = next_path(os.path.join(BASE_DIR, "../../data/processed/blendshape-%s.csv"))
        artkit.to_csv(path, header = False)
    except Exception as e:
        return {
            "success" : False,
            "data" : "",
            "message" : f"Error during coefficient generation and upload : {e}"
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
        pathAudio = next_path(os.path.join(BASE_DIR, "../../data/processed/tts-%s.mp3"))
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

# Save the whole conversation
@app.post("/reset")
async def resetConversation(messages : Messages) -> ResponseModel:
    path = next_path(os.path.join(BASE_DIR, "../../data/feedback/conversation-%s.json"))
    try:
        with open(path, "w", encoding = "utf-8") as json_file:
            json.dump(messages.dict(), json_file, indent = 4)
        return{
            "success" : True,
            "data" : "",
            "message" : "Successful reset and upload of conversation"
        }
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during conversation upload : {e}"
        }

# Generate an NLP response as feedback to the user after the interview and send it back to the frontend
@app.post("/feedback")
async def generateFeedback(messages : Messages) -> ResponseModel:         
    path = next_path(os.path.join(BASE_DIR, "../../data/feedback/conversation-%s.json"))
    
    # Save the conversation in local storage
    try:
        with open(path, "w", encoding = "utf-8") as json_file:
            json.dump(messages.dict(), json_file, indent = 4)
        print(f"Data successfully uploaded to {path}")
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during conversation upload : {e}"
        }
    
    # Retrieve file name to save the response and instructions depending on the user role
    pathResponse = next_path(os.path.join(BASE_DIR, "../../data/feedback/feedback-%s.txt"))
    feedback_prompt = feedback_prompt1 if messages.interviewer == "interviewer" else feedback_prompt2

    # Generate feedback using OpenAI
    try:
        response = get_answer(
            input = [
                {
                    "role" : "user",
                    "content" : [
                        {
                            "type": "input_text",
                            "text": json.dumps(messages.data)
                        }
                    ]
                }
            ],
            instructions = feedback_prompt
        )
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during feedback generation : {e}"
        }

    # Save the response to a file  
    try:                             
        with open(pathResponse, "w") as f:
            f.write(response)
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during feedback upload : {e}"
        }

    # Return the response to the frontend server to be displayed to the feedback box
    return {
        "success" : True,
        "data" : response, 
        "message" : "Successful answer generation"
    }