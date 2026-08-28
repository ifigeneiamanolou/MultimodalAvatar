"""
    Endpoints for emotion detection through emotion2vec

"""

from fastapi import APIRouter
from server.models.pydantic import ResponseModel, EmotionInput
from server.services.emotionsServices import emotion_detection, processScores
import base64
from server.services.fileServices import save_emotion2vec, save_audio

router = APIRouter()

@router.post("/emotion2vec", response_model = ResponseModel)
async def detectAudioEmotion(input : EmotionInput):
    # Decode the base64 input audio
    decoded_data = base64.b64decode(input.audio, validate = True)
    
    # Save raw audio into a webm file  
    path = save_audio(decoded_data)  
    
    # Emotion detection
    try:
        scores = emotion_detection(path, input.language, input.model)
    except RuntimeError as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during emotion generation : {e}"
        }

    # Post processing
    try:
        emotion, scoresNew = processScores(scores)

    except (KeyError, TypeError, ValueError) as e:
        return{
            "success" : False,
            "data" : "",
            "message" : f"Error during post processing : {e}"
        }
    
    # Save the emotion scores and final prediction to a file
    save_emotion2vec(scoresNew, emotion)

    # Return the emotion detected
    return{
        "success" : True,
        "data" : emotion,
        "message" : "Emotion detection from input audio using Emotion2Vec"
    }