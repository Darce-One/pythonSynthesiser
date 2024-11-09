import numpy as np
from typing import List
from Generators import SinGen, SawGen
from Filters import TwoPoleFilter, MoogVCFb
from Envelopes import Ar, Adsr


class AudioProcessor():
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate: int = sample_rate

    def prepare_to_play(self) -> None:
        # Code goes in here...
        self.envs = [Ar(self.sample_rate, 0.2, 1.3, cycling=True), Ar(self.sample_rate, 0.2, 1.4, cycling=True)]
        for env in self.envs:
            env.trigger()
        self.oscs = [SawGen(self.sample_rate, 440), SawGen(self.sample_rate, 660)]
        self.fils = [MoogVCFb(self.sample_rate, 880, 0.2), MoogVCFb(self.sample_rate, 880, 0.2)]


    def process_block(self, buffer: np.ndarray) -> None:
        for n in range(buffer.shape[0]):
            for c in range(buffer.shape[1]):
                buffer[n, c] += 0.3 * self.fils[c].process_sample(self.envs[c].process_sample(self.oscs[c].process()))
