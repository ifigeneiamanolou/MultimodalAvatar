from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from server.models.pydantic import TTSInput
from server.services.ttsServices import controller

router = APIRouter()

@router.post("/orpheus", response_class = StreamingResponse)
async def generate_speech(input : TTSInput):
    # Generate speech and send streaming audio chunks to backend
    return StreamingResponse(controller.generate_audio_stream(input.sentence, input.voice, input.model))
