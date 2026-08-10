import asyncio
import websockets
import logging
from typing import Optional
import aiohttp
import json
import time

# Configure logging
logger = logging.getLogger(__name__)

class Controller:
    """ Handles incoming sentences from the sentence buffer, maintaining a queue of sentences using an Asyncio queue 
        with the consumer-producer pattern. These are forwarded for TTS and emotion detection asychronously using an 
        asyncio Task Group, that handles ongoing tasks cleaning automatically. As soon as emotion probailities from 
        distilbert or audio chunk (in raw binary format) are received, they are sent to A2F, with the latter 
        accompanied with an audio header containing information like the length of the audio chunk and the number of 
        the sentence or the audio chunk. Once both tasks have finished, the consumer forwards the next sentence to 
        Orpheus3B and DistilBert.
    """
    def __init__(self):
        # General attributes
        self.queue = asyncio.Queue(maxsize = 50)
        self.current_sentence = ""                  # Sentence currently processed
        self.orpheus_model = "canopylabs/orpheus-tts-0.1-finetune-prod"
        self.voice = "zoe"                         # Voice used in orpheus3b
        self._sequence_id = 0

        # Orpheus3B and distilbert
        self.windows_url = "http://3.129.236.140:8000/distilbert"             # DistilBert (elastip ip)
        self.ubuntu_url = "http://3.151.224.227:8000/orpheus"                 # Orpheus3B (elastic ip)
        self._session_windows : Optional[aiohttp.ClientSession] = None        # Asychronous HTTP requests to Windows server
        self._session_ubuntu : Optional[aiohttp.ClientSession] = None         # Asychronous HTTP requests to Ubuntuserver

        # Web socket
        self.ws_url = "ws://3.129.236.140:7865"         # replace with ec2 ipv4                           
        self._ue5_lock = asyncio.Lock()                 # Avoid sending both emotion and audio to UE5
        self._ue5_ws = None                             # Web socket connection with UE5 app

    ############################################################
    # Lifecycle
    ############################################################

    async def start(self):
        """ 
            Starts aiohttp sessions with the Uvicorn servers in the AWS instances and connects to the UE5 app via a web socket
        """
        # Start sessions for http requests
        logger.info("starting http sessions")
        self._session_windows = aiohttp.ClientSession()
        self._session_ubuntu = aiohttp.ClientSession()

        # Connect to the web socket 
        await self.connect_ue5()

    async def close(self):
        """ 
            Stops the aiohttp sessions, empties the asyncio queue and disconnects from the UE5 app 
        """
        if self._ue5_ws:
            await self._ue5_ws.close()
            logger.info("Disconnected from UE5 server")

        if self._session_windows:
            await self._session_windows.close()
            logger.info("Disconnected from windows HTTP session")

        if self._session_ubuntu:
            await self._session_ubuntu.close()
            logger.info("Disconnected from ubuntu HTTP session")

        # Empty the queue
        while not self.queue.empty:
            self.queue.get()

    async def connect_ue5(self):
        """ 
            Establishes a websocket connection with the websocket server in the UE5 app
        """
        try:
            self._ue5_ws = await websockets.connect(self.ws_url)
            logger.info(f"connected to {self.ws_url}")
        except Exception as e:
            self._ue5_ws = None
            logger.info(f"Unable to connect to {self.ws_url} with error {str(e)}")

    async def ensure_connection(self):
        """ 
            Attempts to connect to the UE5 web server before sending any data
        """
        if self._ue5_ws is None:
            try:
                self._ue5_ws = await websockets.connect(self.ws_url)
            except Exception as e:
                self._ue5_ws = None
                logger.info(f"Unable to connect to {self.ws_url} with error {str(e)}")
            
    ############################################################
    # Queue management
    ############################################################

    async def consume(self):
        """ 
            Consumer for the asyncio queue containing the NLP produced sentence
        """
        while True:
            sentence = await self.queue.get()

            if sentence == "[[DONE]]":       
                await self.signal_end_audio()
                self.queue.task_done()
                break

            self.current_sentence = sentence
            id = self._sequence_id
            self._sequence_id += 1

            logger.info(msg = f"Current sentence consumed is {id} : {self.current_sentence}")

            try:
                # Wait for both tasks to finish to move to the next sentence
                start = time.perf_counter()
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self.produce_audio_orpheus(self.current_sentence, id))
                    tg.create_task(self.emotion(self.current_sentence, id))
                end = time.perf_counter()
                logger.info(f"Total processing time of sentence [{sentence}] is {end - start} seconds")
            except Exception as e:
                logger.error(msg = f"Error processing sentence {id} : {e}")
            finally:   
                self.queue.task_done()

    async def produce(self, data : str):
        """ Producer for the asyncio queue containing the NLP produced sentences

        Args:
            data (str): the sentence to be placed in the queue
        """
        logger.info(msg = f"Produced sentence in the queue : {data}")
        await self.queue.put(data)

    ############################################################
    # Signal end of audio
    ############################################################
    
    async def signal_end_audio(self):
        """ 
            Sends a text signal "[[DONE]]" to the UE5 WebServer to signal the end of an NLP response
        """
        await self.ensure_connection()
        if self._ue5_ws is None:
            logger.info("Unable to send [[DONE]]. Server is unavailable")
            return
        
        try:
            async with self._ue5_lock:
                await self._ue5_ws.send("[[DONE]]")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Disconnected from UE5 server")
            self._ue5_ws = None
        except Exception as e:
            logger.error(f"Error from UE5 server : {e}")
            self._ue5_ws = None

    ############################################################
    # Orpheus TTS
    ############################################################

    async def produce_audio_orpheus(self, sentence : str, id : int):
        """ Forwards a sentence to Orpheus3B and forwards the output chunks to UE5 along with informative headers

        Args:
            sentence (str): the sentence to send to A2F
            id (int): the id of the sentence
        """
        # Configure payload 
        payload ={
            "sentence" : sentence,
            "voice" : self.voice,
            "model" : self.orpheus_model
        }

        chunk_index = 0
        # Send the sentence to Orpheus3B
        try:
            start = time.perf_counter()
            async with self._session_ubuntu.post(self.ubuntu_url, json = payload) as resp:
                index = 0
                async for audio_chunk in resp.content.iter_any():
                    if index % 10 == 0:
                        logger.info(f"Time until token {index} is received in the controller from Oprheus3B is {time.perf_counter() - start}")
                    if not audio_chunk:
                        continue
                    await self.send_audio_bytes(id, chunk_index, audio_chunk)
                    chunk_index += 1
                    index += 1
            await self.send_audio_end(id)
            logger.info(f"Time sentence [{sentence}] is finished from Oprheus is {time.perf_counter() - start}")
        except Exception as e:
            logger.error(msg = f"Error during orpheus 3b remote upload :  {type(e).__name__}: {e}", exc_info=True)

    async def send_audio_bytes(self, id : int, chunk_index : int, audio_chunk : bytes):
        """ Sends the audio chunk received by Oprheus3B to A2F along with informative headers

        Args:
            id (int): the id of the sentence the chunk belongs to
            chunk_index (int): the id of the chunk
            audio_chunk (bytes): the audio chunk received by Oprheus3B
        """
        await self.ensure_connection()
        if self._ue5_ws is None:
            logger.info("Unable to send audio bytes. Server is unavailable")
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
        except websockets.exceptions.ConnectionClosed:
            logger.info("Disconnected from UE5 server")
            self._ue5_ws = None
        except Exception as e:
            logger.error(f"Error from UE5 server : {e}")
            self._ue5_ws = None

    async def send_audio_end(self, id : int):
        """ Sends a signal to the UE5 app to notify about the end of a sentence

        Args:
            id (int): the id of the sentence that just ended
        """
        await self.ensure_connection()
        if self._ue5_ws is None:
            logger.info("Unable to send done signal. Server is unavailable")
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
        except websockets.exceptions.ConnectionClosed:
            logger.info("Disconnected from UE5 server")
            self._ue5_ws = None
        except Exception as e:
            logger.error(f"Error from UE5 server : {e}")
            self._ue5_ws = None

    ############################################################
    # Distilbert emotion generation
    ############################################################

    async def emotion(self, sentence : str, id : int):
        """ Performs distilbert inference for a sentence and sends the results to the UE5 WebServer

        Args:
            sentence (str): the sentence for which we perform inference
            id (int): the id of the sentence
        """
        start = time.perf_counter()
        try:
            emotions = await self.produce_emotion(sentence)
        except Exception as e:
            logger.error(f"Error during emotion generation {id} : {e}")
        end = time.perf_counter()
        logger.info(f"Time for emotion generation of [{sentence}] is {time.perf_counter() - start}")

        try:
            await self.send_ue5_emotion(emotions, id)
        except Exception as e:
            logger.error(f"Error while sending emotion {id} : {e}")

    async def produce_emotion(self, sentence) -> dict[str, any]:
        payload = {"sentence" : sentence}
        async with self._session_windows.post(self.windows_url, json = payload) as resp:
            return await resp.json()

    async def send_ue5_emotion(self, emotions : dict[str, any], id : int):
        """ Sends the result of distilbert inference to A2F

        Args:
            emotions (dict[str, any]): results from distilbert (scores, maximum score and corresponding emotion label)
            id (int): id of the sentence
        """
        await self.ensure_connection()
        if self._ue5_ws is None:
            logger.info("Unable to send emotion. Server is unavailable")
            return
        
        data = json.dumps(
            {
                "type" : "emotion",
                "sentence_id" : id,                             # indicate id of sentence
                "sentence" : emotions['text'],                  # sentence for which emotion is produced
                "emotion" : emotions['emotion'],                # leading emotion
                "predictions" : emotions['predictions'],        # coefficients generated
                "maxProb" : emotions['maxProb']                 # value of leading emotion
            }
        )     

        try:
            async with self._ue5_lock:
                await self._ue5_ws.send(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Disconnected from UE5 server")
            self._ue5_ws = None
        except Exception as e:
            logger.error(f"Error from UE5 server : {e}")
            self._ue5_ws = None

controller = Controller()

    