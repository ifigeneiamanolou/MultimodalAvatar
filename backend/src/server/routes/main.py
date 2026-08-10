from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes.feedbackNew import router as feedback
from server.routes.response import router as response
from server.services.fileServices import next_path
from server.utils.controller import controller
from contextlib import asynccontextmanager
import logging
import os
import httpx
from dotenv import load_dotenv

# Configure basic logging
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.abspath(
    os.path.join(BASE_DIR, next_path("../../../data/processed/logRuntime-%s.log"))
)

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=LOG_PATH,
    force=True
)
logger = logging.getLogger(__name__)

# Environment variables
load_dotenv()
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

# Constant
WARMUP_SENTENCE = "This is a warmup sentence for the machine learning models"

# Prompt file
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
        async with httpx.AsyncClient() as client:
            await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                json={"model": "openai/gpt-5-nano", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5}
            )
        logger.info("OpenRouter warm-up complete")
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