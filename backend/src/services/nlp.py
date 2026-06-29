from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
import os
from fastapi import HTTPException

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key = OPENAI_API_KEY)

def get_answer(input : str, instructions : str) -> str:
    """ Generates a response using gpt-4o-mini

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt

    Raises:
        HTTPException: if the response generation fails

    Returns:
        str: the bot response
    """
    
    try:
        answer = client.responses.create(
            model="gpt-4o-mini",                   # To change during production
            instructions = instructions,
            input = [
                {
                    "role" : "user",
                    "content" : [
                        {
                            "type": "input_text",
                            "text": input
                        }
                    ]
                }
            ],
            prompt_cache_retention = "24h",         # extended prompt cache retention  
        )
        return answer.output_text
    except RateLimitError as e:
        return "No API credit"
    except Exception as e:
        raise HTTPException(status_code = 500, detail = {e})