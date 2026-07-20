import os
import json
from scipy.io.wavfile import write
import numpy as np
import tempfile
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   

def next_path(path_pattern : str) -> str:
    """ Finds the next path available using binary search

    Args:
        path_pattern (str): the general pattern of the file

    Returns:
        str: the next available path found based on the pattern
    """
    i = 1
    while os.path.exists(path_pattern % i):
        i = i * 2
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

    return path_pattern % b

def saveFeedback(messages : dict, path : str):
    """ Writes the content of a dictionary into a file in utf-8 encoding, with indentation

    Args:
        messages (dict): dictionary to write to a file
        path (str): location of the target file
    """

    path = next_path(os.path.join(BASE_DIR, path))

    with open(path, "w", encoding = "utf-8") as json_file:
        json.dump(messages, json_file, indent = 4, )

def save_stream(input : str, path : str):
    """ Append the input text to the next available path in the specified location avoiding overwriting

    Args:
        input (str): input text
        path (str): relative path to the current directory to save the audio
    """

    path = next_path(os.path.join(BASE_DIR, path))

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "a") as f:      # Avoid overwriting
        f.write(input)

def save_audio_stream(audio_bytes : bytes, path : str):
    """ Write audio encoded in base64 as an mp3 file

    Args:
        audio_bytes (bytes): base64 encoded bytes
        path (str): file path to save the audio
    """

    path = next_path(os.path.join(BASE_DIR, path))

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "ab") as f:     # Avoid overwriting
        f.write(audio_bytes)

def save_audio(audio_bytes : bytes, path : str):
    """ Saves the input audio bytes to the next available path in the specified location

    Args:
        audio_bytes (bytes): input audio bytes 
        path (str): relative path to the current directory to save the audio

    Returns:
        path (str) : absolute path where audio was saved
    """

    path = next_path(os.path.join(BASE_DIR, path))
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(audio_bytes)

    return path

def save(input : str, path : str):
    """ Saves the input text to the next available path in the specified location

    Args:
        input (str): input text
        path (str): relative path to the current directory to save the audio
    """

    path = next_path(os.path.join(BASE_DIR, path))

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write(input)

def save_wav(buffer : list, path : str):
    """ Saves input audio into a wav file using scipy

    Args:
        buffer (list): list containing the audio chunks
        path (str): relative path to save the audio produced
    """
    new_path = next_path(os.path.join(BASE_DIR, path))
    write(new_path, 24_000, np.concatenate(buffer))