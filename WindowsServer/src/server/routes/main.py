from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes.whisper import router as whisper
from server.routes.emotion import router as emotion
from server.routes.bert import router as bert
from contextlib import asynccontextmanager
import logging
from server.services.emotionsServices import load_model as load_emotion2vec
from server.services.emotionsServices import emotion_detection
from server.services.whisperServices import load_model as load_whisper
from server.services.whisperServices import transcription
from server.services.bertServices import load as load_distilbert
from server.services.bertServices import bert_ready_inference
from server.services.fileServices import read_audio, start_logging
import torch

# Configure basic logging
start_logging()
logger = logging.getLogger(__name__)

# Device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Constant
WARMUP_SENTENCE = "This is a warmup sentence for the machine learning models"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure cuda is available
    logger.info(f"Device used is {device}")
    
    # Load emotion2vec, distilert and whisper
    load_emotion2vec("iic/emotion2vec_plus_seed") 
    load_whisper("tiny")
    load_distilbert()

    # Warm up the ML models
    bert_ready_inference(WARMUP_SENTENCE)
    waveform, sr = read_audio("../../../data/raw/Warmup.m4a")
    logger.info(f"Sample rate for current audio file is {sr}")
    emotion_detection(waveform, "en", "iic/emotion2vec_plus_seed")
    transcription("tiny", "../../../data/raw/Warmup.m4a")
    
    # Uncomment this only to test inference time
    logger.info(f"======== RUNNING TEST FOR INFERENCE TIMES =======")
    bert_ready_inference(WARMUP_SENTENCE)
    waveform, sr = read_audio("../../../data/raw/Warmup.m4a")
    emotion_detection(waveform, "en", "iic/emotion2vec_plus_seed")
    transcription("tiny", "../../../data/raw/Warmup.m4a")

    # Run the server
    yield

    # Server closing down
    logger.info("Windows Server shutting down ...")
    
app = FastAPI(lifespan=lifespan)
app.include_router(whisper)
app.include_router(emotion)
app.include_router(bert)


origins = [
            "http://188.73.239.65:8081",        # Frontend Expo server
            "http:// 188.73.239.65:8000"        # Backend Uvicorn server
          ]

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],                     
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True      
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8000, ws_ping_interval = 20, ws_ping_timeout = 60)   
    # Without host 0.0.0.0 it won't listen to all network interfaces, only localhost