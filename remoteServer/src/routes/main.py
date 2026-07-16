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
            "http://188.73.239.65/32:8081",        # Frontend Expo server
            "http://188.73.239.65/32:8000"         # Backend Uvicorn server
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
    # Without host 0.0.0.0 it won't listen to all network interfaces, only localhost