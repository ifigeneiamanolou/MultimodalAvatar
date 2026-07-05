from pathlib import Path
from pydantic import BaseModel

# ================== Pydantic models ===================

# Request body pydantic models

class Message(BaseModel):
    role: str
    content: str

class UserInput(BaseModel):
    input : list[Message]
    interview_type : int             # 1 corresponds to user being the interviewer and 2 to user being the interviewee    

class TTSInput(BaseModel):
    text : str
    path : Path | None = None       # Path to store artkit coefficients, if not provided, new file
    # Additional fields

# Response Body pydantic models
class ResponseModel(BaseModel):
    success : bool
    data : str | dict
    message : str
    meta : dict = {}
