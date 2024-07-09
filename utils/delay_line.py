import numpy as np
from config import MAX_DELAY

class DelayLine:
    def __init__(self, size=MAX_DELAY):
        self.size = size
        self.buffer = np.zeros(size)
        self.index = 0

    def push(self, value: float):
        self.buffer[self.index] = value
        self.index = (self.index + 1) % self.size

    def read(self, delay: int):
        assert delay < self.size, "Delay exceeds buffer size"
        read_index = (self.index - delay - 1) % self.size
        return self.buffer[read_index]