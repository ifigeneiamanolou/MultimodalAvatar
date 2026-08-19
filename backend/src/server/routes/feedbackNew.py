from fastapi import APIRouter
from server.models.pydantic import ResponseModel, UserInput
from server.services.fileServices import save, saveJSON, load_template
from server.services.nlpServices import get_answer_router

router = APIRouter()

feedback_prompt1 = load_template("feedback1")
feedback_prompt2 = load_template("feedback2")

@router.post("/reset", response_model = ResponseModel)
async def resetConversation(user_input : UserInput):
    """ Saves the whole conversation in local storage

    Args:
        messages (Messages): incoming current conversation

    Returns:
        ResponseModel: Pydantic model with information on the completion of the upload
    """
    try:
        input_list = [m.model_dump() for m in user_input.input]
        saveJSON(input_list, "../../../data/feedback/conversation-%s.json")
    except Exception as e:
        return{
            "success" : False, 
            "data" : "",
            "message" : f"Error when uploading conversation : {e}"
        }
    
    return{
        "success" : True,
        "data" : "",
        "message" : "Successful reset and upload of conversation"
    }

@router.post("/feedback", response_model = ResponseModel)
async def generateFeedback(user_input : UserInput):    
    """ Generate an NLP response as feedback to the user after the interview and send it back to the frontend
    
    Args:
        messages (Messages): incoming current conversation

    Returns:
        ResponseModel: Pydantic model with information on the completion of the upload and the feedback response
    
    """   
    input_list = [m.model_dump() for m in user_input.input]
    saveJSON(input_list, "../../../data/feedback/conversation-%s.json")
    
    # Retrieve file name to save the response and instructions depending on the user role
    feedback_prompt = feedback_prompt1 if user_input.interview_type == 1 else feedback_prompt2

    # Generate feedback using OpenAI Router
    try:
        response = get_answer_router(
            input = input_list,
            instructions = feedback_prompt
        )
    except Exception as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during feedback generation : {e}"
        }

    # Save the response to a file  
    save(response, "../../../processed/feedback-%s.txt")

    # Return the response to the frontend server to be displayed to the feedback box
    return {
        "success" : True,
        "data" : response, 
        "message" : "Successful answer generation"
    }

@router.post("/feedback/database")
async def save_feedback():
    pass
    




