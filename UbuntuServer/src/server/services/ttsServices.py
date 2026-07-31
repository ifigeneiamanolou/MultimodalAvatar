import os
import torch
from dotenv import load_dotenv
from server.services.engine_class import OrpheusModel
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

    async def stop(self):
        # Empty cached models
        self._models = {}
        # Empty the queue
        while not self.queue.empty():
            self.queue.get()

    async def start(self, model_name : str):
        """ Load Orpheus3B model into the models dictionary  if not loaded before
        
        Args:
            model_name (str): the ID of the model to load
        """
        # Resolve issue with key max_model_len not found
        # OrpheusModel._setup_engine = custom_setup_engine
        
        try:
            if model_name not in self._models.keys():
                self._models[model_name] = OrpheusModel(model_name=model_name)
        except Exception as e:
            logger.exception(msg=f"Error during orpheus 3b loading : {e}")
            raise
        
        # Warm up
        warmup = 'Hey there, looks like you forgot to provide a prompt! Please provide one that will help us generate speech'
        first = True       
        async for chunk in self.generate_audio_stream(warmup, "zoe", model_name):
           if first:           
               logger.info(f"length of audio chunk is {len(chunk)}")
               first = False

    async def generate_audio_stream(self, sentence : str, voice : str, model : str):
        if model not in self._models.keys():
            logger.info(f"model name not in dictionary")
            raise 
        start = time.perf_counter()
        syn_tokens = self._models[model].generate_speech(
            prompt=sentence,
            voice=voice,
            repetition_penalty=1.1,
            stop_token_ids=[128258],
            max_tokens=2000,
            temperature=0.4,
            top_p=0.9
        )
        
        logger.info(msg = f"generator created in  {time.perf_counter() - start}")

        # sample rate => 24000
        # bits per sample => 16
        # mono channel
        # byte rate => 48000
        first = True
        try:
            logger.info(f"starting chunk generation")
            for i, chunk in enumerate(syn_tokens):
                logger.info(msg = f"received token {i}")
                if first:
                    first = False
                    logger.info(msg = f"TTFT for {sentence} is {time.perf_counter() - start}")
                yield chunk
        except Exception:
            logger.exception("Generation failed")
        logger.info("done")

controller = ttsController()
