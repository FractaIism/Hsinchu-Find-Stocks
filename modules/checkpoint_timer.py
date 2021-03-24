from modules.libraries import *
from modules.utilities import logNprint

class Timer:
    def __init__(self):
        self.initial_time = None
        self.last_time = None

    def checkpoint(self, name: str):
        logNprint("*" * 50)
        logNprint(f"Checkpoint: {name}")
        if self.last_time is None:
            self.initial_time = self.last_time = time.time()
            logNprint(f"Time diff: 0.0")
            logNprint(f"Total time: 0.0")
        else:
            cur_time = time.time()
            logNprint(f"Time diff: {cur_time - self.last_time}")
            logNprint(f"Total time: {cur_time - self.initial_time}")
            self.last_time = cur_time
        logNprint("*" * 50)
