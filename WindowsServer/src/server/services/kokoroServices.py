from kokoro import KPipeline
import torch
from server.services.fileServices import save_tts_result
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"

def transcribe(text : str, language_code : str, voice : str):
    pipeline = KPipeline(lang_code = language_code)
    generator = pipeline(text, voice = voice, device = device)
    
    chunks = []
    start_time = time.perf_counter()
    logger.info(f"Passing [{text}] through kokoro")
    for i, (_, _, audio) in enumerate(generator):
        if i == 0:
            logger.info(f"TTFT for kokoro: {time.perf_counter() - start_time} sec")
        
        if i != 0 and i % 10 == 0:
            logger.info(f"Time for chunk {i} from kokoro: {time.perf_counter() - start_time} sec")
            
        chunks.append(audio)
        yield audio
    logger.info(f"Time for kokoro inference: {time.perf_counter() - start_time} sec")
    
    # Save the resulting audio
    save_tts_result(chunks)
    