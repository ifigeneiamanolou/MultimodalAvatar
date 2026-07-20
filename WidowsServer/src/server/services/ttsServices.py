
import os
import torch
from dotenv import load_dotenv
# from orpheus_tts import OrpheusModel
import asyncio 
import websockets

_models = {}

device = "cuda" if torch.cuda.is_available() else "cpu"
load_dotenv()
HF_TOKEN = os.environ["HF_TOKEN"]

def load_model(model_name : str):
    """ Load Orpheus3B model into the models dictionary if not loaded before

    Args:
        model_id (str): the ID of the model to load
        language (str) : the language of the model
    """

    if id not in _models.keys():
        # _models[model_name] = OrpheusModel(
        #     model_name = model_name,
        #     max_model_len = 2048,
        # )
        pass

async def generate_audio(sentence : str, model_name : str, voice : str):
    """ Generate audio tokens from input sentence and stream it to Audio2Face through Audio2Face

    Args:
        sentence (str): the sentence we need to produce audio from
        model_name (str) : the name of the model to load
        voice (str) : the voice used to produce audio via Orpheus3B
    """
    print("/n/n Starting audio generation ... /n/n")

    model = _models(model_name)
    syn_tokens = model.generate_speech(
        prompt = sentence,
        voice = voice
    )

    for chunk in syn_tokens:
        print(f"Chunk generated: {chunk} \n")
        async with websockets.connect(f'ws://localhost:8765') as websocket:
            await websocket.send_data(chunk)