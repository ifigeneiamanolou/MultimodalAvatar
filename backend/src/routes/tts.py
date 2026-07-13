from fastapi import APIRouter
from typer import prompt
from src.models.pydantic import TTSInput, ResponseModel
from src.services.animations import generateAnimations, textToSpeechStreaming
from src.services.fileServices import next_path, save_audio
from src.models.ConnectionManager import ConnectionManager
import os
from elevenlabs.client import ElevenLabs
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import base64
from orpheus_cpp import OrpheusCpp
import numpy as np
import wave
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
load_dotenv()
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
tts = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)
# orpheus = OrpheusCpp(verbose = False, lang = "en")
managerTTS = ConnectionManager()           

router = APIRouter()

@router.post("/tts", response_model = ResponseModel)
async def generateAudio(input : TTSInput):
    """ Transcribes the input audio using ElevenLabs and generates artkit coefficients as a less
    ressource intensive alternative to using Audio2Face through AWS

    Args:
        user_input (UserInput): Contains the text and the type of the interview

    Returns:
        ResponseModel: Pydantic model containing fields meta, success, data and message
    """

    text = input.text
    path = input.path if input.path else next_path(os.path.join(BASE_DIR, "../../data/processed/blendshape-%s.csv"))

    # ================= Blendshape generation ===============
    try:
        artkit = await generateAnimations(text)
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
    save_audio(audio_chunks, "../../data/processed/tts-%s.mp3")
    
    return {
        "success" : True,
        "data" : {
            "blendshape_path" : path, 
            "audio" : base64.b64encode(audio_chunks).decode("utf-8")},      # Audio after TTS
        "message" : "Audio and ArtKit coefficients generated successfully"
    }

@router.post("/tts/stream")
async def generateAudio(input : TTSInput):
    """ Transcribes the input audio using ElevenLabs and web sockets and generates artkit coefficients as a less
    ressource intensive alternative to using Audio2Face through AWS

    Args:
        input (TTSInput) : 
    """

    text = input.text
    path = input.path if input.path else next_path(os.path.join(BASE_DIR, "../../data/processed/blendshape-%s.csv"))
    
    # ================= Blendshape generation ===============
    try:
        artkit = await generateAnimations(text)
        artkit.to_csv(path, header = False)
    except Exception as e:
        return {
            "success" : False,
            "data" : "",
            "message" : f"Error during coefficient generation and upload : {e}"
        }
    # ================ TTS generation =================
    voice_id = "JBFqnCBsd6RMkjVDRZzb"  # "George"
    model_id = "eleven_flash_v2_5"
    return StreamingResponse(
        textToSpeechStreaming(text, voice_id, model_id),
        media_type='audio/mpeg'
    )

@router.post("/tts/Orpheus", response_model = ResponseModel)
async def generateAudio(input : TTSInput):
    text = input.text
    path = input.path if input.path else next_path(os.path.join(BASE_DIR, "../../data/processed/blendshape-%s.csv"))
    
    # ================= Blendshape generation ===============
    try:
        artkit = await generateAnimations(text)
        artkit.to_csv(path, header = False)
    except Exception as e:
        return {
            "success" : False,
            "data" : "",
            "message" : f"Error during coefficient generation and upload : {e}"
        }
    
    model = orpheus(model_name ="canopylabs/orpheus-tts-0.1-finetune-prod", max_model_len=2048)

    start_time = time.monotonic()
    syn_tokens = model.generate_speech(
        prompt=prompt,
        voice="tara",
    )

    with wave.open("output.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)

        total_frames = 0
        chunk_counter = 0
        for audio_chunk in syn_tokens: # output streaming
            chunk_counter += 1
            frame_count = len(audio_chunk) // (wf.getsampwidth() * wf.getnchannels())
            total_frames += frame_count
            wf.writeframes(audio_chunk)
        duration = total_frames / wf.getframerate()

        end_time = time.monotonic()
    print(f"It took {end_time - start_time} seconds to generate {duration:.2f} seconds of audio")