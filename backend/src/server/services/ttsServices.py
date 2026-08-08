import websockets
from fastapi import WebSocket, HTTPException
import base64
import json
from server.services.fileServices import save_audio_stream
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import asyncio
import logging

load_dotenv()
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
elevenlabs = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

# Configure logging
logger = logging.getLogger(__name__)

async def textToSpeechStreaming(text : str, voice_id : str, model_id : str):
    """ Initiate a connection to the ElevenLabs streaming API and send data

    Args:
        text (str): ipput text
        voice_id (str): ElevenLabs voice ID
        model_id (str): ElevenLabs model ID
    """

    uri = f"ws://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model_id}"
    async with websockets.connect(uri) as WebSocket:
        try:
            await WebSocket.send(json.dumps({
                "text" : text.encode("utf-8"),
                "xi_api_key": ELEVENLABS_API_KEY,
            }))
        except Exception as e:
            logger.error(msg = f"Error during text upload {str(e)}")

        try:
            # Send empty string to indicate the end of the text sequence which will close the WebSocket connection
            await WebSocket.send(json.dumps({"text": ""}))
        except Exception as e:
            logger.error(msg = f"Error when closing elevenlabs connection {str(e)}")

        try:
            # Add listen task to pass audio chunks to audio2face
            listen_task = asyncio.create_task(listen(WebSocket))
            await listen_task
        except Exception as e:
            logger.error(msg = f"Error during audio upload to Audio2Face {str(e)}")
    

async def listen(websocket : WebSocket):
    """
        Listen to the websocket for audio data and stream it.

        Args:
            websocket (WebSocket): ElevenLabs websocket connection
    """

    while True:
        try:
            message = await websocket.recv()
            data = json.loads(message)
            if data.get("audio"):
                # Save received audio chunk
                save_audio_stream(base64.b64decode(data["audio"]), "../../../data/processed/tts-%s.mp3")
                # Send the audio chunk to Audio2Face
                async with websockets.connect(f'ws://localhost:8765') as websocket:
                    await websocket.send_data(data["audio"])
            elif data.get('isFinal'):
                # Singal to audio2face for the end of the incoming audio
                async with websockets.connect(f'ws://localhost:8765') as websocket:
                    await websocket.send_text("[[DONE]]")
        except websockets.exceptions.ConnectionClosed:
            logger.error(msg = f"Websocket connection with UE5 closed")
            break

async def processText(text : str, model_id : str, voice_id : str):
    try:
        # Perform the text-to-speech conversion
        response = elevenlabs.text_to_speech.stream(
            voice_id = voice_id,
            output_format = "pcm_16000",            # Format needed by Audio2Face
            text = text,
            model_id = model_id
        )
    except Exception as e:
        logger.error(msg = f"Error speech elevenlabs generation {str(e)}")

    # Send the audio chunks to Audio2Face
    try:
        async with websockets.connect(f'ws://localhost:8765') as websocket:
            for chunk in response:
                if chunk:
                    print(f"chunk is {chunk}\n")
                    await websocket.send_data(chunk)
            await websocket.send_text("[[DONE]]")
    except Exception as e:
        logger.error(msg = f"Error during sending to Audio2Face {str(e)}")


