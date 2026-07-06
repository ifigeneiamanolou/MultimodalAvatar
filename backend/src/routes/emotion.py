"""
    Endpoints for emotion detection

"""

from fastapi import APIRouter
from src.models.pydantic import ResponseModel, EmotionInput
import os
from src.services.emotionsServices import load_model, emotion_detection, processScores
import base64
from src.services.fileServices import save

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   

@router.post("/emotion2vec", response_model = ResponseModel)
async def detectAudioEmotion(input : EmotionInput):
    """ Detect emotional state of user input audio through emotion2vec that classsifies input audio
    into the following categories: anger, disgust, fear, happiness, neutrality, sadness, surprise

    Args:
        input (EmotionInput) : pydantic model with the model id and the audio 

    Returns:
        ResponseModel : information about the success of the request and the emotion label
    """

    # Load the model
    load_model(input.model)
    
    # Emotion detection
    try:
        scores = emotion_detection(base64.b64decode(input.audio, ' /'), input.model)
    except RuntimeError as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during emotion generation : {e}"
        }

    # Post processing
    try:
        emotion = processScores(scores)

    except (KeyError, TypeError, ValueError) as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during post processing : {e}"
        }
    
    # Save the emotion to a file
    save(emotion, "../../data/processed/emotion-%s.txt")

    # Return the emotion detected
    return{
        "success" : True,
        "data" : emotion,
        "message" : "Emotion detection from input audio using Emotion2Vec"
    }