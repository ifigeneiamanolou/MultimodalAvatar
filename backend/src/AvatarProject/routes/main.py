from fastapi import FastAPI
from src.AvatarProject.routes.whisper import router as whisper
from src.AvatarProject.routes.whisperAWS import router as whisperAWS
from src.AvatarProject.routes.avatar import router as avatar
from src.AvatarProject.routes.feedback import router as feedback
from src.AvatarProject.routes.tts import router as tts
from src.AvatarProject.routes.response import router as response

app = FastAPI()
app.include_router(whisper)
app.include_router(whisperAWS)
app.include_router(feedback)
app.include_router(tts)
app.include_router(response)
app.include_router(avatar)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "127.0.0.1", port = 8000, ws_ping_interval = 20, ws_ping_timeout = 60)