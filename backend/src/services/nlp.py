from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from openai import OpenAI, RateLimitError, AsyncOpenAI, APIError
import os
from src.services.fileServices import save_stream
from fastapi import HTTPException
import logging
from openrouter import OpenRouter
import requests
import json

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

def get_answer_router(input : list, instructions : str) -> str:
    """ Stream the model's response through OpenRouter API (gpt-4o-mini)

    Args:
        input (list): Input of the user
        instructions (str): Default instructions used in every prompt

    Returns:
        str : response of the LLM 
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {os.getenv("OPENROUTER_API_KEY")}",
        "Content-Type": "application/json"
    }

    input.append(
        {
            "role" : "developer",
            "content" : instructions
        }
    )

    payload = {
        "model": "openai/gpt-4o",
        "messages": input,
        "stream": False
    }

    with requests.post(url, headers=headers, json=payload, stream=True) as response:
        return response.choices[0].message.content
    
def get_answer_router_stream(input : list, instructions : str):
    """ Stream the model's streaming response through OpenRouter API through SSEs

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {os.getenv("OPENROUTER_API_KEY")}",
        "Content-Type": "application/json"
    }

    input.append(
        {
            "role" : "developer",
            "content" : instructions
        }
    )

    payload = {
        "model": "openai/gpt-4o",
        "messages": input,
        "stream": False
    }

    buffer = ""
    with requests.post(url, headers=headers, json=payload, stream=True) as r:
        for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
            buffer += chunk
            while True:
                try:
                    # Find the next complete SSE line
                    line_end = buffer.find('\n')
                    if line_end == -1:
                        break

                    line = buffer[:line_end].strip()
                    buffer = buffer[line_end + 1:]

                    if line.startswith('data: '):
                        data = line[6:]
                    if data == '[DONE]':
                        break

                    try:
                        data_obj = json.loads(data)
                        content = data_obj["choices"][0]["delta"].get("content")
                        if content:
                            # Save the data for logging
                            save_stream(content, "../../data/raw/response-%s.txt")
                            # Return the data 
                            yield content
                    except json.JSONDecodeError:
                        pass
                except Exception:
                    break