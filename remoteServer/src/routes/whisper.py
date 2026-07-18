""" 

    Implements a web socket connection that implements audio transcription through WhisperX along with force alignment
    when using a standard CPU to run the application (no AWS).

"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.ConnectionManager import ConnectionManager
from src.services.fileServices import save, save_audio
from src.services.whisperServices import transcription
import base64

# Websocket manager
manager = ConnectionManager() 

# FastAPI router
router = APIRouter()

# Perform automatic speech recognition using Whisper and generate a response from OpenAI
@router.websocket("/asr")
async def speechRecognition(websocket : WebSocket):
    await manager.connect(websocket)        # Connect the client to the websocket manager

    try:
        while True:
            # Receive data from the client 
            data = await websocket.receive_text()  

            # Handle keep-alive messages to prevent closure of the socket
            if data == 'keep-alive':
                continue
            
            # Decode the base64 input audio
            decoded_data = base64.b64decode(data, validate = True);

            # Save raw audio into a webm file  
            path = save_audio(decoded_data, "../../data/raw/audio-%s.webm")             # THE AUDIO IS NOT SAVED PROPERLY

            try:
                # Perform audio trancription
                text = transcription("small", path)
        
                # Save the transcription result
                save(text, "../../data/processed/transcription-%s.txt")

                # Send back the result of the transcription to the frontend
                await manager.send_personal(websocket, text)
            except Exception as e:
                await manager.send_personal(websocket, f"Error {e}")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await manager.send_personal(connection = websocket, data = f"Error {e}")
    finally:
        await manager.disconnect(websocket)
