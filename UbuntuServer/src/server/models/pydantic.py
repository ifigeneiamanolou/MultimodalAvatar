from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

# ================== Pydantic models ===================

# Request body pydantic models
class TTSInput(BaseModel):
    sentence : str
    voice : str = ["zoe", "zac","jess", "leo", "mia", "julia", "leah"]
    model : str = ["canopylabs/orpheus-tts-0.1-finetune-prod"]

# Response Body pydantic models
class ResponseModel(BaseModel):
    success : bool
    data : Any | None = None
    message : str
    meta : dict[str, Any] = Field(default_factory=dict)
