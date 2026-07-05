from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.whisper import router as whisper
# from src.AvatarProject.routes.whisperAWS import router as whisperAWS
from src.routes.avatar import router as avatar
from src.routes.feedback import router as feedback
from src.routes.tts import router as tts
from src.routes.response import router as response

app = FastAPI()
app.include_router(whisper)
# app.include_router(whisperAWS)
app.include_router(feedback)
app.include_router(tts)
app.include_router(response)
app.include_router(avatar)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8081",
                     "http://localhost:8082",
                     "http://localhost:8000"],          # Change in production    
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True      
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "127.0.0.1", port = 8000, ws_ping_interval = 20, ws_ping_timeout = 60)