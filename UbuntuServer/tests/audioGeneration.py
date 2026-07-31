import pandas as pd
import logging
from dotenv import load_dotenv
from vllm import AsyncLLMEngine, AsyncEngineArgs
from server.services.engine_class import OrpheusModel
import torch
import os
import wave

# GPU
torch.cuda.empty_cache()
device = "cuda" if torch.cuda.is_available() else "cpu"

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# HF token
load_dotenv()
HF_TOKEN = os.environ["HF_TOKEN"]

# Base path
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Monkey patch
def custom_setup_engine(self):
    engine_args = AsyncEngineArgs(
        model=self.model_name,
        dtype=self.dtype,
        max_model_len=2048,
    )
    return AsyncLLMEngine.from_engine_args(engine_args)

def main():
    # Load the dataset as a series    
    db = pd.read_csv(os.path.join(BASE_PATH, "../data/sentences.csv"))
   
    # Initialize the orpheus model
    OrpheusModel._setup_engine = custom_setup_engine
    model =  OrpheusModel(model_name = "canopylabs/orpheus-tts-0.1-finetune-prod")
    
    for index, row in db.iterrows():
        # Perform audio transcription
        syn_tokens = model.generate_speech(
            prompt = row.iloc[0],
            voice = "zoe",
            repetition_penalty=1.1,
            stop_token_ids=[128258],
            max_tokens=2000,
            temperature=0.4,
            top_p=0.9
        )

        # Save the audio as a wav file in the data folder
        path = os.path.join(BASE_PATH, f"../data/sentenceAudio{index}.wav")
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)

            for audio_chunk in syn_tokens: # output streaming
                wf.writeframes(audio_chunk)
        # Logging
        logger.info(msg = f"Finished sentence {index} : {row.iloc[0]}")

if __name__ == "__main__": 
    main()
