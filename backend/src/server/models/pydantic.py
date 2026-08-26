from pathlib import Path
from typing import Any, Literal
from pydantic import BaseModel, Field

# ================== Pydantic models ===================

# Request body pydantic models
class Message(BaseModel):
    role: str
    content: str

# Used when calling the LLM with text input
class LLMInput(BaseModel):
    input : list[Message]
    interview_type : int = Field(int, ge = 1, le = 2)
    model : str | None = "openai/gpt-4o-audio-preview"

# Used when calling the LLM with audio input
class LLMAudioInput(BaseModel):
    input : str             # base64 encoded string
    interview_type : int = Field(int, ge = 1, le = 2)            
    messages : list[Message] 
    model : str | None = "openai/gpt-4o-audio-preview"

# Used to generate feedback
class UserInput(BaseModel):
    input : list[Message]
    interview_type : int = Field(int, ge = 1, le = 2)            
    # 1 corresponds to user being the interviewer and 2 to user being the interviewee   

# Used in the endpoints for storing the feedback in the db
class FeedbackInput(BaseModel):
    messages : str
    interview_type : int = Field(int, ge = 1, le = 2)
    id : int
    feedback : str

# Response Body pydantic models
class ResponseModel(BaseModel):
    success : bool
    data : Any | None = None
    message : str
    meta : dict[str, Any] = Field(default_factory=dict)
