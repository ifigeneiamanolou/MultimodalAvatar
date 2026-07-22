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
from fastapi import WebSocketDisconnect, HTTPException
import websockets
from server.services.fileServices import load_template, load_json, saveJSON
from server.services.ttsServices import textToSpeechStreaming, processText
import os
import logging

load_dotenv()
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

class Controller:
    def __init__(self):
        self.queue = asyncio.Queue(maxsize = 50)
        self.current_sentence = ""                  # Sentence currently processed
        self.model = "gpt-4o-mini"                  # Used for emotion generation
        self.orpheus_model = "canopylabs/orpheus-tts-0.1-finetune-prod"
        self.voice = "tara"                         # Voice used in orpheus3b

    async def consume(self):
        while True:
            sentence = await self.queue.get()

            if sentence is None:
                self.signal_end_audio()
                self.queue.task_done()
                break

            self.current_sentence = sentence
            logger.info(msg = f"Current sentence consumed is: {self.current_sentence}")

            try:
                await self.produce_audio_orpheus()
            except Exception as e:
                logger.error(msg = f"Error while uploading to orpheus3 {str(e)}")
            finally:   
                self.queue.task_done()

    async def produce(self, data : str):
        logger.info(msg = f"Produced sentence in the queue : {data}")
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
        try:
            with requests.post(url, headers = headers, json = payload, stream=True) as response:
                response = response.choices[0].message.content
        except Exception as e:
            logger.error(msg = f"Error during emotion generation : {e}")

        return response
    
    async def signal_end_audio(self):
        try:
            async with websockets.connect(f'ws://localhost:8765') as websocket:
                await websocket.send("[[DONE]]")
        except WebSocketDisconnect:
            logger.info(msg = "Disconnected with UE5 server")
        except Exception as e:
            logger.error(msg = f"Error during speech generation from orpheus : {str(e)}")

    async def produce_audio_orpheus(self):
        url = "http://3.151.224.227:8000/orpheus"            # Elastic IP address

        # Configure payload 
        payload = {
            "sentence" : self.current_sentence,
            "voice" : self.voice,
            "model" : self.orpheus_model
        }

        # Send the sentence to Orpheus3B
        try:
            requests.post(url, json = payload) 
        except Exception as e:
            logger.error(msg = f"Error during orpheus 3b remote upload : {e}")

    