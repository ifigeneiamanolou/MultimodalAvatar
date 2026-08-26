from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes.whisper import router as whisper
from contextlib import asynccontextmanager
import logging
from server.services.whisperServices import load_model as load_whisper
from server.services.whisperServices import transcription
from server.services.fileServices import read_audio, start_logging
import torch

# Configure basic logging
start_logging()
logger = logging.getLogger(__name__)

# Device
device = "cuda" if torch.cuda.is_available() else "cpu"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure cuda is available
    logger.info(f"Device used is {device}")
    
    # Load whisper
    load_whisper("tiny")

    # Warm up Whisper
    transcription("tiny", "../../../data/raw/Warmup.m4a")

    # Run the server
    yield

    # Server closing down
    logger.info("Windows Server shutting down ...")
    
app = FastAPI(lifespan=lifespan)
app.include_router(whisper)

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