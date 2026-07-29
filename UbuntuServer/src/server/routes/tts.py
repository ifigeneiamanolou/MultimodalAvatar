from fastapi import APIRouter
from fastapi.responses import Response
from server.models.pydantic import TTSInput
from server.services.ttsServices import controller

router = APIRouter()

@router.post("/orpheus")
async def generate_speech(input : TTSInput):
    # Generate speech and send streaming audio chunks to backend
    return Response(controller.generate_audio_stream(input.sentence, input.voice, input.model), mimetype='audio/wav')
