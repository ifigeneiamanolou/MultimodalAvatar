from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

# ================== Pydantic models ===================

# Request body pydantic models
class Message(BaseModel):
    role: str
    content: str

class LLMInput(BaseModel):
    emotion : str =  ['angry', 'disgusted', 'fearful', 'happy', 'sad', 'surprised', 'neutral']
    input : list[Message]
    interview_type : int             # 1 corresponds to user being the interviewer and 2 to user being the interviewee   
    model : str | None = "openai/gpt-4o-mini" 

class TTSInput(BaseModel):
    text : str
    language : str
    # Additional fields

class EmotionInput(BaseModel):      # Model used in the emotion2vec endpoint
    model : str = ["iic/emotion2vec_plus_seed", "iic/emotion2vec_plus_base", "iic/emotion2vec_plus_large"]
    audio : str                     # Encoded audio into a base64 string
    language : str                  # Encoded as a language code ie "en"

# Response Body pydantic models
class ResponseModel(BaseModel):
    success : bool
    data : Any | None = None
    message : str
    meta : dict[str, Any] = Field(default_factory=dict)
