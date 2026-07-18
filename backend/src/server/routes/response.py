from fastapi import APIRouter
import os
from fastapi.responses import StreamingResponse
from server.services.nlpServices import get_answer_router, get_answer_router_stream
from server.models.pydantic import LLMInput, ResponseModel
from server.services.fileServices import save

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))     

# Templates
template_path1 = os.path.join(BASE_DIR, "../../../data/templates/interview1.md")      # Bot : interviewer
with open(template_path1, "r") as f:
    prompt1 = f.read()

template_path2= os.path.join(BASE_DIR, "../../../data/templates/interview2.md")       # Bot : interviewee
with open(template_path2, "r") as f:
    prompt2 = f.read()
    
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
    save(response, "../../../data/raw/response-%s.txt")

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
    try:
        return StreamingResponse(
            get_answer_router_stream(
                input = [m.model_dump() for m in user_input.input],
                instructions = prompt1 if user_input.interview_type == 1 else prompt2,
                emotion = user_input.emotion,
                model = user_input.model
            ), 
            headers = headers
        )
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during response generation : {e}"
        }
 
    