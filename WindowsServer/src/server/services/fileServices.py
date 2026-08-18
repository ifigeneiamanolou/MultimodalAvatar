import os
import numpy as np
import torchaudio
import logging

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

def save_emotion2vec(scores : np.ndarray, emotion : str):
    """ Saves locally the results of emotion2vec inference

    Args:
        scores (np.ndarray): the emotion scores for the emotions angry, disgusted, fearful, happy, sad, surprised
        and neutral
        emotion (str): the emotion label with the maximum score
    """
    labels = ['angry', 'disgusted', 'fearful', 'happy', 'sad', 'surprised', 'neutral']

    # Create directory if needed
    path = next_path(os.path.join(BASE_DIR, "../../../data/processed/emotion2vec-%s.txt"))
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Write inference results
    with open(path, "w") as f:
        f.write("Explicit scores : \n\n")

        # Write emotion scores
        for i, score in enumerate(scores):
            f.write(f"{labels[i]} : {score} \n")

        # Write final prediction
        f.write(f"Final prediction is : {emotion}")

def save_distilbert(sentence : str, emotion : str, maxProb : float, result : dict):
    """ Saves locally the results of distilbert inference

    Args:
        sentence (str): the sentence for which inference was performed
        emotion (str): the emotion label with the maximum score
        maxProb (float): maximum score from distilbert
        result (dict): dictionary with keys the labels needed for Audio2Face and values their scores after mapping
    """
    # Create directory if needed
    path = next_path(os.path.join(BASE_DIR, "../../../data/processed/distilbert-%s.txt"))
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Write inference results
    with open(path, "w") as f:
        # Write emotion scores
        f.write("Explicit scores : \n\n")

        for emotion in result.keys():
            score = result[emotion]
            f.write(f"{emotion} : {score} /n")

        # Write final predictions
        f.write(f"Final prediction for {sentence} is {emotion} with probability {maxProb}")

def read_audio(path):
    path = os.path.join(BASE_DIR, path)
    waveform, sr = torchaudio.load(path)
    return waveform, sr

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
        
def start_logging():
    """ Configure the file to store runtime logs for the server
    """
    # Logging path
    LOG_PATH = os.path.abspath(
        os.path.join(BASE_DIR, next_path("../../../data/processed/logRuntime-%s.log"))
    )
    
    # Check if 10 logging files are already present
    MAX_PATH = os.path.join(BASE_DIR, "../../../data/processed/logRuntime-11.log")
    if(str(LOG_PATH) == MAX_PATH):
        # Updated log file path
        LOG_PATH = os.path.abspath(
            os.path.join(BASE_DIR, "../../../data/processed/logRuntime-1.log")
        )
        
        # Remove old logging files
        for i in range(1, 11):
            os.remove(os.path.join(BASE_DIR, f"../../../data/processed/logRuntime-{i}.log"))
            
    # Create a directory to store runtime logs
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=LOG_PATH,
        force=True
    )
        
