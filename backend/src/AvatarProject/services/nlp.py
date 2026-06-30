from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from openai import OpenAI, RateLimitError, AsyncOpenAI, APIError
import os
from src.AvatarProject.services.fileServices import save
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
    
async def get_answer_stream(input : str, instructions : str) -> StreamingResponse:
    """ Stream the model's response as it is generated using Server-Sent Events(SSE)

    Args:
        input (str): Input of the user
        instructions (str): Default instructions used in every prompt

    Raises:
        HTTPException: if the response generation fails

    Returns:
        StreamingResponse : continuous response of the LLM 
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
    except RateLimitError:
        raise HTTPException(status_code = 429, detail = "No API credit")
    
    # Continuously return the response to the frontend (10 tokens at a time)
    async def async_generator():
        full_text = ""
        partial_text = ""
        count = 0
        try:
            async for event in response:
                if event.type == "response.output_text.delta":
                    full_text += event.delta
                    partial_text += event.delta
                    count = count + 1

                    if(count == 10):
                        yield partial_text
                        count = 0
                        partial_text = ""
                if event.type == "response.completed":     
                    total_tokens = event.response.usage.total_tokens
                    logging.info(f"Used tokens: {total_tokens}")
        except (RateLimitError, APIError) as e:
            logging.error(f"OpenAI quota/API error mid-stream: {e}")
            yield "[[NO-CREDIT]]"
    
    return StreamingResponse(
        async_generator(),
        media_type = "text/event-stream",
    )
    