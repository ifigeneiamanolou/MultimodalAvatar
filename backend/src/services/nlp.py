from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from openai import OpenAI, RateLimitError, AsyncOpenAI, APIError
import os
from src.services.fileServices import save
from fastapi import HTTPException
import logging
from openrouter import OpenRouter
import requests

# Environment variables
load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]

def get_answer(input : str, instructions : str) -> str:
    """ Generates a response using gpt-4o-mini through OpenAI API

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt

    Raises:
        HTTPException: if the response generation fails

    Returns:
        str: the bot response
    """

    client = OpenAI(api_key = OPENAI_API_KEY)
    
    try:
        answer = client.responses.create(
            model="gpt-4o-mini",                   # To change during production
            instructions = instructions,
            input = [
                {
                    "role" : "user",
                    "content" : input
                },
                {
                    "role" : "developer",
                    "content" : instructions
                }
            ],
            prompt_cache_retention = "24h",         # extended prompt cache retention  
        )
        return answer.output_text
    except RateLimitError as e:
        return "No API credit"
    except Exception as e:
        raise HTTPException(status_code = 500, detail = {e})
    
async def get_answer_stream(input : str, instructions : str) -> StreamingResponse:
    """ Stream the model's response through OpenAI API as it is generated using Server-Sent Events(SSE)

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt

    Raises:
        HTTPException: if the response generation fails

    Returns:
        StreamingResponse : continuous response of the LLM 
    """

    

async def get_answer_deepseek(input : str, instructions : str) -> str:
    """ Stream the model's response from DeepSeek v3.2

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt

    Raises:
        HTTPException: if the response generation fails

    Returns:
        str : response of the LLM 
    """
    client = OpenAI(api_key = DEEPSEEK_API_KEY,  base_url = "https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {
                "role" : "user",
                "content" : input
            },
            {
                "role" : "developer",
                "content" : instructions
            }
        ],
        stream = False,
    )

    return response.choices[0].message.content

def get_answer_router(input : str, instructions : str) -> str:
    """ Stream the model's response through OpenRouter API (gpt-4o-mini)

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt

    Raises:
        HTTPException: if the response generation fails

    Returns:
        str : response of the LLM 
    """
    try:
        with OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY", ""),) as client:
            response = client.chat.send(
                model="openai/gpt-4o-mini",
                messages=[
                    {
                        "role" : "user",
                        "content" : input
                    },
                    {
                        "role" : "developer",
                        "content" : instructions
                    }
                ]
            )
        return response.choices[0].message.content
    except RateLimitError as e:
        return "[[NO-CREDIT]]"
    except Exception as e:
        raise HTTPException(status_code = 500, detail = {e})
    
def get_answer_router_stream(input : str, instructions : str) -> StreamingResponse:
    """ Stream the model's streaming response through OpenRouter API through SSEs

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt

    Raises:
        HTTPException: if the response generation fails

    Returns:
        StreamingResponse : continuous response of the LLM 
    """
