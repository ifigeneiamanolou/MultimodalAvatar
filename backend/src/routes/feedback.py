from fastapi import APIRouter
from src.models.pydantic import Messages, ResponseModel
from src.services.fileServices import save, saveFeedback
import os
import json
from src.services.nlp import get_answer

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

feedback_path1 = os.path.join(BASE_DIR, "../../data/templates/feedback1.md")         # Bot : interviewer
with open(feedback_path1, "r") as f:
    feedback_prompt1 = f.read()

feedback_path2 = os.path.join(BASE_DIR, "../../data/templates/feedback2.md")         # Bot : interviewee
with open(feedback_path2, "r") as f:
    feedback_prompt2 = f.read()

@router.post("/reset", response_model = ResponseModel)
async def resetConversation(messages : Messages):
    """ Saves the whole conversation in local storage

    Args:
        messages (Messages): incoming current conversation

    Returns:
        ResponseModel: Pydantic model with information on the completion of the upload
    """

    saveFeedback(messages.model_dump(), "../../data/feedback/conversation-%s.json")
    return{
        "success" : True,
        "data" : "",
        "message" : "Successful reset and upload of conversation"
    }

@router.post("/feedback", response_model = ResponseModel)
async def generateFeedback(messages : Messages):    
    """ Generate an NLP response as feedback to the user after the interview and send it back to the frontend
    
    Args:
        messages (Messages): incoming current conversation

    Returns:
        ResponseModel: Pydantic model with information on the completion of the upload and the feedback response
    
    """   
    saveFeedback(messages.model_dump(), "../../data/feedback/conversation-%s.json")
    
    # Retrieve file name to save the response and instructions depending on the user role
    feedback_prompt = feedback_prompt1 if messages.interviewer == "interviewer" else feedback_prompt2

    # Generate feedback using OpenAI
    try:
        response = get_answer(
            input = json.dumps(messages.data),
            instructions = feedback_prompt
        )
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during feedback generation : {e}"
        }

    # Save the response to a file  
    save(response, "../../feedback/feedback-%s.txt")

    # Return the response to the frontend server to be displayed to the feedback box
    return {
        "success" : True,
        "data" : response, 
        "message" : "Successful answer generation"
    }