from fastapi import APIRouter
from server.services.kokoroServices import transcribe
from server.models.pydantic import TTSInput
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/kokoro")
async def textToSpeech(input : TTSInput):
    headers = {
        "Content-Type": "text/event-stream",
        "cache-control": "no-cache",
        "Connection": "keep-alive"
    }
    
    return StreamingResponse(
        transcribe(
            text = input.text,
            language_code = input.language_code,
            voice = input.voice
        ),
        media_type = "text/event-stream",
        headers = headers
    )