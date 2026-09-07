from kokoro import KPipeline
import torch
from server.services.fileServices import save_tts_result
import logging
import time
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"

_models = {}

WARM_UP = "THIS IS A SENTENCE TO WARM UP THE MACHINE LEARNING MODEL"

def load_kokoro(codes : list, warm_voice : str = "af_bella"):
    for code in codes:
        if code not in _models.keys():
            _models[code] = KPipeline(
                lang_code = code,
                repo_id="hexgrad/Kokoro-82M"
            )
           
        start_time = time.perf_counter() 
        for index, _ in enumerate(_models[code](WARM_UP, voice = warm_voice)):
            if index == 0:
                logger.info(f"TTFT for kokoro: {time.perf_counter() - start_time} sec")
        logger.info(f"Time for kokoro inference: {time.perf_counter() - start_time} sec") 
            
def transcribe(text : str, language_code : str, voice : str):
    pipeline = _models[language_code]
    generator = pipeline(text, voice = voice)
    
    chunks = []
    start_time = time.perf_counter()
    logger.info(f"Passing [{text}] through kokoro")
    for i, (_, _, audio) in enumerate(generator):
        if i == 0:
            logger.info(f"TTFT for kokoro: {time.perf_counter() - start_time} sec")
        
        if i != 0 and i % 10 == 0:
            logger.info(f"Time for chunk {i} from kokoro: {time.perf_counter() - start_time} sec")
            
        chunks.append(audio)
        pcm = (audio.detach().cpu().numpy() * 32767).astype(np.int16)
        yield pcm.tobytes()
    logger.info(f"Time for kokoro inference: {time.perf_counter() - start_time} sec")
    
    # Save the resulting audio
    save_tts_result(chunks)
    