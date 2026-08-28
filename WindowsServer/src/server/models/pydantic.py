from typing import Any, Literal, Annotated
from pydantic import BaseModel, Field

# ================== Pydantic models ===================

# Request body pydantic models
class EmotionInput(BaseModel):      # Model used in the emotion2vec endpoint
    model : str = ["iic/emotion2vec_plus_seed", "iic/emotion2vec_plus_base", "iic/emotion2vec_plus_large"]
    audio : str                     # Encoded audio into a base64 string
    language : str                  # Encoded as a language code ie "en"

class TTSInput(BaseModel):
    text : str
    language_code : Literal['a', 'e', 'f', 'h', 'i', 'j', 'p', 'z']
    voice : str

class BertInput(BaseModel):
    sentence : str

# Response Body pydantic models
class ResponseModel(BaseModel):
    success : bool
    data : Any | None = None
    message : str
    meta : dict[str, Any] = Field(default_factory=dict)

class BertOutput(BaseModel):
    text : str
    emotion : Literal['amazement', 'anger', 'cheekiness', 'disgust', 'fear', 'grief', 'joy', 'out of breath', 'pain', 'sadness', 'neutral']
    maxProb : Annotated[float, Field(gt = 0, lt = 1)]
    predictions : dict