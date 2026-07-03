"""
    Endpoints for emotion detection

"""

from fastapi import APIRouter
from funasr import AutoModel
from pathlib import Path
from src.models.pydantic import ResponseModel
import os
from src.services.fileServices import next_path, save

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   


@router.post("/emotion2vec", response_model = ResponseModel)
async def detectAudioEmotion(audio : bytes):
    """_summary_

    Args:
        path (Path): Directory of audio path to process
    """

    # model="iic/emotion2vec_base"
    # model="iic/emotion2vec_base_finetuned"
    # model="iic/emotion2vec_plus_seed"
    # model="iic/emotion2vec_plus_base"
    model_id = "iic/emotion2vec_base"

    model = AutoModel(
        model = model_id,
        hub = "hf",  # "ms" or "modelscope" for China mainland users; "hf" or "huggingface" for other overseas users
    )

    # Input can be a numpy array, raw binary audio bytes, a path or a URL
    path = next_path(os.path.join(BASE_DIR, "../../data/processed/emotion-%s.txt"))
    pathLabel = next_path(os.path.join(BASE_DIR, "../../data/processed/emotionLabel-%s.txt"))
    result = AutoModel.generate(
        input = audio, 
        extract_embedding = False, 
        output_dir = path, 
        granularity = "frame"
    )
    save(input = result.labels, path = pathLabel)



