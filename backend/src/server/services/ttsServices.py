import websockets
from fastapi import WebSocket
import base64
import json
from backend.src.server.services.fileServices import save_audio_stream
import os
from dotenv import load_dotenv

load_dotenv()
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]

async def textToSpeechStreaming(text : str, voice_id : str, model_id : str):
    """ Initiate a connection to the ElevenLabs streaming API and send data

    Args:
        text (str): ipput text
        voice_id (str): ElevenLabs voice ID
        model_id (str): ElevenLabs model ID
    """

    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model_id}"
    with websockets.connect(uri) as WebSocket:
        WebSocket.send(json.dumps({
            "text" : text.encode("utf-8"),
            "xi_api_key": ELEVENLABS_API_KEY,
        }))

        await listen(WebSocket)

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
                save_audio_stream(base64.b64decode(data["audio"]), "../../data/processed/tts-%s.mp3")
                # Send the audio chunk to Audio2Face
                async with websockets.connect(f'ws://localhost:8765') as websocket:
                    await websocket.send_data(data["audio"])
            elif data.get('isFinal'):
                # Singal to audio2face for the end of the incoming audio
                async with websockets.connect(f'ws://localhost:8765') as websocket:
                    await websocket.send_text("[[DONE]]");
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
            break
