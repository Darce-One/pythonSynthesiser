import numpy as np
from typing import List
from Generators import SinGen, SawGen
from Filters import TwoPoleFilter
from Envelopes import Ar, Adsr


class AudioProcessor():
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate: int = sample_rate

    def prepare_to_play(self) -> None:
        # Code goes in here...
        pass

    def process_block(self, buffer: np.ndarray) -> None:
        for n in range(buffer.shape[0]):
            for c in range(buffer.shape[1]):
                buffer[n, c] += 0.0
