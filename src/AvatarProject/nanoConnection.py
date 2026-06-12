import os
from openai import OpenAI
from dotenv import load_dotenv
import edge_tts
import asyncio
from faster_whisper import WhisperModel

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(
    api_key = OPENAI_API_KEY
)

# Given a user query in string format returns the GPT repsponse
def generate_response(user_input):
    response = client.responses.create(
        model = "gpt-5.5-nano",
        input = user_input
    )
    return response.output_text

def start_chatbot():
    print("Welcome to the avatar, say exit to stop.\n")

    with open("file.txt", "r") as file:
        user_input = file.read()

    if user_input.lower() == "exit":
        print("End of the conversation.")
        return None
    else:
        print(f"You : {user_input} \n")
        return generate_response(user_input)
    

async def main():
    # ASR
    model = WhisperModel(model_size_or_path="large-v3", device="cuda", compute_type="int8_float16") # To investigate models
    audio_file = "file.m4a"
    segments, _ = model.transcribe(
        audio_file,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )   
    segments = list(segments)
    for seg in segments:
        print(f"for segment {seg} text is {seg.text} \n")
    # To be moved to a Google Collab GPU and to enable parallel processing (now 3.2s)

    # Directory with the input audio file
    file = open("input.txt", "w")
    full_text = " ".join(seg.text for seg in segments)
    file.write(full_text)
    file.close()

    # NLP
    response = start_chatbot()
    if response:
        print(f"Bot : {response} \n")

    # Directory with output text file
    file = open("output.txt", "w")
    file.write(response)
    file.close()

    # TTS
    tts = edge_tts.Communicate(response, voice="en-US-AriaNeural")

    # Save speech in an mp4 file
    await tts.save("output.mp4")

    # Generate facial animation using OVR Lip Syncing (NVIDIA)

asyncio.run(main())    
 
