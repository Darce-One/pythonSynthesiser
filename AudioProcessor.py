from typing import List
from Generators import SinGen
import numpy as np

class AudioProcessor():
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate: int = sample_rate

    def prepare_to_play(self) -> None:
        self.sin_gens = [SinGen(440, 0.1, self.sample_rate), SinGen(441.5, 0.1, self.sample_rate)]

    def process_block(self, buffer: np.ndarray) -> None:
        for i in range(buffer.shape[0]):
            for c in range(buffer.shape[1]):
                buffer[i,c] += self.sin_gens[c].process()
