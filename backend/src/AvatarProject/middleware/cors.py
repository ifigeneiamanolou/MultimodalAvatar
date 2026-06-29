from backend.src.AvatarProject.routes.main import app
from fastapi import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8081",
                     "http://localhost:8082"],          # Change in production    
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials = True      
)