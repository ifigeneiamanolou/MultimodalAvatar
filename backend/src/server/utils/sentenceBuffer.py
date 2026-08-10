class sentenceBuffer:
    """ Custom buffer to extract full sentences from the NLP response once a punctuation mark or maximum length is
        reached
    """
    def __init__(self):
        self.buffer = ""                                # Buffer for full sentences
        self.sentence_ends = [".", "!", ":", ";", "?"]
        self.maximum_length = 200                       # Maximum length before a sentence is buffered
        self.minimum_length = 10

    def full_sentence(self) -> bool:
        """ Checks if the sentence buffer has generated a full sentence or a maximum length is exceeded

        Returns:
            bool: indicates whether a full sentence has been accumulated
        """
        return (any(self.buffer.endswith(end) for end in self.sentence_ends) and len(self.buffer) >= self.minimum_length) or len(self.buffer) >= self.maximum_length
    
    async def add(self, text : str):
        """ Adds incoming text to the buffer and returns a sentence if a condition is reached 

        Args:
            text (str): the token from the SSE buffer

        Yields:
            str: the accumulated sentence
        """

        self.buffer += text

        if(self.full_sentence()):
            sentence = self.buffer
            self.buffer = "" 
            yield sentence           

    async def flush(self):
        """ Return the remaining text from the buffer even if the conditions are not met

        Yields:
            str: the remaining contents in the buffer
        """
        
        if self.buffer:     # if the buffer is not empty
            sentence = self.buffer
            self.buffer = "" 
            yield sentence


        

    




  
    