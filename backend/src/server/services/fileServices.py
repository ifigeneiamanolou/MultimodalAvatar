import os
import json
import json
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


def saveJSON(messages : dict, path : str):
    """ Writes the content of a dictionary into a file in utf-8 encoding, with indentation

    Args:
        messages (dict): dictionary to write to a file
        path (str): location of the target file
    """

    path = next_path(os.path.join(BASE_DIR, path))

    with open(path, "w", encoding = "utf-8") as json_file:
        json.dump(messages, json_file, indent = 4)

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

def load_template(template : str = ["feedback1", "feedback2", "emotions", "interview1", "interview2"]):
    """ Reads a template needed for prompt engineering

    Args:
        template (str) : name of template file in local storage
    """
    template_path = os.path.join(BASE_DIR, f"../../../data/templates/{template}.md")         # Bot : interviewee
    with open(template_path , "r") as f:
        prompt = f.read()
    return prompt

def save_response(path : str | None, response : str):
    """_summary_

    Args:
        path (str | None): _description_
        response (str): _description_

    Returns:
        _type_: _description_
    """
    # Checks if a new file needs to be opened
    if path is None:
        path = os.path.join(BASE_DIR, next_path("../../../data/raw/response-%s.txt"))

    with open(path, "a") as f:
        f.write(response)
    return path

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
        
