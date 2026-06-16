from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from faster_whisper import WhisperModel
import os
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
import uuid

app = FastAPI()

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key = OPENAI_API_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8081", "http://127.0.0.1:8081"],       
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True      
)

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

# Load the whisper model
model = WhisperModel(model_size_or_path="small", compute_type = "float32")        # Connect to strong GPU

# Perform automatic speech recognition using Whisper
@app.websocket("/asr")
async def speechRecognition(websocket : WebSocket):
    await manager.connect(websocket)        # Connect the client to the websocket manager

    try:
        while True:
            # Receive data from the client
            data = await websocket.receive_bytes()   
            await manager.send_personal(websocket, "Received input audio, processing ...")   

            try:
                # Convert from audio data to numpy integer array
                audio_data = np.frombuffer(data, dtype = np.int16).astype(np.float32) / 32768.0

                # Perform audio transcription
                segments, _ = model.transcribe(
                    audio_data, 
                    language = "en",
                    no_speech_threshold=0.4,  # default is 0.6
                    log_prob_threshold=-1.0,
                    condition_on_previous_text=False,
                    initial_prompt = "ignore noise, white space, musical background sounds, and transcribe the part that speaks. Don't transcribe empty audio"
                )
                text = " ".join([segment.text for segment in segments])

                # Send back the result of the transcription to the frontend
                await manager.send_personal(websocket, text)
            except Exception as e:
                await manager.send_personal(websocket, f"Error {e}")
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        await manager.disconnect(websocket)

# Generate an NLP response given a text or audio user input
@app.websocket("/response")
async def generateTextResponse(websocket : WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            # Receive text from the client
            user_input = await websocket.receive_text()  

            # Download a text file with the response
            filename = uuid.uuid4().hex + ".txt"
            directory = "../data/processed"

            # Generate response from OpenAI
            response = get_answer(user_input)

            # Save the response to a file                                   !! TO TRANSITION TO JSON
            with open(os.path.join(directory, filename), "w") as f:
                f.write(response)

            # Send back via the web socket
            await manager.send_personal(websocket, response)
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        await manager.disconnect(websocket)

def get_answer(input, fallback = "Default answer"):
    try:
        answer = client.responses.create(
                    model = "gpt-5.4-mini",
                    input = input
        )
        return answer.output_text
    except RateLimitError as e:
        return fallback

# Some way to control facial animation on the right of the screen
@app.websocket("/avatar")
async def generateAnimations(websocket : WebSocket):
    await manager.connect(websocket)        # Connect the client to the websocket manager

    try:
        data = await websocket.receive_text()
    except WebSocketDisconnect:
        print("Client Disconnected")
    finally:
        await manager.disconnect(websocket)
