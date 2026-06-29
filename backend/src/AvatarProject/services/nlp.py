from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from openai import OpenAI, RateLimitError, AsyncOpenAI
import os
from fastapi import HTTPException
import logging

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key = OPENAI_API_KEY)
clientAsync = AsyncOpenAI(api_key = OPENAI_API_KEY)

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
            stream = True,                          # Stream continuous output
            prompt_cache_retention = "24h",         # extended prompt cache retention  
        )
        return answer.output_text
    except RateLimitError as e:
        return "No API credit"
    except Exception as e:
        raise HTTPException(status_code = 500, detail = {e})
    
async def get_answer_stream(input : str, instructions : str) -> str:
    """ Stream the model's response as it is generated using Server-Sent Events(SSE)

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt

    Raises:
        HTTPException: if the response generation fails

    Returns:
        str: the bot response
    """

    try:
        # Generate OpenAI response
        response = await clientAsync.responses.create(
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
            stream = True,                          # Stream continuous output
            prompt_cache_retention = "24h",         # extended prompt cache retention 
        ) 
    
        # Continuously return the response to the frontend
        async def async_generator():
            async for event in response:
                if event.type == "response.output_text.delta":
                    text = event.delta
                if event.type == "response.completed":
                    total_tokens = event.response.usage.total_tokens
                    logging.info(f"Used tokens: {total_tokens}")
    
        return StreamingResponse(
            async_generator(),
            media_type = "text/event-stream",
        )
    except RateLimitError as e:
        return "No API credit"
    except Exception as e:
        raise HTTPException(
            detail = f"Error : {e}",
            status_code = 500,
        )
    