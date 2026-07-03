"""  
    Sample FastAPI endpoint to connect to SageMaker endpoints through AWS

"""

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from src.services.fileServices import save_audio, save
from src.models.pydantic import ResponseModel
import boto3
import json
import base64

router = APIRouter()
whisper_endpoint = "WRITE AN ENDPOINT HERE AFTER CREATING IN AWS SAGEMAKER"
align_endpoint = "WRITE AN ENDPOINT HERE AFTER CREATING IN AWS SAGEMAKER"

sagemaker_runtime = boto3.client("sagemaker-runtime")

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
        payload = json.dump({
            "audio" : base64.b64encode(audio_bytes).decode('utf-8'),
            "text" : text
        })
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName = align_endpoint,
            Body = payload
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = "Error when performing force alignment")

    # Decodes and returns the response body
    return response['Body'].read().decode('utf-8')

@router.post("/whisperAWS", response_model = ResponseModel)
async def transcribe(audio_bytes : bytes):
    """ Transcribes the input audio using Whisper AWS deployed model after saving the input audio. It also performs force aligment
    between the input audio and the transcribed text and saves the text into local storage (data folder) returning the transcripted
    text

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
            "data" : None
        }

    # Force align the text with the audio
    text = response['Body'].read().decode('utf-8')
    try:
        aligned_text = await align(audio_bytes, text)
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