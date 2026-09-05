import re

class sentenceBuffer:
    """ Custom buffer to extract full sentences from the NLP response once a punctuation mark or maximum length is
        reached
    """
    def __init__(self):
        self.buffer = ""                                # Buffer for full sentences
        self.maximum_length = 200                       # Maximum length before a sentence is buffered
        self.minimum_length = 10

    async def add(self, text : str):
        """ Adds incoming text to the buffer and returns a sentence if a condition is reached 

        Args:
            text (str): the token from the SSE buffer

        Yields:
            str: the accumulated sentence
        """

        self.buffer += text
        while True:
            # Find a match to the given pattern
            match = re.search(r'(?<=[.!?;:])(?:\s|$)', self.buffer)

            # If a match is found send it to the controller
            if match:
                end = match.start() + 1
                sentence = self.buffer[:end].strip()

                # Safety limit for small sentences
                if(len(sentence) < self.minimum_length):
                    break

                # Remove from the buffer
                self.buffer = self.buffer[end:].lstrip()
                yield sentence        
                continue

            # Safety limit for long sentences
            if(len(self.buffer) > self.maximum_length):
                sentence = self.buffer[:self.maximum_length]      
                self.buffer = self.buffer[self.maximum_length:]

                if sentence:
                    yield sentence.strip()   
                continue
            break 

    async def flush(self):
        """ Return the remaining text from the buffer even if the conditions are not met

        Yields:
            str: the remaining contents in the buffer
        """
        
        if self.buffer.strip():     # if the buffer is not empty
            sentence = self.buffer.strip()
            self.buffer = "" 
            yield sentence


        

    




  
    