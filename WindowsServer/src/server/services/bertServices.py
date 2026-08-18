from transformers import DistilBertForSequenceClassification, DistilBertTokenizer, AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import os
import time
import logging

_models = {}

# Emotions produced by Distilbert
emotions = [
        "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion", "curiosity",
        "desire", "disappointment", "disapproval", "embarrassment", "excitement", "fear", "gratitude", "grief",
        "joy", "love", "nervousness", "optimism", "pride", "realization", "relief", "remorse", "sadness",
        "surprise", "neutral"
]

# Mapping of distilbert to audio2face emotions
# this implementation ignores out of breath, pain and cheekiness   
_SOURCE_LABEL_FOR_SLOT = [
    "amusement",     # amazement
    "anger",         # anger
    None,            # cheekiness
    "remorse",       # disgust
    "fear",          # fear
    "grief",         # grief
    "joy",           # joy
    None,            # out of breath
    None,            # pain
    "sadness",       # sadness
    "neutral",       # neutral
]

_A2F_EMOTIONS = ['amazement', 'anger', 'cheekiness', 'disgust', 'fear', 'grief', 'joy', 'out of breath', 'pain', 'sadness', 'neutral'] 

# Configure logging
logger = logging.getLogger(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
 
#################################################################
# Custom finetuned implementation
#################################################################

def tokenize_input(sentence : str):
    """ Perform tokenization of a sentence using a pretrained HF model

    Args:
        sentence (str): the sentence to tokenize

    Returns:
        dict: dictionary with the results of tokenization
    """
    tokenizer = DistilBertTokenizer.from_pretrained(os.path.join(BASE_DIR, "../../../data/fine_tuned_model"))
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=512)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    return inputs

def bert_inference(inputs : dict):
    """ Inference using a custom fine-tuned (locally) distilbert model

    Args:
        inputs (dict): tokenized input sentence

    Returns:
        np.ndarray: array with the output scores
    """
    model = DistilBertForSequenceClassification.from_pretrained(os.path.join(BASE_DIR, "../../../data/fine_tuned_model"))
    outputs = model(**inputs)
    predictions = outputs.logits
    return predictions

def post_process(predictions : list):
    """ Post processing of output scores using the softmax function. It wraps the results in a dictionary with
    keys the A2F emotions and detects the emotion label with the maximum score

    Args:
        predictions (list): list of raw emotion scores

    Returns:
        list, int, double, dict: list of A2F emotions, index of max emotion score, maximum score and dictionary of
        scores and corresponding emotion labels
    """
    start = time.perf_counter()
    probs = F.softmax(predictions, dim = -1)
    emotions = ['amazement', 'anger', 'cheekiness', 'disgust', 'fear', 'grief', 'joy', 'out of breath', 'pain', 'sadness', 'neutral']
    result = {label: p.item() for label, p in zip(_A2F_EMOTIONS, probs)}
    idx = torch.argmax(predictions, dim = -1).item()
    maxProb = predictions[idx].item()
    end = time.perf_counter()
    logger.info(f"time for distilbert post processing : {end - start} seconds")
    return emotions, idx, maxProb, result

#################################################################
# Implementation from hugging face
#################################################################
def load():
    if "tokenizer" not in _models.keys():
        _models["tokenizer"] = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    if "model" not in _models.keys():
        _models["model"] = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")
             
def bert_ready_inference(text : str):
    """ Perform bert inference using a HF model

    Args:
        text (str): input to distilbert

    Returns:
        probs: list of probability scores
    """
    logger.info(f"passing sentence {text} through distilbert")
    start = time.perf_counter()

    tokenizer = _models["tokenizer"]
    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():    # No gradient calculation
        model = _models["model"]
        logits = model(**inputs).logits
        probs = torch.sigmoid(logits)[0]

    end = time.perf_counter()
    logger.info(f"time for distilbert inference : {end - start} seconds")
    return probs

def map(probs : list):
    """ Maps probabilities from HF distilbert to custom ones suitable to the emotion labels used by A2F

    Args:
        probs (list): probability scores

    Returns:
        list: new probability scores after mapping
    """
    start = time.perf_counter()
    out = torch.zeros(len(_A2F_EMOTIONS), dtype = probs.dtype)
    for slot, label in enumerate(_SOURCE_LABEL_FOR_SLOT):
        if label is not None:
            out[slot] = probs[emotions.index(label)]
    end = time.perf_counter()
    logger.info(f"time for distilbert mapping : {end - start} seconds")
    return out 
        