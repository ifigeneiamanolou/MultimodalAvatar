from fastapi import APIRouter
from server.models.pydantic import TTSInput
from server.services.ttsServices import load_model, generate_audio

router = APIRouter()

@router.post("/orpheus")
async def generate_speech(input : TTSInput):
    # Load the model
    try:
        load_model(input.model)
    except RuntimeError as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during model loading : {e}"
        }

    # Generate speech and send to Audio2Face
    try:
        await generate_audio(sentence = input.sentence, model_name = input.model, voice = input.voice)
    except RuntimeError as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during speech generation and websocket upload : {e}"
        }
