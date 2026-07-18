from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

# ================== Pydantic models ===================

# Request body pydantic models
class EmotionInput(BaseModel):      # Model used in the emotion2vec endpoint
    model : str = ["iic/emotion2vec_plus_seed", "iic/emotion2vec_plus_base", "iic/emotion2vec_plus_large"]
    audio : str                     # Encoded audio into a base64 string
    language : str                  # Encoded as a language code ie "en"

class TTSInput(BaseModel):
    sentence : str
    voice : str = ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]
    model : str = ["canopylabs/orpheus-tts-0.1-finetune-prod"]

# Response Body pydantic models
class ResponseModel(BaseModel):
    success : bool
    data : Any | None = None
    message : str
    meta : dict[str, Any] = Field(default_factory=dict)
