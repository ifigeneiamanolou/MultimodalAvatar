import os
from openai import OpenAI
from dotenv import load_dotenv
import edge_tts
import asyncio
from faster_whisper import WhisperModel
import py_audio2face as pya2f

# FILE CONSTANTS
INPUT_FILE = "data/raw/input.m4a"
ASR_TEXT = "data/processed/asr.txt"
RESPONSE_FILE = "data/raw/output.txt"
TTS_FILE = "data/processed/tts.m4a"
ANIMATION_FILE = "data/processed/animation.usd"

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NVIDIA_API_KEY = os.environ["NVIDIA_API_KEY"]       # Audio2Face model

client = OpenAI(
    api_key = OPENAI_API_KEY
)

a2f = pya2f.Audio2Face()

# Given a user query in string format returns the GPT repsponse
def generate_response(user_input):
    response = client.responses.create(
        model = "gpt-5.5-nano",
        input = user_input
    )
    return response.output_text

def start_chatbot():
    print("Welcome to the avatar, say exit to stop.\n")

    with open(ASR_TEXT, "r") as file:
        user_input = file.read()

    if user_input.lower() == "exit":
        print("End of the conversation.")
        return None
    else:
        print(f"You : {user_input} \n")
        return generate_response(user_input)
    

async def main():
    # ASR
    model = WhisperModel(model_size_or_path="large-v3", device="cuda", compute_type="int8_float16") 
    segments, _ = model.transcribe(
        INPUT_FILE,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )   
    segments = list(segments)
    for seg in segments:
        print(f"for segment {seg} text is {seg.text} \n")

    # Writing text generated into a file
    file = open(ASR_TEXT, "w")
    full_text = " ".join(seg.text for seg in segments)
    file.write(full_text)
    file.close()

    # NLP
    response = start_chatbot()
    if response:        # If input isnt exit
        print(f"Bot : {response} \n")

    # Store the bot response
    file = open(RESPONSE_FILE, "w")
    file.write(response)
    file.close()

    # TTS
    tts = edge_tts.Communicate(response, voice="en-US-AriaNeural")

    # Save speech in an mp4 file
    await tts.save(TTS_FILE)

    # Generate facial animation
    a2f.audio2face_single(
        audio_file_path= TTS_FILE,
        output_path= ANIMATION_FILE,
        fps=60, # Higher fps will result in smoother animations and longer processing time
        emotion_auto_detect=True  # automatically detect emotions in the audio file. If false the set emotion will be used
    )

asyncio.run(main())    
 
