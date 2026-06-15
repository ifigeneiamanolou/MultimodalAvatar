from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from faster_whisper import WhisperModel

app = FastAPI()
origins = [
    "http://localhost:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True
)

@app.websocket("/wb")
async def wesocketendpoint(websocket : WebSocket):
    await websocket.accept()

    try:
        while True:
            # Receive data
            data = await websocket.receive_bytes()

            # Convert from audio data to numpy integer array
            audio_data = np.frombuffer(data, dtype = np.int16).astype(np.float32)

            # Perform audio transcription
            model = WhisperModel(model_size_or_path="large-v3", device="cuda", compute_type="int8_float16") 
            result = model.transcribe(audio_data)

            # Send back the result of the transcription to the frontend
            await websocket.send_data(result["text"])
    except WebSocketDisconnect:
        print("server disconnected")


@app.get("/speechRecognition")
async def generateText():
    pass

@app.post("postSpeech")
async def downloadSpeechText():
    pass

@app.post("postText")
async def downloadText():
    pass

@app.get("/response")
async def generateTextResponse():
    pass

# Some way to control facial animation on the right of the screen