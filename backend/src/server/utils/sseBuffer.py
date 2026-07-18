from fastapi import Request
import json

class sseBuffer:
    def __init__(self):
        self.buffer = ""                                # Buffer for SSE events data

    async def flush_buffer(self, chunk):                       # Async generator
        self.buffer += chunk
        """ Extracts SSE events fron the response buffer and yields sentences as a generator """
        while True:
            try:
                # Find the next complete SSE line
                line_end = self.buffer.find('\n')
                if line_end == -1:
                    break

                # Extract the full SSE line
                line = self.buffer[:line_end].strip()

                # Remove the processed line from the buffer
                self.buffer = self.buffer[line_end + 1:]      

                if line.startswith('data: '):
                    data = line[6:]
                if data == '[DONE]':
                    return None

                try:
                    data_obj = json.loads(data)
                    content = data_obj["choices"][0]["delta"].get("content")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue
            except Exception:
                break