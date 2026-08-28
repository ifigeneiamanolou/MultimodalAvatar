# 
#  Based on code from Orpheus-TTS
#  https://github.com/canopyai/Orpheus-TTS.git
#  
#  Original copyright © canopylabs.ai.
#  Licensed under the Apache License 2.0.
#  
#  Modified for MultimodalAvatar project.
#  

from snac import SNAC
import time
import numpy as np
import torch
import asyncio
import threading
import queue
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

model = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval()

snac_device = os.environ.get("SNAC_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
model = model.to(snac_device)

def convert_to_audio(multiframe, count):
    if len(multiframe) < 7:
        return None
    t0 = time.perf_counter()

    num_frames = len(multiframe) // 7
    frame = torch.tensor(
        multiframe[:num_frames * 7],
        device=snac_device,
        dtype=torch.int32
    ).view(num_frames, 7)

    codes_0 = frame[:, 0].contiguous()
    codes_1 = torch.stack([frame[:, 1], frame[:, 4]], dim=1).flatten()
    codes_2 = torch.stack([frame[:, 2], frame[:, 3], frame[:, 5], frame[:, 6]], dim=1).flatten()
    codes = [codes_0.unsqueeze(0), codes_1.unsqueeze(0), codes_2.unsqueeze(0)]

    if any(torch.any((c < 0) | (c > 4096)) for c in codes):
        return None

    torch.cuda.synchronize()
    t1 = time.perf_counter()

    with torch.inference_mode():
        audio_hat = model.decode(codes)
    torch.cuda.synchronize()
    t2 = time.perf_counter()

    audio_slice = audio_hat[:, :, 2048:4096]
    audio_int16 = (audio_slice.detach().cpu().numpy() * 32767).astype(np.int16)
    audio_bytes = audio_int16.tobytes()
    t3 = time.perf_counter()

    logger.info(f"tensor_build={t1-t0:.4f}s decode={t2-t1:.4f}s cpu_convert={t3-t2:.4f}s")
    return audio_bytes

def turn_token_into_id(token_string, index):
    # Strip whitespace
    token_string = token_string.strip()
    
    # Find the last token in the string
    last_token_start = token_string.rfind("<custom_token_")
    
    if last_token_start == -1:
        print("No token found in the string")
        return None
    
    # Extract the last token
    last_token = token_string[last_token_start:]
    
    # Process the last token
    if last_token.startswith("<custom_token_") and last_token.endswith(">"):
        try:
            number_str = last_token[14:-1]
            return int(number_str) - 10 - ((index % 7) * 4096)
        except ValueError:
            return None
    else:
        return None
  
    
async def tokens_decoder(token_gen):
    buffer = []
    count = 0
    async for token_sim in token_gen:       
        token = turn_token_into_id(token_sim, count)
        if token is None:
            pass
        else:
            if token > 0:
                buffer.append(token)
                count += 1

                if count % 7 == 0 and count > 27:
                    buffer_to_proc = buffer[-28:]
                    audio_samples = convert_to_audio(buffer_to_proc, count)
                    if audio_samples is not None:
                        yield audio_samples


# ------------------ Synchronous Tokens Decoder Wrapper ------------------ #
def tokens_decoder_sync(syn_token_gen):
    audio_queue = queue.Queue()

    # Convert the synchronous token generator into an async generator.
    async def async_token_gen():
        for token in syn_token_gen:
            yield token

    async def async_producer():
        num = 0
        # tokens_decoder.tokens_decoder is assumed to be an async generator that processes tokens.
        async for audio_chunk in tokens_decoder(async_token_gen()):
            if(num % 100 == 0):
                logger.info(f"putting chunk generated from the decoder with index {num} in decoder queue")
            num = num + 1
            audio_queue.put(audio_chunk)
        audio_queue.put(None)  # Sentinel

    def run_async():
        asyncio.run(async_producer())

    thread = threading.Thread(target=run_async)
    thread.start()

    numAudio = 0
    while True:
        audio = audio_queue.get()
        if audio is None:
            break
        if (numAudio % 100 == 0):
            logger.info(f"getting audio chunk {numAudio} from decoder queue consumer to stream to the backend")
        numAudio = numAudio + 1
        yield audio

    thread.join()
