from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from src.AvatarProject.models.pydantic import UserInput, ResponseModel
from src.AvatarProject.services.animations import generateAnimations
from src.AvatarProject.services.fileServices import next_path, save_audio
from src.AvatarProject.models.ConnectionManager import ConnectionManager
import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import base64
from orpheus_cpp import OrpheusCpp
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
load_dotenv()
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
tts = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)
orpheus = OrpheusCpp(verbose = False, lang = "en")
managerOrpheus = ConnectionManager()           

router = APIRouter()

@router.post("/tts")
async def generateAudio(user_input : UserInput) -> ResponseModel:
    """ Generates and uploads artkit coefficients using ElevenLabs

    Args:
        user_input (UserInput): Contains the text and the type of the interview

    Returns:
        ResponseModel: Pydantic model containing fields meta, success, data and message
    """

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
    audio_chunks = b"".join(chunk for chunk in audio if chunk)
    save_audio(audio_chunks, "../data/processed/tts-%s.mp3")
    
    return {
        "success" : True,
        "data" : {
            "blendshape_path" : path, 
            "audio" : base64.b64encode(audio_chunks).decode("utf-8")},      # Audio after TTS
        "message" : "Audio and ArtKit coefficients generated successfully"
    }


@router.websocket("/ttsOrpheus")
async def generateAudio(websocket : WebSocket):
    """ Generates and uploads artkit coefficients using Orpheus3B to adress data proprietry issues in a continuous manner

    Args:
        websocket (WebSocket): incomming web socket connection
    """

    await managerOrpheus.connect(websocket)

    try:    
        while True:
            # Receive data from the client
            data = await websocket.receive_text()  

            # Generate blendshapes
            artkit = await generateAnimations(data)
            path = next_path(os.path.join(BASE_DIR, "../../data/processed/blendshape-%s.csv"))
            artkit.to_csv(path, header = False)

            # Text to Speech
            buffer = []
            for i, (_, chunk) in enumerate(orpheus.stream_tts_sync(data, options={"voice_id": "tara"})):
                buffer.append(chunk)
                await managerOrpheus.send_personal(websocket, chunk)

            # Audio upload in a wav file
            buffer = np.concatenate(buffer, axis=1)
            save_audio(buffer, "../data/processed/tts-%s.wav")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error when performing text transcription : {e}")
    finally:
        await managerOrpheus.disconnect(websocket)


