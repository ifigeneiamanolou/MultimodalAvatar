import os
import wave
import logging

# Base directory
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

def save_audio(buffer : bytearray):
    """ Save the result from orpheus3b locally

    Args:
        buffer (bytearray): Orpheus3B output
    """
    path = os.path.join(BASE_DIR, next_path("../../../data/raw/output-%s.wav"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(buffer)


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
    if(os.path.samefile(str(LOG_PATH), str(MAX_PATH))):
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
        
