from pandas import DataFrame, read_csv, Series, concat
import numpy as np
from fastapi import HTTPException, WebSocket
from src.services.fileServices import save_audio_stream
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer.separator import Separator
from phonemizer.backend import EspeakBackend
import os
import websockets
import json
from dotenv import load_dotenv
import base64

# Espeak configuration for phoneme detection
EspeakWrapper.set_library(
    r"C:/Program Files/eSpeak NG/libespeak-ng.dll"
)
backend = EspeakBackend(preserve_punctuation = True, 
                        language = "en-us")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]

# Dictionaries
try:
    db = read_csv(os.path.join(BASE_DIR, "../../data/PhoBlendDataset.csv"))
except Exception as e:
    raise HTTPException(status_code = 500, detail = f"Error when loading the PhoBlendDataset : {e}")

async def generateAnimations(text : str) -> DataFrame:
    """ Given the input text, generate the corresponding artkit blendshape coefficients through a 2-step process:
    1) Convert input text to a list of phonemes
    2) Conver the phonemes to artkit coefficients

    Args:
        text (str): input text

    Raises:
        HTTPException: if the phonemization process files

    Returns:
        DataFrame: Contains the coefficients with each row corresponding to a 3D frame and each column to a coefficient
    """

    try:
        result = backend.phonemize(
            text = list(text),
            separator = Separator(phone = " ", syllable = "|", word = None),
        )       # returns list[str]
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error when phonemizing the text : {e}")

    # Extract the list of phonemes
    phonemes = [p.split(" ") for p in result]
    phonemes = sum(phonemes, [])
    phonemes = [p for p in phonemes if p != '']
    _, c = db.shape
    artkit = DataFrame()       # Empty dataframe to store the coefficients

    for pho in phonemes:
        # Row number for the given phoneme
        index = np.where(db.iloc[:, 1] ==  pho)[0]

        # Handle the case the phoneme is not found in the dictionary
        if index.size <= 0:
            coeff = Series([0] * c)

        # Blendhsape coeffiecients for the given phoneme
        coeff = db.iloc[index, 2 : c].reset_index(drop = True)

        # Add coefficients to the dataframe
        artkit = concat([artkit, coeff], ignore_index = True)

    # Return the blendshape coefficients
    return artkit

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
                save_audio_stream(base64.b64decode(data["audio"]), "../../data/processed/tts-%s.mp3")
                yield base64.b64decode(data["audio"])
            elif data.get('isFinal'):
                break
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
            break
