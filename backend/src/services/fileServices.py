import os
import json
from scipy.io.wavfile import write
import numpy as np

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
    """ Writes the content of a dictionary into a file

    Args:
        messages (dict): dictionary to write to a file
        path (str): location of the target file
    """

    path = next_path(os.path.join(BASE_DIR, path))

    with open(path, "w", encoding = "utf-8") as json_file:
            json.dump(messages, json_file, indent = 4)

def saveAudio(audio_bytes : bytes, path : str):
    """ Saves the input audio bytes to the next available path in the specified location

    Args:
        audio_bytes (bytes): input audio bytes from MediaRecorder API
        path (str): relative path to the current directory to save the audio
    """

    path = next_path(os.path.join(BASE_DIR, path))

    with open(path, "wb") as f:
        f.write(audio_bytes)

def save(input : str, path : str):
    """ Saves the input text to the next available path in the specified location

    Args:
        input (str): input audio bytes from MediaRecorder API
        path (str): relative path to the current directory to save the audio
    """

    path = next_path(os.path.join(BASE_DIR, path))

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
