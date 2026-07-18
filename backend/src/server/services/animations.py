from pandas import DataFrame, read_csv, Series, concat
import numpy as np
from fastapi import HTTPException
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer.separator import Separator
from phonemizer.backend import EspeakBackend
import os

# Espeak configuration for phoneme detection
EspeakWrapper.set_library(
    r"C:/Program Files/eSpeak NG/libespeak-ng.dll"
)
backend = EspeakBackend(preserve_punctuation = True, 
                        language = "en-us")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   

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
