from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from matplotlib import text
from openai import OpenAI, RateLimitError, AsyncOpenAI, APIError
import os
from backend.src.routes import response
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
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

def input_processing(input : list, instructions : str, emotion : str, role : str) -> list:
    """ Preprocess the user input to include emotion detected and instructions

    Args:
        input (list): Conversation between the avatar and the LLM
        instructions (str): developer instructions
        emotion (str): detected emotion label
        role (str) : sting used to denote system instructions
    Returns:
        list: processed input to the LLM
    """
    # Emotion integration
    input[len(input) - 1] = {
        "role" : "user",
        "content" : {
            "text" : input[len(input) - 1]["content"],
            "emotion" : emotion
        }
    }

    # Developer instructions to the input
    input.append(
        {
            "role" : role,
            "content" : instructions
        }
    )

    return input

async def get_answer_router(input : list, instructions : str, emotion : str, model : str) -> str:
    """ Stream the model's response through OpenRouter API (gpt-4o-mini)

    Args:
        input (list): Input of the user
        instructions (str): Default instructions used in every prompt
        emotion (str) : emotion label
        model (str) : model name to use for inference

    Returns:
        str : response of the LLM 
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    # Authorization headers for OpenRouter API
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Input processing
    input = input_processing(input, instructions, emotion, "developer")

    # Request payload
    payload = {
        "model": model,
        "messages": input,
        "stream": False
    }

    with requests.post(url, headers = headers, json = payload, stream=True) as response:
        return response.choices[0].message.content
    
async def get_answer_router_stream(input : list, instructions : str, emotion : str, model : str):
    """ Stream the model's streaming response through OpenRouter API through SSEs

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt
        emotion (str) : emotion label
        model (str) : model name to use for inference
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    # Authorization headers for OpenRouter API
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Input processing
    input = input_processing(input, instructions, emotion, "developer")

    # Request payload
    payload = {
        "model": model,
        "messages": input,
        "stream": False
    }

    buffer = ""
    with requests.post(url, headers=headers, json=payload, stream=True) as r:
        for chunk in r.iter_content(chunk_size = 1024, decode_unicode=True):
            buffer += chunk     # Append the chunk produced to the buffer
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

async def get_answer(input : list, instructions : str, emotion : str, model : str) -> str:
    """ Generates a response using OpenAI API

    Args:
        input (list): List of messages between the LLM and the user
        instructions (str): Default instructions used in every prompt
        emotion (str) : emotion label
        model (str) : model name to use for inference

    Raises:
        HTTPException: if the response generation fails

    Returns:
        str: the bot response
    """

    client = OpenAI(api_key = OPENAI_API_KEY)

    # Input processing
    input = input_processing(input, instructions, emotion, "developer")
    
    try:
        answer = await client.responses.create(
            model = model,                 
            instructions = instructions,
            input = input,
            prompt_cache_retention = "24h",         # extended prompt cache retention  
        )
        return answer.output_text.content[0].text
    except RateLimitError as e:
        return "No API credit"
    except Exception as e:
        raise HTTPException(status_code = 500, detail = {e})
    
async def get_answer_stream(input : str, instructions : str, emotion : str, model : str):
    """ Stream the model's response through OpenAI API using Server-Sent Events(SSE)

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt
        emotion (str) : emotion label
        model (str) : model name to use for inference

    Raises:
        HTTPException: if the response generation fails
    """

    client = OpenAI(api_key = OPENAI_API_KEY)

    # Input processing
    input = input_processing(input, instructions, emotion, "developer")
    
    try:
        answer = await client.responses.create(
            model = model,                 
            instructions = instructions,
            input = input,
            prompt_cache_retention = "24h",         # extended prompt cache retention  
            stream = True,
        )
        
        content = ""
        async for event in answer:
            if event.type == "response.output_text.delta":
                text = event.delta
                content += text
                yield f"data: {text}\n\n"
                
            if event.type == "response.completed":
                # Output the number of tokens produced
                total_tokens = event.response.usage.total_tokens
                logging.info(f"Used tokens: {total_tokens}")
                # Save the bot response 
                save_stream(content, "../../data/raw/response-%s.txt")

    except RateLimitError as e:
        return "No API credit"
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

async def get_answer_deepseek(input : str, instructions : str, emotion : str, model : str) -> str:
    """ Return the model's response using DeepSeek API (deepseek-v4-flash as default) with CoT completion

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt
        emotion (str) : emotion label
        model (str) : model name to use for inference

    Raises:
        HTTPException: if the response generation fails

    Returns:
        str : response of the LLM 
    """
    client = OpenAI(api_key = DEEPSEEK_API_KEY,  base_url = "https://api.deepseek.com")

    # Input processing
    input = input_processing(input, instructions, emotion, "system")

    response = await client.chat.completions.create(
        model = model,
        messages = input,
        stream = False,
        reasoning_effort = "high",
        extra_body = {"thinking": {"type": "enabled"}}      # Chain-of-thought reasoning
    )

    return response.choices[0].message.content