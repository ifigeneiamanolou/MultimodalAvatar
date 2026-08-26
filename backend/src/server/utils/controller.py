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
    """ Handles incoming audio chunks from the LLM and forwards the to UE5 using an Asyncio queue
    with the consumer-producer pattern. 
    """

    def __init__(self):
        # General attributes
        self.queue = asyncio.Queue(maxsize = 50)
        self.chunk_id = 0

        # Web socket
        self.ws_url = "ws://3.129.236.140:7865"         # replace with ec2 ipv4                           
        self._ue5_lock = asyncio.Lock()                 # Avoid sending both emotion and audio to UE5
        self._ue5_ws = None                             # Web socket connection with UE5 app

    ############################################################
    # Lifecycle
    ############################################################

    async def start(self):
        """ 
           Connect to the UE5 app via a web socket when starting the server
        """
        try:
            self._ue5_ws = await websockets.connect(self.ws_url)
            logger.info(f"connected to {self.ws_url}")
        except Exception as e:
            self._ue5_ws = None
            logger.info(f"Unable to connect to {self.ws_url} with error {str(e)}")

    async def restart(self):
        """
            Restarts the state of the controller once a new LLM stream starts
        """
        # Empty the queue
        while not self.queue.empty:
            self.queue.get()

        # Reset chunk id 
        self.chunk_id = 0
        
    async def close(self):
        """ 
            Empties the asyncio queue and disconnects from the UE5 app on server shutdown
        """
        if self._ue5_ws:
            await self._ue5_ws.close()
            logger.info("Disconnected from UE5 server")

        # Empty the queue
        while not self.queue.empty:
            self.queue.get()

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
            Consumer for the asyncio queue containing the NLP produced chunks
        """
        while True:
            chunk = await self.queue.get()

            if chunk == "[[DONE]]":       
                await self.signal_end_audio()
                self.queue.task_done()
                break

            logger.info(msg = f"Current chunk consumed is {id} : {self.chunk_id}")

            try:
                self.send_audio(chunk)
            except Exception as e:
                logger.error(msg = f"Error processing sentence {id} : {e}")
            finally:   
                self.queue.task_done()

    async def produce(self, data : str):
        """ Producer for the asyncio queue containing the NLP produced chunks

        Args:
            data (str): the chunk to be placed in the queue
        """
        logger.info(msg = f"Produced sentence in the queue : {data}")
        await self.queue.put(data)

    ############################################################
    # Communication with UE5
    ############################################################
    async def signal_filler(self):
        """ 
            Sends a text signal to UE5 to start a random cached filler
        """
        await self.ensure_connection()
        if self._ue5_ws is None:
            logger.info("Unable to send [[FILLER]]. Server is unavailable")
            return
            
        try:
            async with self._ue5_lock:
                await self._ue5_ws.send("[[FILLER]]")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Disconnected from UE5 server")
            self._ue5_ws = None
        except Exception as e:
            logger.error(f"Error from UE5 server : {e}")
            self._ue5_ws = None
    
    async def signal_end_audio(self):
        """ 
            Sends a text signal "[[DONE]]" to the UE5 WebServer to signal the end of an NLP stream
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

    async def send_audio(self, audio_chunk : str):
        """ Sends the audio chunk received by the LLM to A2F

        Args:
            id (int): the id of the chunk
            audio_chunk (str): the audio chunk received by the LLM
        """
        await self.ensure_connection()
        if self._ue5_ws is None:
            logger.info("Unable to send audio bytes. Server is unavailable")
            return

        try:
            async with self._ue5_lock:
                await self._ue5_ws.send(audio_chunk)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Disconnected from UE5 server")
            self._ue5_ws = None
        except Exception as e:
            logger.error(f"Error from UE5 server : {e}")
            self._ue5_ws = None

controller = Controller()