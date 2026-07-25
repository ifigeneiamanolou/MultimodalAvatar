from fastapi import APIRouter

from src.server.models.pydantic import BertInput, BertOutput
from src.server.services.bertServices import post_process, bert_inference, tokenize_input

router = APIRouter()

@router.post("/distilbert", response_model = BertOutput)
def predict(input : BertInput):
    # Convert input into tokens
    inputs = tokenize_input(input.sentence)

    # Perform inference
    predictions = bert_inference(inputs)

    # Post process outputs
    emotions, idx, maxProb, result = post_process(predictions)

    return {
        "text": input.sentence, 
        "emotion": emotions[idx],
        "maxProb" : maxProb,
        "predictions": result,
    }