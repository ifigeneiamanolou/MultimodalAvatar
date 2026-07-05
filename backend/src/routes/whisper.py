""" 

    Implements a web socket connection that implements audio transcription through WhisperX along with force alignment
    when using a standard CPU to run the application (no AWS).

"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import whisperx
from src.models.ConnectionManager import ConnectionManager
from src.services.fileServices import save, save_audio
from src.services.fileServices import next_path
import os
from dotenv import load_dotenv

# Settings
device = "cpu"
compute_type = "int8"

# Websocket manager
manager = ConnectionManager()

# ffmpeg configuration
if os.name == "nt":
    os.add_dll_directory(r"C:/ffmpeg-n7.1-latest-win64-gpl-shared-7.1/bin")     # ADD YOUR FFMPEG HERE

# Whisper models
model = whisperx.load_model("tiny", device = device, compute_type = compute_type)
model_align, metadata = whisperx.load_align_model(language_code = "en", device = device)

# Directories 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   

# Environemt variables
load_dotenv()  
HF_TOKEN = os.environ["HF_TOKEN"]       

# FastAPI router
router = APIRouter()

@router.websocket("/asr")
async def speechRecognition(websocket : WebSocket):
    """ Handles incoming data to the websocket (audio input)

    Args:
        websocket (WebSocket): input web socket connection

    Raises:
        HTTPException: if the transcription or force alignment process fails
    """

    await manager.connect(websocket)        # Connect the client to the websocket manager

    try:
        while True:
            # Receive data from the client
            data = await websocket.receive_bytes()  
            
            # Save raw audio into a webm file  
            path = save_audio(data, "../../data/raw/audio-%s.webm")  
            audio = whisperx.load_audio(path)

            try:
                # Perform audio transcription
                result = model.transcribe(
                    audio,            
                    language = "en",
                    batch_size = 4,
                )
            
                # Perform force alignment
                aligned = whisperx.align(result["segments"], model_align, metadata, audio, device, return_char_alignments = False)
                aligned_text = " ".join(
                    segment["text"] for segment in aligned["segments"]
                )   
            
                # Save the transcription result
                save(aligned_text, "../../data/processed/transcription-%s.txt")

                # Send back the result of the transcription to the frontend to display
                await manager.send_personal(connection = websocket, data = aligned_text)
            except Exception as e:
                print(e)
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await manager.send_personal(connection = websocket, data = f"Error {e}")
    finally:
        await manager.disconnect(websocket)