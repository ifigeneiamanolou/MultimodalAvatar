from dotenv import load_dotenv
from openai import OpenAI
import os
from server.utils.sentenceBuffer import sentenceBuffer
from server.utils.sseBuffer import sseBuffer
from server.utils.controller import controller as syncCoordinator
from server.services.fileServices import save_response
import requests
import re
import asyncio
import httpx
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

# Openai Client
http_client = httpx.AsyncClient()

async def get_answer_router_stream(input : list, instructions : str, emotion : str, model : str):
    """ Stream the model's streaming response through OpenRouter API through SSEs

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt
        emotion (str) : emotion label
        model (str) : model name to use for inference
    """
    # Singal UE5 to start a random filler
    await syncCoordinator.signal_filler()

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
    consumerTask = asyncio.create_task(syncCoordinator.consume())
    start = time.perf_counter()
    path = None         # Used to save the response from the LLM
    logger.info(f"Input to the LLM is {input}")
    try:
        index = 0
        async with http_client.stream(url = url, headers = headers, json = payload, method = "POST") as r:
            async for chunk in r.aiter_text(chunk_size = 1024):
                if index == 0:
                    logger.info(f"Time until first chunk from NLP : {time.perf_counter() - start} seconds")
                index = index + 1
                if(index != 0 and index % 10 == 0):
                    logger.info(f"Time until token number {index} is {time.perf_counter() - start} seconds")
                async for token in bufferSmall.flush_buffer(chunk): 
                    yield f"data: {token}\n\n"                         # Used in the frontend         
                    async for sentence in buffer.add(token):
                        await syncCoordinator.produce(sentence)        # Pass the sentence to the asyncio Queue       
                        path = save_response(path, sentence)    
                        logger.info(f"Time until sentence [{sentence}] from NLP : {time.perf_counter() - start}")

        async for sentence in buffer.flush():
            if(sentence):
                await syncCoordinator.produce(sentence)                 # Pass the remaining data to the Queue if they exist
                path = save_response(path, sentence)   
            await syncCoordinator.produce("[[DONE]]")  # Signal the end of the stream
            yield "data: [[DONE]]\n\n"                         # Signal to the frontend the end of SSE events
            logger.info(f"Full NLP response in {time.perf_counter() - start}")
    except Exception as e:
        logger.error(msg = f"Error during processing of NLP : {e}")
    finally:   
        await consumerTask                         # Await for the queue to finish consuming the sentences  

async def get_answer_router_stream_mobile(input : list, instructions : str, emotion : str, model : str):
    """ Stream the model's streaming response through OpenRouter API through SSEs

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt
        emotion (str) : emotion label
        model (str) : model name to use for inference
    """
    # Singal UE5 to start a random filler
    await syncCoordinator.signal_filler()

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
    consumerTask = asyncio.create_task(syncCoordinator.consume())
    start = time.perf_counter()
    path = None         # Used to save the response from the LLM
    response = ""
    try:
        index = 0
        async with http_client.stream(url = url, headers = headers, json = payload, method = "POST") as r:
            async for chunk in r.aiter_text(chunk_size = 1024):
                if index == 0:
                    logger.info(f"Time until first chunk from NLP : {time.perf_counter() - start} seconds")
                index = index + 1
                if(index != 0 and index % 10 == 0):
                    logger.info(f"Time until token number {index} is {time.perf_counter() - start} seconds")
                async for token in bufferSmall.flush_buffer(chunk):    
                    async for sentence in buffer.add(token):  
                        response += sentence                            # Accumulate tokens for frontend
                        path = save_response(path, sentence)            # Debugging logs
                        logger.info(f"Time until sentence {sentence} from NLP : {time.perf_counter() - start}")
                        await syncCoordinator.produce(sentence)        # Pass the sentence to the asyncio Queue

        async for sentence in buffer.flush():
            if(sentence):
                await syncCoordinator.produce(sentence)                 # Pass the remaining data to the Queue if they exist
                path = save_response(path, sentence)                    # Save the end of the response
        await syncCoordinator.produce("[[DONE]]")                       # Signal the end of the stream to UE5
        logger.info(f"Full NLP response in {time.perf_counter() - start}")
        return sentence                                                 # Return the sentence to the frontend
    except Exception as e:
        logger.error(msg = f"Error during processing of NLP : {e}")
    finally:   
        await consumerTask                         # Await for the queue to finish consuming the sentences  

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

    re.sub(r"\[EMOTION\]", emotion, instructions)


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