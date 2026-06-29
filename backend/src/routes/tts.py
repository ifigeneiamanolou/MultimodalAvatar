from fastapi import APIRouter
from src.models.pydantic import UserInput, ResponseModel
from src.services.animations import generateAnimations
from src.services.fileServices import next_path, save_audio
import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
load_dotenv()
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
tts = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

router = APIRouter()

@router.post("/tts")
async def generateAudio(user_input : UserInput) -> ResponseModel:
    """ Generates and uploads artkit coefficients

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