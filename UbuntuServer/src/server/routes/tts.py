from fastapi import APIRouter
from fastapi.responses import StreamingResponse
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

    # Generate speech and send audio chunks to backend
    return StreamingResponse(generate_audio(input.sentence, input.model, input.voice))
