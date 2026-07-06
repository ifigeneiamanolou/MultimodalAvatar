from pathlib import Path
from pydantic import BaseModel

# ================== Pydantic models ===================

# Request body pydantic models

class Message(BaseModel):
    role: str
    content: str

class UserInput(BaseModel):
    emotion : str =  ['angry', 'disgusted', 'fearful', 'happy', 'sad', 'surprised', 'neutral']
    input : list[Message]
    interview_type : int             # 1 corresponds to user being the interviewer and 2 to user being the interviewee    

class TTSInput(BaseModel):
    text : str
    path : Path | None = None       # Path to store artkit coefficients, if not provided, new file
    # Additional fields

class EmotionInput(BaseModel):      # Model used in the emotion2vec endpoint
    model : str = ["iic/emotion2vec_plus_seed", "iic/emotion2vec_plus_base", "iic/emotion2vec_plus_large"]
    audio : bytes

# Response Body pydantic models
class ResponseModel(BaseModel):
    success : bool
    data : str | dict
    message : str
    meta : dict = {}
