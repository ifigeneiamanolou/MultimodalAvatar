from fastapi import APIRouter
import os
from backend.src.AvatarProject.services.nlp import get_answer
from backend.src.AvatarProject.models.pydantic import UserInput, ResponseModel
from backend.src.AvatarProject.services.fileServices import save

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))     

# Templates
template_path1 = os.path.join(BASE_DIR, "../../data/templates/interview1.md")      # Bot : interviewer
with open(template_path1, "r") as f:
    prompt1 = f.read()

template_path2= os.path.join(BASE_DIR, "../../data/templates/interview2.md")       # Bot : interviewee
with open(template_path2, "r") as f:
    prompt2 = f.read()
    
@router.post("/response")
async def generateTextResponse(user_input : UserInput) -> ResponseModel:
    """ Generates and saves the response to the input text using an LLM
    Args:
        user_input (UserInput): Contains the user text query and the type of the interviewee

    Returns:
        ResponseModel: Pydantic model with fields success, meta, data and message
    """

    # Generate response from OpenAI
    try:
        response = get_answer(
            input = user_input.input,
            instructions = prompt1 if user_input.interview_type == 1 else prompt2
        )
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during response generation : {e}"
        }
    
    # Save the response to a file                              
    save(response["text"], "../data/raw/response-%s.txt")

    # Return the response to the frontend server
    return {
        "success" : True,
        "data" : response, 
        "message" : "Successful answer generation"
    }