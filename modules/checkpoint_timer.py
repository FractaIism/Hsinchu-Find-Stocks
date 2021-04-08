from modules.libraries import *
from modules.utilities import logNprint

@dataclass
class Timer:
    initial_time: float = None
    last_time: float = None

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
