from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.whisper import router as whisper
from src.routes.tts import router as tts
from src.routes.emotion import router as emotion

app = FastAPI()
app.include_router(whisper)
app.include_router(tts)
app.include_router(emotion)

origins = [
            "http://216.128.13.126/32:8081",        # Frontend Expo server
            "http://216.128.13.126/32:8000"         # Backend Uvicorn server
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
    uvicorn.run(app, host = "127.0.0.1", port = 8000, ws_ping_interval = 20, ws_ping_timeout = 60)      # Run on localhost:8000