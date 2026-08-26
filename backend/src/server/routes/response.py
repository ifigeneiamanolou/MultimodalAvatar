from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from server.services.nlpServices import audio_mobile, text_mobile, text_web, audio_web
from server.models.pydantic import LLMInput, LLMAudioInput
from server.services.fileServices import load_template
from server.utils.controller import controller as syncCoordinator

router = APIRouter()     

# Templates
prompt1 = load_template("interview1")
prompt2 = load_template("interview2")

@router.post("/response")
async def generateTextResponse(user_input : LLMInput):
    headers = {
        "Content-Type": "text/event-stream",
        "cache-control": "no-cache",
        "Connection": "keep-alive"
    }

    # Generate response from OpenAI
    return StreamingResponse(
        text_web(
            input = user_input.input,
            instructions = prompt1 if user_input.interview_type == 1 else prompt2,
            model = user_input.model
        ),
        media_type = "text/event-stream",
        headers = headers
    )

@router.post("/response/audio")
async def generateresponse(user_input : LLMAudioInput):
    headers = {
        "Content-Type": "text/event-stream",
        "cache-control": "no-cache",
        "Connection": "keep-alive"
    }

    # Generate response from OpenAI
    return StreamingResponse(
        audio_web(
            input = user_input.messages,
            instructions = prompt1 if user_input.interview_type == 1 else prompt2,
            model = user_input.model,
            audio = user_input.input
        ),
        media_type = "text/event-stream",
        headers = headers
    )

@router.post("/response/audio/mobile")
async def generateResponse(user_input : LLMAudioInput):
    response = await audio_mobile(
        input = [m.model_dump() for m in user_input.model],
        instructions = prompt1 if user_input.interview_type == 1 else prompt2,
        model = user_input.model,
        audio = user_input.input
    )

    return response

@router.post("/response/mobile")
async def generateTextResponse(user_input : LLMInput):
    # Generate response from OpenAI
    result = await text_mobile(
        input = [m.model_dump() for m in user_input.model],
        instructions = prompt1 if user_input.interview_type == 1 else prompt2,
        model = user_input.model
    )
    return result

@router.post("/reset/queue")
async def reset_queue():
    await syncCoordinator.restart()