from fastapi import Request
import json

class sentenceBuffer:
    def __init__(self):
        self.buffer = ""                                # Buffer for full sentences
        self.sentence_ends = [".", "!", ":", ";", "?"]
        self.maximum_length = 200                       # Maximum length before a sentence is buffered
        self.minimum_length = 10

    def full_sentence(self) -> bool:
        """ Checks if the sentence buffer has generated a full sentence or a maximum length is exceeded """
        return (any(self.sentence.endswith(end) for end in self.sentence_ends) and len(self.sentence) >= self.minimum_length) or len(self.sentence) >= self.maximum_length
    
    async def add(self, text):
        """ Adds incoming text to the buffer and returns a sentence if a condition is reached """
        self.buffer += text

        if(self.full_sentence()):
            sentence = self.buffer
            self.buffer = "" 
            yield sentence

    async def flush(self):
        """ Return the remaining text from the buffer even if the conditions are not met"""
        if self.buffer:     # if the buffer is not empty
            sentence = self.buffer
            self.buffer = "" 
            yield sentence


        

    




  
    