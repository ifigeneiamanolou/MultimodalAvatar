import asyncio
import requests

class Controller:
    def __init__(self):
        self.queue = asyncio.Queue(maxsize = 50)


    async def consume(self):
        while True:
            sentence = await self.queue.get()

            if sentence is None:
                self.queue.task_done()
                break

            try:
                # Perform some task
                async with asyncio.TaskGroup() as task_group:
                    emotionTask = task_group.create_task(self.produce_emotions(sentence))
                    audioTask = task_group.create_task(self.produce_audio(sentence))
            finally:   
                self.queue.task_done()


    async def produce(self, data : str):
        await self.queue.put(data)

    async def produce_emotions(sentence : str):
        # Call to LLM for emotions
        pass

    async def produce_audio(sentence : str):
        # Call FASTAPI on remote server using requests
        pass