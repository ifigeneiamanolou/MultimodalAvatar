from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from server.services.nlpServices import get_answer_router, get_answer_router_stream, get_answer_router_stream_mobile
from server.models.pydantic import LLMInput, ResponseModel
from server.services.fileServices import save, load_template
from server.utils.controller import controller as syncCoordinator

router = APIRouter()     

# Templates
prompt1 = load_template("interview1")
prompt2 = load_template("interview2")
    
@router.post("/response", response_model = ResponseModel)
async def generateTextResponse(user_input : LLMInput):
    """ Generates and saves the response to the input text using an LLM
    Args:
        user_input (LLMInput): Contains the user text query and the type of the interviewee

    Returns:
        ResponseModel: Pydantic model with fields success, meta, data and message
    """

    # Generate response from OpenAI
    try:
        response = get_answer_router(
            input = [m.model_dump() for m in user_input.input],
            instructions = prompt1 if user_input.interview_type == 1 else prompt2,
            emotion = user_input.emotion,
            model = user_input.model
        )
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during response generation : {e}"
        }
    
    # Save the response to a file                              
    save(response)

    # Return the response to the frontend server
    return {
        "success" : True,
        "data" : response, 
        "message" : "Successful answer generation"
    }

@router.post("/response/stream")
async def generateTextResponse(user_input :LLMInput):
    """ Generates a response from the LLM and streams it in a continuous manner
    Args:
        user_input (LLMInput): Contains the user text query and the type of the interviewee
    """
    headers = {
        "Content-Type": "text/event-stream",
        "cache-control": "no-cache",
        "Connection": "keep-alive"
    }

    # Generate response from OpenAI
    return StreamingResponse(
        get_answer_router_stream(
            input = [m.model_dump() for m in user_input.input],
            instructions = prompt1 if user_input.interview_type == 1 else prompt2,
            emotion = user_input.emotion,
            model = user_input.model,
        ), 
        media_type = "text/event-stream",
        headers = headers
    )

@router.post("/response/stream/mobile")
async def generateTextResponse(user_input :LLMInput):
    """ Generates a response from the LLM, streams it to Orpheus and returns it at once to the frontend
    Args:
        user_input (LLMInput): Contains the user text query and the type of the interviewee
    """
    # Generate response from OpenAI
    result = await get_answer_router_stream_mobile(
        input = [m.model_dump() for m in user_input.input],
        instructions = prompt1 if user_input.interview_type == 1 else prompt2,
        emotion = user_input.emotion,
        model = user_input.model,
    )
    return result

@router.post("/reset/queue")
async def reset_queue():
    syncCoordinator.restart()