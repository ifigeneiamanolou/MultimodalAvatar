import os
import numpy as np
import torchaudio
import logging
import soundfile as sf

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

def save_audio(audio_bytes : bytes):
    """ Saves the input audio bytes locally

    Args:
        audio_bytes (bytes): input audio bytes 

    Returns:
        path (str) : absolute path where audio was saved
    """

    # Data path
    DATA_PATH = os.path.abspath(
        os.path.join(BASE_DIR, next_path("../../../data/raw/audio-%s.webm"))
    )
    
    # Check if 10 logging files are already present
    MAX_PATH = os.path.abspath(
        os.path.join(BASE_DIR, "../../../data/raw/audio-11.webm")
    )
    if(str(DATA_PATH) == str(MAX_PATH)):
        # Updated data file path
        DATA_PATH = os.path.abspath(
            os.path.join(BASE_DIR, "../../../data/raw/audio-1.webm")
        )
        
        # Remove old logging files
        for i in range(1, 11):
            os.remove(os.path.join(BASE_DIR, f"../../../data/raw/audio-{i}.webm"))
            
    # Create a directory to store output from orpheus3b
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    with open(DATA_PATH, "wb") as f:
        f.write(audio_bytes)

    return DATA_PATH

def save_tts_result(audio : list):
    # Data path
    DATA_PATH = os.path.abspath(
        os.path.join(BASE_DIR, next_path("../../../data/processed/tts-%s.wav"))
    )
    
    # Check if 10 logging files are already present
    MAX_PATH = os.path.abspath(
        os.path.join(BASE_DIR, "../../../data/processed/tts-11.wav")
    )
    if(str(DATA_PATH) == str(MAX_PATH)):
        # Updated data file path
        DATA_PATH = os.path.abspath(
            os.path.join(BASE_DIR, "../../../data/processed/tts-1.wav")
        )
        
        # Remove old logging files
        for i in range(1, 11):
            os.path.remove(os.path.join(BASE_DIR, f"../../../data/processed/tts-{i}.wav"))
            
    # Create a directory to store output from kokoro
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    
    if audio:
        data = np.concatenate(audio)
        sf.write(DATA_PATH, data, 24000)

def save_emotion2vec(scores : np.ndarray, emotion : str):
    """ Saves locally the results of emotion2vec inference

    Args:
        scores (np.ndarray): the emotion scores for the emotions angry, disgusted, fearful, happy, sad, surprised
        and neutral
        emotion (str): the emotion label with the maximum score
    """
    labels = ['angry', 'disgusted', 'fearful', 'happy', 'sad', 'surprised', 'neutral']

    # Data path
    DATA_PATH = os.path.abspath(
        os.path.join(BASE_DIR, next_path("../../../data/processed/emotion2vec-%s.txt"))
    )
    
    # Check if 10 logging files are already present
    MAX_PATH = os.path.abspath(
        os.path.join(BASE_DIR, "../../../data/processed/emotion2vec-11.txt")
    )
    if(str(DATA_PATH) == str(MAX_PATH)):
        # Updated data file path
        DATA_PATH = os.path.abspath(
            os.path.join(BASE_DIR, "../../../data/processed/emotion2vec-1.txt")
        )
        
        # Remove old logging files
        for i in range(1, 11):
            os.path.remove(os.path.join(BASE_DIR, f"../../../data/processed/emotion2vec-{i}.txt"))
            
    # Create a directory to store output from orpheus3b
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    # Write inference results
    with open(DATA_PATH, "w") as f:
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
    # Data path
    DATA_PATH = os.path.abspath(
        os.path.join(BASE_DIR, next_path("../../../data/processed/distilbert-%s.txt"))
    )
    
    # Check if 10 logging files are already present
    MAX_PATH = os.path.abspath(
        os.path.join(BASE_DIR, "../../../data/processed/distilbert-11.txt")
    )
    if(str(DATA_PATH) == str(MAX_PATH)):
        # Updated data file path
        DATA_PATH = os.path.abspath(
            os.path.join(BASE_DIR, "../../../data/processed/distilbert-1.txt")
        )
        
        # Remove old logging files
        for i in range(1, 11):
            os.remove(os.path.join(BASE_DIR, f"../../../data/processed/distilbert-{i}.txt"))
            
    # Create a directory to store output from orpheus3b
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    # Write inference results
    with open(DATA_PATH, "w") as f:
        # Write emotion scores
        f.write("Explicit scores : \n\n")

        for emotion in result.keys():
            score = result[emotion]
            f.write(f"{emotion} : {score} /n")

        # Write final predictions
        f.write(f"Final prediction for {sentence} is {emotion} with probability {maxProb}")

def read_audio(path):
    """ Read audio from given location using torchaudio

    Args:
        path (str): relative path to the current location

    Returns:
        bytes, int: the audio bytes, the sample rate of the bytes
    """
    path = os.path.join(BASE_DIR, path)
    waveform, sr = torchaudio.load(path)
    return waveform, sr

def save(input : str):
    """ Saves the input text to the next available path (Used to store Whisper transcriptions)

    Args:
        input (str): input text
    """
    # Data path
    DATA_PATH = os.path.abspath(
        os.path.join(BASE_DIR, next_path("../../../data/processed/transcription-%s.txt"))
    )
    
    # Check if 10 logging files are already present
    MAX_PATH = os.path.abspath(
        os.path.join(BASE_DIR, "../../../data/processed/transcription-11.txt")
    )
    if(str(DATA_PATH) == str(MAX_PATH)):
        # Updated data file path
        DATA_PATH = os.path.abspath(
            os.path.join(BASE_DIR, "../../../data/processed/trasncription-1.txt")
        )
        
        # Remove old logging files
        for i in range(1, 11):
            os.remove(os.path.join(BASE_DIR, f"../../../data/processed/transcription-{i}.txt"))
            
    # Create a directory to store output from orpheus3b
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    with open(DATA_PATH, "w") as f:
        f.write(input)
        
def start_logging():
    """ Configure the file to store runtime logs for the server
    """
    # Logging path
    LOG_PATH = os.path.abspath(
        os.path.join(BASE_DIR, next_path("../../../data/processed/logRuntime-%s.log"))
    )
    
    # Check if 10 logging files are already present
    MAX_PATH = os.path.abspath(
        os.path.join(BASE_DIR, "../../../data/processed/logRuntime-11.log")
    )
    if(str(LOG_PATH) == str(MAX_PATH)):
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
        
