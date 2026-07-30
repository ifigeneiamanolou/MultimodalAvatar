from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes.feedbackNew import router as feedback
from server.routes.response import router as response
from server.utils.controller import controller
from server.services.nlpServices import get_answer_router_stream
from contextlib import asynccontextmanager
import logging
import os

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# Constant
WARMUP_SENTENCE = "This is a warmup sentence for the machine learning models"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))    
template_path1 = os.path.join(BASE_DIR, "../../../data/templates/interview1.md")      # Bot : interviewer
with open(template_path1, "r") as f:
    prompt = f.read()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Establish a web socket connection with the UE5 app
    await controller.start()

    # Open router warmup
    try:
        async for _ in get_answer_router_stream(
            input = [{"role": "user", "content": "Hello"}],
            instructions = prompt,
            emotion = "neutral",
            model = "openai/gpt-4o-mini" 
        ):
            pass
        logger.info("Open router warm up complete !")
    except Exception as e:
        logger.error(f"OpenRouter warm-up failed: {e}", exc_info=True)
    yield
    await controller.close()

app = FastAPI(lifespan = lifespan)
app.include_router(feedback)
app.include_router(response)

origins = ["http://localhost:8081"]             # Fronted expo server

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,          # Change in production    
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True      
)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "127.0.0.1", port = 8000, ws_ping_interval = 20, ws_ping_timeout = 60)