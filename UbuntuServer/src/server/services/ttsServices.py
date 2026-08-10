import os
import torch
from dotenv import load_dotenv
from server.services.engine_class import OrpheusModel
import logging
from vllm import AsyncLLMEngine, AsyncEngineArgs
import asyncio
import time
import os
import wave
from server.services.fileServices import next_path

# Configure logging
logger = logging.getLogger(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"
load_dotenv()
HF_TOKEN = os.environ["HF_TOKEN"]

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
DATA_PATH = os.path.join(BASE_DIR, "../../../data/raw/output-%s.wav")

class ttsController:
    """ Controls interaction with Orpheus3B allowing model loading, cache clean-up and inference
    """
    def __init__(self):
        self._models = {}               # in case multiple models are used                  

    async def stop(self):
        """ Perform cleanup by emptying the cached Orpheus3B models
        """
        # Empty cached models
        self._models = {}

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
        async for chunk in self.generate_audio_stream(warmup, "zoe", model_name):
           pass

    async def generate_audio_stream(self, sentence : str, voice : str, model : str):
        """ Perform Orpheus3B inference and return the result as a streaming response

        Args:
            sentence (str): the sentence for which we want to perform TTS
            voice (str): the voice used in Orpheus3B
            model (str): the model used from the variants of Orpheus3B

        Yields:
            bytes : audio chunks generated
        """
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

        # sample rate => 24000
        # bits per sample => 16
        # mono channel
        # byte rate => 48000
        first = True
        try:
            with wave.open(DATA_PATH, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                for i, chunk in enumerate(syn_tokens):
                    # Time logging
                    if(i % 10 == 0):
                        logger.info(msg = f"Token {i} : {len(chunk)} bytes in {time.perf_counter() - start} seconds")
                    if first:
                        first = False
                        logger.info(msg = f"TTFT for {sentence} is {time.perf_counter() - start}")

                    # Local audio logging
                    wf.writeframes(chunk)

                    # Return to the central backend server
                    yield chunk
                logger.info(msg = f"Time for sentence {sentence} : {time.perf_counter() - start}")
        except Exception:
            logger.exception("Generation failed")

controller = ttsController()


