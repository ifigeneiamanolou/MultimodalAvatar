""""
    Handles incoming sentences from the sentence buffer, maintaining a queue of sentences. These are forwarded for TTS and emotion
    detection asychronously using an asyncio Task Group, that handles ongoing tasks cleaning automatically. Once both tasks are 
    finished, emotion probabilities by distilbert and audio chunks (in raw binary format) are forwarded to Audio2Face via the UE5 
    application.

"""

import asyncio
import requests
from fastapi import WebSocketDisconnect
import websockets
import os
import logging
from typing import Optional
import aiohttp
import json

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
        self.orpheus_model = "canopylabs/orpheus-tts-0.1-finetune-prod"
        self.voice = "tara"                         # Voice used in orpheus3b
        self._sequence_id = 0

        self.windows_url = "http://3.129.236.140:8000/distilbert"                      # DistilBert (elastip ip)
        self.ubuntu_url = "http://3.151.224.227:8000/orpheus"                          # Orpheus3B (elastic ip)
        self.ws_url = "http://3.129.236.140:8765"
        self.chunk_size = 4096

        self._ue5_lock = asyncio.Lock()                                       # Avoid sending both emotion and audio to UE5
        self._session : Optional[aiohttp.ClientSession] = None                # Asychronous HTTP requests
        self._ue5_ws = None    # Web socket connection with UE5 app

    ############################################################
    # Lifecycle
    ############################################################

    async def start(self):
        # Start session for http requests
        self._session = aiohttp.ClientSession()

        # Connect to the web socket
        await self.connect_ue5()

    async def close(self):
        if self._ue5_ws:
            await self._ue5_ws.cloe()
            logger.info("Disconnected from UE5 server")

        if self._session:
            await self._session.close()
            self.logger.info("Disconnected from HTTP session")

    async def connect_ue5(self):
        try:
            self._ue5_ws = await websockets.connect(self.ws_url)
            logger.info(f"Connected to {self.ws_url}")
        except Exception as e:
            self._ue5_ws = None
            logger.info(f"Unable to connect to {self.ws_url} with error {str(e)}")

    async def ensure_connection(self):
        if self._ue5_ws is None or self._ue5_ws.connection_lost:
            await self.connect_ue5()
        
    ############################################################
    # Queue management
    ############################################################

    async def consume(self):
        while True:
            sentence = await self.queue.get()

            if sentence is None:
                await self.signal_end_audio()
                self.queue.task_done()
                break

            self.current_sentence = sentence
            id = self._sequence_id
            self._sequence_id += 1

            logger.info(msg = f"Current sentence consumed is {id} : {self.current_sentence}")

            try:
                # Wait for both tasks to finish to move to the next sentence
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self.produce_audio_orpheus(self.current_sentence, id))
                    tg.create_task(self.emotion(self.current_sentence, id))
            except* Exception as exs:
                for e in exs:
                    logger.error(msg = f"Error processing sentence {id} : {str(e)}")
            finally:   
                self.queue.task_done()

    async def produce(self, data : str):
        logger.info(msg = f"Produced sentence in the queue : {data}")
        await self.queue.put(data)

    ############################################################
    # Signal end of audio
    ############################################################
    
    async def signal_end_audio(self):
        await self.ensure_connection()
        if self._ue5_ws is None:
            logger.info("Unable to send [[DONE]]. Server is unavailable")
            return
        
        try:
            async with self._ue5_lock:
                await self._ue5_ws.send("[[DONE]]")
        except WebSocketDisconnect:
            logger.info("Disconnected from UE5 server")
            self._ue5_ws = None
        except Exception as e:
            logger.error(f"Error from UE5 server : {str(e)}")
            self._ue5_ws = None

    ############################################################
    # Orpheus TTS
    ############################################################

    async def produce_audio_orpheus(self, sentence : str, id : int):
        # Configure payload 
        payload = json.dumps(
            {
                "sentence" : sentence,
                "voice" : self.voice,
                "model" : self.orpheus_model
            }
        )
        chunk_index = 0
        # Send the sentence to Orpheus3B
        try:
            async with self._session.post(self.ubuntu_url, json = payload) as resp:
                async for audio_chunk in resp.content.iter_chunked(self.chunk_size):
                    if not audio_chunk:
                        continue
                    await self.send_audio_bytes(id, chunk_index, audio_chunk)
                    chunk_index += 1

            await self.send_audio_end(id)
        except Exception as e:
            logger.error(msg = f"Error during orpheus 3b remote upload : {e}")

    async def send_audio_bytes(self, id : int, chunk_index : int, audio_chunk : bytes):
        await self.ensure_connection()
        if self._ue5_ws is None:
            logger.info("Unable to send audio chunk. Server is unavailable")
            return

        header = json.dumps(
            {
                "type" : "audio_chunk",
                "sentence_id" : id,                 # indicate id of sentence
                "chunk_index" : chunk_index,
                "length" : len(audio_chunk)
            }
        )

        try:
            async with self._ue5_lock:
                await self._ue5_ws.send(header)
                await self._ue5_ws.send(audio_chunk)
        except WebSocketDisconnect:
            logger.info("Disconnected from UE5 server")
            self._ue5_ws = None
        except Exception as e:
            logger.error(f"Error from UE5 server : {str(e)}")
            self._ue5_ws = None

    async def send_audio_end(self, id : int):
        await self.ensure_connection()
        if self._ue5_ws is None:
            logger.info("Unable to send audio chunk. Server is unavailable")
            return

        header = json.dumps(
            {
                "type" : "audio_end",
                "sentence_id" : id,                 # indicate id of sentence
            }
        )

        try:
            async with self._ue5_lock:
                await self._ue5_ws.send(header)
        except WebSocketDisconnect:
            logger.info("Disconnected from UE5 server")
            self._ue5_ws = None
        except Exception as e:
            logger.error(f"Error from UE5 server : {str(e)}")
            self._ue5_ws = None

    ############################################################
    # Distilbert emotion generation
    ############################################################

    async def emotion(self, sentence, id):
        try:
            emotions = await self.produce_emotion(sentence)
        except Exception as e:
            logger.error(f"Error during emotion generation {id} of : {sentence}")
            raise

        await self.send_ue5_emotion(emotions, id)

    async def produce_emotion(self, sentence) -> dict[str, any]:
        payload = {"sentence" : sentence}
        async with self._session.post(self.windows_url, json = payload) as resp:
            return await resp.json()

    async def send_ue5_emotion(self, emotions : dict[str, any], id : int):
        await self.ensure_connection()
        if self._ue5_ws is None:
            logger.info("Unable to send emotion. Server is unavailable")
            return

        data = json.dumps(
            {
                "type" : "emotion",
                "sentence_id" : id,                 # indicate id of sentence
                "sentence" : emotions['sentence'],
                "emotion" : emotions['emotion'],
                "predictions" : emotions['predictions'],
                "maxProb" : emotions['maxProb']
            }
        )     

        try:
            async with self._ue5_lock:
                await self._ue5_ws.send(data)
        except WebSocketDisconnect:
            logger.info("Disconnected from UE5 server")
            self._ue5_ws = None
        except Exception as e:
            logger.error(f"Error from UE5 server : {str(e)}")
            self._ue5_ws = None



    