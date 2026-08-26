from dotenv import load_dotenv
import json
import os
import asyncio
from server.utils.controller import controller as syncCoordinator
from server.services.fileServices import save
import asyncio
import httpx
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
load_dotenv()
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

# Client for Openrouter requests
http_client = httpx.AsyncClient()

###########################################
# MOBILE
###########################################

async def text_mobile(input : list, instructions : str, model : str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    syncCoordinator.restart()

    # Signal to UE5 to start a filler
    syncCoordinator.signal_filler()

    # Format the input to the LLM
    input.append(
    {
        "role" : "developer",
        "content" : instructions
        }
    )

    # Format the payload
    payload = {
        "model": model,
        "messages": input,
        "modalities": ["text", "audio"],        # Defines the output format
        "audio": {
            "voice": "alloy",
            "format": "wav"
        },
        "stream": True
    }

    # Authorization headers
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Generate NLP response and emotion parameters
    consumerTask = asyncio.create_task(syncCoordinator.consume())
    start = time.perf_counter()
    transcript_chunks = []
    try:
        index = 0
        async with http_client.stream(url = url, headers = headers, json = payload, method = "POST") as r:
            async for line in r.iter_lines():
                # Debugging logs
                if index == 0:
                    logger.info(f"Time until first chunk from NLP : {time.perf_counter() - start} seconds")

                if(index != 0 and index % 10 == 0):
                    logger.info(f"Time until token number {index} is {time.perf_counter() - start} seconds")
                index = index + 1

                # Process the incoming line
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue
                data = line[len("data: "):]
                if data.strip() == "[DONE]":
                    break
                chunk = json.loads(data)
                delta = chunk["choices"][0].get("delta", {})
                audio = delta.get("audio", {})

                # Send the audio as a base64 string to UE5
                if audio.get("data"):
                    syncCoordinator.produce(audio["data"])

                # Append the text to a buffer
                if audio.get("transcript"):
                    transcript_chunks.append(audio["transcript"])

            # Signal to UE5 the end of audio
            syncCoordinator.produce("[[DONE]]")
    except Exception as e:
        logger.error(msg = f"Error during processing of NLP : {e}")
    finally:   
        await consumerTask              # Await for the queue to finish consuming the sentences  

    # Save the text response locally
    logger.info(f"Full NLP response in {time.perf_counter() - start}")
    transcript = "".join(transcript_chunks)
    save(transcript)

    # Return the response to the frontend
    return transcript
    
async def audio_mobile(input : list, instructions : str, model : str, audio : str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    syncCoordinator.restart()

    # Signal to UE5 to start a filler
    syncCoordinator.signal_filler()

    # Format the input to the LLM
    inputllm = input.append(
        {
            "type": "input_audio",
            "input_audio": {
                "data": audio,
                 # Change this depending on the format of the audio in the frontend
                "format": "wav"        
            }
        },
        {
            "role" : "developer",
            "content" : instructions
        }
    )

    # Format the payload
    payload = {
        "model": model,
        "messages": inputllm,
        "modalities": ["text", "audio"],        # Defines the output format
        "audio": {
            "voice": "alloy",
            "format": "wav"
        },
        "stream": True
    }

    # Authorization headers
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Generate NLP response and emotion parameters
    consumerTask = asyncio.create_task(syncCoordinator.consume())
    start = time.perf_counter()
    transcript_chunks = []
    try:
        index = 0
        async with http_client.stream(url = url, headers = headers, json = payload, method = "POST") as r:
            async for line in r.iter_lines():
                # Debugging logs
                if index == 0:
                    logger.info(f"Time until first chunk from NLP : {time.perf_counter() - start} seconds")

                if(index != 0 and index % 10 == 0):
                    logger.info(f"Time until token number {index} is {time.perf_counter() - start} seconds")
                index = index + 1

                # Process the incoming line
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue
                data = line[len("data: "):]
                if data.strip() == "[DONE]":
                    break
                chunk = json.loads(data)
                delta = chunk["choices"][0].get("delta", {})
                audio = delta.get("audio", {})

                # Send the audio as a base64 string to UE5
                if audio.get("data"):
                    syncCoordinator.produce(audio["data"])

                # Append the text to a buffer
                if audio.get("transcript"):
                    transcript_chunks.append(audio["transcript"])

            # Signal to UE5 the end of audio
            syncCoordinator.produce("[[DONE]]")
    except Exception as e:
        logger.error(msg = f"Error during processing of NLP : {e}")
    finally:   
        await consumerTask              # Await for the queue to finish consuming the sentences  

    # Save the text response locally
    logger.info(f"Full NLP response in {time.perf_counter() - start}")
    transcript = "".join(transcript_chunks)
    save(transcript)

    # Return the response to the frontend
    return transcript

###########################################
# WEB
###########################################

async def text_web(input : list, instructions : str, model : str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    syncCoordinator.restart()

    # Signal to UE5 to start a filler
    syncCoordinator.signal_filler()

    # Format the input to the LLM
    input.append(
    {
        "role" : "developer",
        "content" : instructions
        }
    )

    # Format the payload
    payload = {
        "model": model,
        "messages": input,
        "modalities": ["text", "audio"],        # Defines the output format
        "audio": {
            "voice": "alloy",
            "format": "wav"
        },
        "stream": True
    }

    # Authorization headers
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Generate NLP response and emotion parameters
    consumerTask = asyncio.create_task(syncCoordinator.consume())
    start = time.perf_counter()
    transcript_chunks = []
    try:
        index = 0
        async with http_client.stream(url = url, headers = headers, json = payload, method = "POST") as r:
            async for line in r.iter_lines():
                # Debugging logs
                if index == 0:
                    logger.info(f"Time until first chunk from NLP : {time.perf_counter() - start} seconds")

                if(index != 0 and index % 10 == 0):
                    logger.info(f"Time until token number {index} is {time.perf_counter() - start} seconds")
                index = index + 1

                # Process the incoming line
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue
                data = line[len("data: "):]
                if data.strip() == "[DONE]":
                    break
                chunk = json.loads(data)
                delta = chunk["choices"][0].get("delta", {})
                audio = delta.get("audio", {})

                # Send the audio as a base64 string to UE5
                if audio.get("data"):
                    syncCoordinator.produce(audio["data"])

                # Append the text to a buffer
                if audio.get("transcript"):
                    yield audio["transcript"]
                    transcript_chunks.append(audio["transcript"])

            # Signal to UE5 the end of audio
            syncCoordinator.produce("[[DONE]]")
    except Exception as e:
        logger.error(msg = f"Error during processing of NLP : {e}")
    finally:   
        await consumerTask              # Await for the queue to finish consuming the sentences  

    # Save the text response locally
    logger.info(f"Full NLP response in {time.perf_counter() - start}")
    transcript = "".join(transcript_chunks)
    save(transcript)

    # Return the response to the frontend
    return transcript
    
async def audio_web(input : list, instructions : str, model : str, audio : str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    syncCoordinator.restart()

    # Signal to UE5 to start a filler
    syncCoordinator.signal_filler()

    # Format the input to the LLM
    inputllm = input.append(
        {
            "type": "input_audio",
            "input_audio": {
                "data": audio,
                 # Change this depending on the format of the audio in the frontend
                "format": "wav"        
            }
        },
        {
            "role" : "developer",
            "content" : instructions
        }
    )

    # Format the payload
    payload = {
        "model": model,
        "messages": inputllm,
        "modalities": ["text", "audio"],        # Defines the output format
        "audio": {
            "voice": "alloy",
            "format": "wav"
        },
        "stream": True
    }

    # Authorization headers
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Generate NLP response and emotion parameters
    consumerTask = asyncio.create_task(syncCoordinator.consume())
    start = time.perf_counter()
    transcript_chunks = []
    try:
        index = 0
        async with http_client.stream(url = url, headers = headers, json = payload, method = "POST") as r:
            async for line in r.iter_lines():
                # Debugging logs
                if index == 0:
                    logger.info(f"Time until first chunk from NLP : {time.perf_counter() - start} seconds")

                if(index != 0 and index % 10 == 0):
                    logger.info(f"Time until token number {index} is {time.perf_counter() - start} seconds")
                index = index + 1

                # Process the incoming line
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue
                data = line[len("data: "):]
                if data.strip() == "[DONE]":
                    break
                chunk = json.loads(data)
                delta = chunk["choices"][0].get("delta", {})
                audio = delta.get("audio", {})

                # Send the audio as a base64 string to UE5
                if audio.get("data"):
                    syncCoordinator.produce(audio["data"])

                # Append the text to a buffer
                if audio.get("transcript"):
                    yield transcript
                    transcript_chunks.append(audio["transcript"])

            # Signal to UE5 the end of audio
            syncCoordinator.produce("[[DONE]]")
    except Exception as e:
        logger.error(msg = f"Error during processing of NLP : {e}")
    finally:   
        await consumerTask              # Await for the queue to finish consuming the sentences  

    # Save the text response locally
    logger.info(f"Full NLP response in {time.perf_counter() - start}")
    transcript = "".join(transcript_chunks)
    save(transcript)

    # Return the response to the frontend
    return transcript

