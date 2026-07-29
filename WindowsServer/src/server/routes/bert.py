from fastapi import APIRouter

from server.models.pydantic import BertInput, BertOutput
from server.services.bertServices import post_process, bert_inference, tokenize_input, load, bert_ready_inference, map
router = APIRouter()

# this is the endpoint for custom finutuned distilbert model
@router.post("/distilbert/finetuned", response_model = BertOutput)
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
    
# this is the endpoint for the distilbert model fetched from Hugging Face
@router.post("/distilbert", response_model = BertOutput)
def predict(input : BertInput):
    # Load the model and the tokenizer
    load()

    # Perform inference
    dictionary = bert_ready_inference(input.sentence)

    # Post process outputs
    predictions = map(dictionary)
    emotions, idx, maxProb, result = post_process(predictions)

    return {
        "text": input.sentence, 
        "emotion": emotions[idx],
        "maxProb" : maxProb,
        "predictions": result,
    }