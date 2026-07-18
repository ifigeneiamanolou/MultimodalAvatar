from faster_whisper import WhisperModel
from pathlib import Path
import torch

# models
_models = {}

# Settings
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "int8"

def transcription(model_id : str, path : Path) -> str:
    """ Perform audio transcription 

    Args:
        model_id (str):  Whisper model id
        path (Path): path of the audio to transcribe

    Raises:
        TypeError: if the model id is invalid

    Returns:
        str: the transcription of the input audio
    """

    # Check model id
    if model_id not in ["small", "tiny", "tiny.en", "base", "base.en", "small", "small.en", "distil-small.en", "medium", "medium.en", "distil-medium.en", "large-v1",
            "large-v2", "large-v3", "large", "distil-large-v2", "distil-large-v3", "large-v3-turbo", "turbo"]:
        raise TypeError("No model found")
    
    # Load model
    if model_id not in _models.keys():
        _models[model_id] = WhisperModel(model_size_or_path = model_id, device = device, compute_type = compute_type)  

    # Perform audio transcription
    segments, _ = _models[model_id].transcribe(
        path,                     # Absolute path to webm file stored locally
        language = "en",
        vad_filter = True,        # Address hallucination
        vad_parameters = dict(
            min_silence_duration_ms=500,
            speech_pad_ms=400
        ),
        condition_on_previous_text=False,
        beam_size = 1             # Faster inference
    )
    
    text = " ".join([segment.text for segment in segments])
    return text