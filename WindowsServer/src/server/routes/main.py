from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes.whisper import router as whisper
from server.routes.emotion import router as emotion
from server.routes.bert import router as bert

app = FastAPI()
app.include_router(whisper)
app.include_router(emotion)
app.include_router(bert)

origins = [
            "http://109.242.186.148:8081",        # Frontend Expo server
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