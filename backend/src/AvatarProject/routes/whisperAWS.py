from backend.src.AvatarProject.models.textSpeech import sagemaker_runtime
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from src.AvatarProject.services.fileServices import save_audio, save
from src.AvatarProject.models.pydantic import ResponseModel

router = APIRouter()
whisper_endpoint = "WRITE AN ENDPOINT HERE AFTER CREATING IN AWS SAGEMAKER"
whisperx_endpoint = "WRITE AN ENDPOINT HERE AFTER CREATING IN AWS SAGEMAKER"

async def align(audio_bytes : bytes, text : str) -> str:
    """ Returns the aligned text using the original audio through WhisperX

    Args:
        audio_bytes (bytes): original input audio
        text (str): text transcription through Whisper

    Returns:
        str: forced aligned text
    """

    # Gets inference from the model hosted at the specified endpoint:
    try:
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName = whisperx_endpoint,
            Body = bytes({"audio": {audio_bytes}, "text" : {text}}, 'utf-8')
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = "Error when performing force alignment")

    # Decodes and returns the response body
    return response['Body'].read().decode('utf-8')

@router.post("/whisperAWS")
async def transcribe(audio_bytes : bytes) -> ResponseModel:
    """ Transcribes the input audio using Whisper AWS deployed model after saving the input audio. It also performs force aligment
    between the input audio and the transcribed text and saves the text into local storage (data folder)

    Args:
        audio_bytes (bytes): input audio bytes to transcribe detected through MediaRecorder API

    Returns:
        ResponseModel: standard response pydantic model with success, data, message and meta fields
    """

    # Save the audio response
    save_audio(audio_bytes, "../data/raw/audio-%s.mp3")

    # Gets Whisper inference from the model hosted at the specified endpoint
    try:
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName = whisper_endpoint,
            Body = audio_bytes
        )
    except Exception as e:
        return {
            "success" : False, 
            "message" : "Failed to perform Whisper audio transcription",
            "data" : audio_bytes
        }

    # Force align the text with the audio
    text = response['Body'].read().decode('utf-8')
    try:
        aligned_text = align(audio_bytes, text)
    except Exception as e:
        return{
            "success" : False, 
            "message" : "Failed to perform Whisper audio transcription",
            "data" : audio_bytes
        }

    # Save the aligned text
    save(aligned_text, "../data/processed/transcription-%s.txt")

    # Return the original text
    return{
        "success" : True, 
        "message" : "Successful transcription and force alignment",
        "data" : aligned_text
    }