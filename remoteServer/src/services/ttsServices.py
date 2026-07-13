
import os
import torch
from dotenv import load_dotenv

_models = {}        # Avoid time consuming model reloading

device = "cuda" if torch.cuda.is_available() else "cpu"
load_dotenv()
HF_TOKEN = os.environ["HF_TOKEN"]

def load_model(model_id : str, language : str):
    """ Load model into the models dictionary if not loaded before

    Args:
        model_id (str): the ID of the model to load
        language (str) : the language of the model
    """

    if id not in _models.keys():
        pass