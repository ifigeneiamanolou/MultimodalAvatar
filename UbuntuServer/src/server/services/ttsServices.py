import os
import torch
from dotenv import load_dotenv
from orpheus_tts import OrpheusModel
import logging
from vllm import AsyncLLMEngine, AsyncEngineArgs
import asyncio
import time

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"
load_dotenv()
HF_TOKEN = os.environ["HF_TOKEN"]

class ttsController:
    def __init__(self):
        self.queue = asyncio.Queue(maxsize = 50)
        self._models = {}               # in case multiple models are used
        self.lock = asyncio.Lock()                  

    def custom_setup_engine(self):
        engine_args = AsyncEngineArgs(
            model=self.model_name,
            dtype=self.dtype,
            max_model_len=2048,
            gpu_memory_utilization=0.5,     # Enable Audio2Face to run along with Orpheus3B : default is 0.9
        )
        return AsyncLLMEngine.from_engine_args(engine_args)

    def start(self, model_name : str):
        """ Load Orpheus3B model into the models dictionary if not loaded before
        
        Args:
            model_name (str): the ID of the model to load
        """
        # Resolve issue with key max_model_len not found
        OrpheusModel._setup_engine = self.custom_setup_engine
        
        try:
            if model_name not in self._models.keys():
                self._models[model_name] = OrpheusModel(model_name=model_name)
        except Exception as e:
            logger.exception(msg=f"Error during orpheus 3b loading : {e}")
            raise

    def generate_audio_stream(self, sentence : str, voice : str, model : str):
        if model not in self._models.keys():
            logger.info(f"model name not in dictionary")
            raise 
        start = time.perf_counter()
        syn_tokens = self.model.generate_speech(
            prompt=sentence,
            voice="tara",
            repetition_penalty=1.1,
            stop_token_ids=[128258],
            max_tokens=2000,
            temperature=0.4,
            top_p=0.9
        )

        # sample rate => 24000
        # bits per sample => 16
        # mono channel
        # byte rate => 48000
        first = True
        for chunk in syn_tokens:
            if first:
                first = False
                logger.info(msg = f"TTFT for {sentence} is {time.perf_counter() - start}")
            yield chunk

controller = ttsController()