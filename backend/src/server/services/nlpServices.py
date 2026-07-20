from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
import os
from server.services.fileServices import save_stream
from server.utils.sentenceBuffer import sentenceBuffer
from server.utils.sseBuffer import sseBuffer
from server.utils.controller import Controller
from fastapi import HTTPException
import logging
import requests
import re
import asyncio
import httpx

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

    re.sub(r"[EMOTION]", emotion, instructions)


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
    input = input_processing(input, instructions, emotion, "system")

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
        "stream": True
    }

    buffer = sentenceBuffer()
    bufferSmall = sseBuffer()
    syncCoordinator = Controller()
    consumerTask = asyncio.create_task(syncCoordinator.consume())
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(url = url, headers = headers, json = payload, method = "POST") as r:
                async for chunk in r.aiter_text(chunk_size = 1024):
                    async for token in bufferSmall.flush_buffer(chunk): 
                        yield f"data: {token}\n\n"                  
                        async for sentence in buffer.add(token):           
                            await syncCoordinator.produce(sentence)        # Pass the sentence to the Queue

        async for sentence in buffer.flush():
            await syncCoordinator.produce(sentence)   # Pass the remaining data to the Queue
            await syncCoordinator.produce(None)                         # Singal end of input
    except Exception as e:
        print(f"error {str(e)} \n")
    finally:
        await consumerTask
            
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

        async for event in answer:
            if event.type == "response.output_text.delta":
                text = event.delta
                content = f"data: {text}\n\n"
                save_stream(content, "../../../data/raw/response-%s.txt")
                yield content

            if event.type == "response.completed":
                # Output the number of tokens used
                total_tokens = event.response.usage.total_tokens
                logging.info(f"Used tokens: {total_tokens}")

    except RateLimitError as e:
        yield "No API credit"
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