"""
    Maintains a dictionary of active audio-emotion tuples that need to be passed to the UE5 application with pixel streaming 
    configured as well the id of the next sentence to be processed.

"""

from controller import SyncedChunk

class dispatcher:
    def __init__(self):
        self.pending = {}
        self.next_id = 0
    
    def submit(self, chunk : SyncedChunk):
        # Submit the sentence to the dictionary
        if chunk[]

        # Check if a task is already running

        # If yes, wait

        # If not, forward to UN5 for pixel streaming