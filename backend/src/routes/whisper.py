from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import whisperx
from src.models.textSpeech import modelAlign, metadata
from src.models.ConnectionManager import ConnectionManager
from src.service.fileServices import save, save_audio
from whisper import WhisperModel
from src.services.fileServices import next_path
import os
from dotenv import load_dotenv

device = "cpu"
compute_type = "int8"
manager = ConnectionManager()
model = WhisperModel(model_size_or_path = "small", device = device, compute_type = compute_type, batch_size = 4)  
model_align, metadata = whisperx.load_align_model(language_code = "en", device = device)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
load_dotenv()  
HF_TOKEN = os.environ["HF_TOKEN"]       

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
            path = next_path(os.path.join(BASE_DIR, "../data/raw/audio-%s.mp3")) 
            save_audio(data, "../data/raw/audio-%s.mp3")

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

                # Perform force alignment
                result = whisperx.align(segments, model_align, metadata, data, device, return_char_alignments = False)
                segments = result["segments"]
                aligned_text = " ".join([segment.text for segment in segments])

                # Save the transcription result
                save(aligned_text, "../data/processed/transcription-%s.txt")

                # Send back the result of the transcription to the frontend
                await manager.send_personal(websocket, aligned_text)
            except Exception as e:
                await manager.send_personal(websocket, f"Error {e}")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error when performing speech recognition : {e}")
    finally:
        await manager.disconnect(websocket)