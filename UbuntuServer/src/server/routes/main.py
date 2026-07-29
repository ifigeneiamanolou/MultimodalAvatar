from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes.tts import router as tts
from contextlib import asynccontextmanager
from server.services.ttsServices import controller

@asynccontextmanager
async def lifespan(app: FastAPI):
    await controller.start("canopylabs/orpheus-tts-0.1-finetune-prod")
    yield

app = FastAPI(lifespan = lifespan)
app.include_router(tts)

origins = [
           "http://109.242.88.228:8000"        # Backend uvicorn server
          ]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,                     
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True      
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8000, ws_ping_interval = 20, ws_ping_timeout = 60)   
    # Accessible by remote hosts (avoid 127.0.0.1)
