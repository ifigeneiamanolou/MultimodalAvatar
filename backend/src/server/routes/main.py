from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.server.routes.feedback import router as feedback
from backend.src.server.routes.response import router as response

app = FastAPI()
app.include_router(feedback)
app.include_router(response)

origins = ["http://localhost:8081",
            "http://localhost:8082",
            "http://localhost:8000"]

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