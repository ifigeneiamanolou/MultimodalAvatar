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
from backend.src.server.services.fileServices import load_template, load_json, saveJSON
from backend.src.server.services.ttsServices import textToSpeechStreaming
import os
from dataclasses import dataclass

load_dotenv()
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

@dataclass
class SyncedChunk:
    sequence_id : int
    audio_bytes : bytes             # PCM 16-bit format
    emotion_params : dict = {}      # Emotion configuration

class Controller:
    def __init__(self):
        self.queue = asyncio.Queue(maxsize = 50)
        self.current_sentence = ""                  # Sentence currently processed
        self.model = "gpt-4o-mini"                  # Used for emotion generation


    async def consume(self):
        while True:
            sentence = await self.queue.get()

            if sentence is None:
                self.queue.task_done()
                break
            else:
                self.current_sentence = sentence

            try:
                async with asyncio.TaskGroup() as task_group:
                    await task_group.create_task(self.produce_emotions("gpt-4o-mini"))
                    await task_group.create_task(self.produce_audio_elevenlabs())
            except Exception as e:
                print(f"\n Sentence : {sentence} failed with error {e} \n")
            finally:   
                self.queue.task_done()

    async def produce(self, data : str):
        await self.queue.put(data)

    async def produce_emotions(self):
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
                "content" : self.current_sentence
            }
        ]

        # Response JSON schema
        schema = load_json("../../data/templates/schema.json")

        format = {
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "Emotions",
                    "strict": True,
                    "schema": schema
                }
            }
        }

        # Request payload
        payload = {
            "model": self.model,
            "messages": input,
            "response_format" : format,
            "stream": False
        }

        with requests.post(url, headers = headers, json = payload, stream=True) as response:
            response = response.choices[0].message.content

        # Save the response for debugging
        saveJSON(response, "../../processed/emotionParameters-%s.json")

    async def produce_audio_orpheus(self):
        url = "http://3.129.236.140:8000/orpheus"

        # Configure payload 
        payload = {"content" : self.current_sentence}

        # Send the sentence to Orpheus3B
        requests.post(url, json = payload) 

    async def produce_audio_elevenlabs(self):
        voice_id = "JBFqnCBsd6RMkjVDRZzb"  # "George"
        model_id = "eleven_flash_v2_5"
        textToSpeechStreaming(self.current_sentence, voice_id, model_id)

    