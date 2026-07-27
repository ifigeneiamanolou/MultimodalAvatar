from fastapi import HTTPException
import os
import torch
from dotenv import load_dotenv
from orpheus_tts import OrpheusModel
from fastapi import WebSocketDisconnect
import websockets
import logging
from vllm import AsyncLLMEngine, AsyncEngineArgs
import asyncio
import Queue


# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

_models = {}
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(msg = f"Using device {device}")
load_dotenv()
HF_TOKEN = os.environ["HF_TOKEN"]

def custom_setup_engine(self):
    engine_args = AsyncEngineArgs(
        model=self.model_name,
        dtype=self.dtype,
        max_model_len=2048,
    )
    return AsyncLLMEngine.from_engine_args(engine_args)

def load_model(model_name : str):
    """ Load Orpheus3B model into the models dictionary if not loaded before

    Args:
        model_id (str): the ID of the model to load
        language (str) : the language of the model
    """
    # Resolve issue with key max_model_len not found
    OrpheusModel._setup_engine = custom_setup_engine

    try:
        if model_name not in _models.keys():
            _models[model_name] = OrpheusModel(model_name = model_name)
    except Exception as e:
        logger.exception(msg = f"Error during orpheus 3b loading : {e}")

async def generate_audio(sentence : str, model_name : str, voice : str):
    """ Generate audio tokens from input sentence and stream it to Audio2Face through Audio2Face

    Args:
        sentence (str): the sentence we need to produce audio from
        model_name (str) : the name of the model to load
        voice (str) : the voice used to produce audio via Orpheus3B
    """
    
    if model_name not in _models.keys():
	logger.info(f"model name not in dictionary)
	return
        
    model = _models[model_name]
    q : Queue = Queue()
    SENTINEL = -1

    def produce():
        try:
            syn_tokens = model.generate_speech(
                prompt = sentence,
                voice = voice
            )

            for chunk in syn_tokens:
                q.put(chunk)
	    q.put(-1)
        except WebSocketDisconnect:
            logger.info(msg = "Disconnected with UE5 server")
        except Exception as e:
            logger.error(msg = f"Error during speech generation from orpheus : {str(e)}")

    running_loop = asyncio.get_event_loop()
    running_loop.run_in_executor(None, produce)
    
    while(True):
	chunk = await running_loop.run_in_executor(None, q.get())
	if chunk is None:
	    break
	yield chunk
