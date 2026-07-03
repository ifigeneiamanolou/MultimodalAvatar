""" 

    Implements a web socket connection that implements audio transcription through WhisperX along with force alignment
    when using a standard CPU to run the application (no AWS).

"""

import tempfile
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
            
            # Save raw audio into a temporary webm file  
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=True) as tmp:
                tmp.write(data)
                tmp.flush()
                audio = whisperx.load_audio(tmp.name)   

            try:
                # Perform audio transcription
                result = model.transcribe(
                    audio      ,            
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

                # Send back the result of the transcription to the frontend
                await manager.send_personal(websocket, aligned_text)
            except Exception as e:
                await manager.send_personal(websocket, f"Error {e}")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await manager.send_personal(f"Error {e}")
    finally:
        await manager.disconnect(websocket)