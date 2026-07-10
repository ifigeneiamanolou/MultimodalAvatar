""""
    Handles incoming sentences from the sentence buffer, maintaining a queue of sentences. These are forwarded for TTS and emotion
    detection asychronously using an asyncio Task Group, that handles ongoing tasks cleaning automatically. Once both tasks are 
    finished, a new instance of the data class SyncedChunk is created containing both the audio bytes and the emotion parameters
    generated, as well as a sequence id to keep track of all sentences that need to be sent to the UE5 application for pixel 
    streaming. The management of all pending pixel streaming requests is handled by audio2facedispatcher.

"""

import asyncio
import requests
from dotenv import load_dotenv
from src.services.fileServices import load_template
import os
from dataclasses import dataclass

load_dotenv()
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   

@dataclass
class SyncedChunk:
    sequence_id : int
    audio_bytes : bytes             # PCM 16-bit format
    emotion_params : dict           # Emotion configuration

class Controller:
    def __init__(self):
        self.queue = asyncio.Queue(maxsize = 50)


    async def consume(self):
        while True:
            sentence = await self.queue.get()

            if sentence is None:
                self.queue.task_done()
                break

            try:
                # Perform some task
                async with asyncio.TaskGroup() as task_group:
                    emotionTask = task_group.create_task(self.produce_emotions(sentence, "gpt-4o-mini"))
                    audioTask = task_group.create_task(self.produce_audio(sentence))
            finally:   
                self.queue.task_done()


    async def produce(self, data : str):
        await self.queue.put(data)

    async def produce_emotions(sentence : str, model : str):
        # API endpoint
        url = "https://openrouter.ai/api/v1/chat/completions"

        # Authorization headers for OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Load template
        instructions = load_template("emotions")

        # Input processing
        input = [
            {
                "role" : "developer",
                "content" : instructions
            },
            {
                "role" : "user",
                "content" : sentence
            }
        ]

        # Request payload
        payload = {
            "model": model,
            "messages": input,
            "stream": False
        }

        with requests.post(url, headers = headers, json = payload, stream=True) as response:
            response = response.choices[0].message.content

    async def produce_audio(sentence : str):
        url = "http://<your-ec2-public-ip>:8000"

        # Configure payload 
        payload = {"content" : sentence}

        with requests.post(url, json = payload) as response:
            # Receive PCM 16-but audio
            pass
        pass