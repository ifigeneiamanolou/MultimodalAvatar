from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Path
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

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

# Pydantic models
class UserInput(BaseModel):
    input : str
    session_id : str = "default"

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8081"],          # Change in production    
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
model = WhisperModel(model_size_or_path="small", device="cpu", compute_type="int8")        # Connect to strong GPU

# Finds the next available path using binary search
def next_path(path_pattern):
    i = 1
    while os.path.exists(path_pattern % i):
        i = i * 2
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) 
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

    return path_pattern % b

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
                    path,                  # Absolute path to webm file stored locally
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
        print(f"Error : {e}")
    finally:
        await manager.disconnect(websocket)

# Generate an NLP response given the file with the user input
@app.post("/response")
async def generateTextResponse(user_input : UserInput):
    # Retrieve file name to save the response
    path = next_path(os.path.join(BASE_DIR, "../data/raw/response-%s.txt"))

    # Generate response from OpenAI
    response = get_answer(user_input.input)

    # Save the response to a file                               
    with open(path, "w") as f:
        f.write(response)

    # Return the response to the frontend server
    return {"response" : response}

def get_answer(input):
    try:
        answer = client.chat.completions.create(
            model="gpt-4o-mini",                    # To change during production
            messages=[{"role": "user", "content": input}]
        )
        return answer.choices[0].message.content
    except RateLimitError as e:
        return "No API credit"
    except Exception as e:
        return f"Other Error: {e}"

@app.post("/tts")
async def generateAudio(user_input : UserInput):
    text = user_input.input

    audio = tts.text_to_speech.with_raw_response.convert(
        text = text,
        voice_id = "JBFqnCBsd6RMkjVDRZzb",  # "George" 
        model_id = "eleven_v3",             # To switch to v2.5-flash
        output_format = "mp3_44100_128",
        language_code = "en",
    )

    # Play the audio
    play(audio)

    # Save the audio
    path = next_path(os.path.join(BASE_DIR, "../data/processed/tts-%s.txt"))
    with open(path, "w") as f:
        f.write(audio.data)

# Some way to control facial animation on the right of the screen
@app.post("/avatar")
async def generateAnimations():
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "127.0.0.1", port = 8000, ws_ping_interval = 20, ws_ping_timeout = 60)