from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes.feedbackNew import router as feedback
from server.routes.response import router as response
from server.utils.controller import controller
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await controller.start()
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