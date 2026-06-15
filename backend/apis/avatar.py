from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from faster_whisper import WhisperModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8081"],           # In production, replace with specific origins
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True      
)

class ConnectionManager:        # Class containing the web socket connections
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
model = WhisperModel(model_size_or_path="large-v3", compute_type = "float32")        # Connect to strong GPU

# Perform automatic speech recognition using Whisper
@app.websocket("/asr")
async def speechRecognition(websocket : WebSocket):
    await manager.connect(websocket)        # Connect the client to the websocket manager

    try:
        while True:
            # Receive data from the client
            data = await websocket.receive_bytes()   
            await manager.send_personal(websocket, "Received input audio, processing ...")   

            # Convert from audio data to numpy integer array
            audio_data = np.frombuffer(data, dtype = np.int16).astype(np.float32);
            print("data on which to perform suscription", audio_data);

            # Perform audio transcription
            segments, info = model.transcribe(audio_data)
            text = " ".join([segment.text for segment in segments])

            # Send back the result of the transcription to the frontend
            await manager.send_personal(websocket, text)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        print("Client disconnected")
    except Exception as e:
        await manager.disconnect(websocket)
        print(f"Error {e}")

# Download speech data recorded in the backend
@app.post("/postSpeech")
async def downloadSpeechText():
    pass

# Download corresponding text recorded in the backend
@app.post("/postText")
async def downloadText():
    pass

# Generate an NLP response given a text or audio user input
@app.get("/response")
async def generateTextResponse():
    pass

# Some way to control facial animation on the right of the screen

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "127.0.0.1", port = 8000)       # Custom server configuration