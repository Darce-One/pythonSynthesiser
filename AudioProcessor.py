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
        self.env = Ar(self.sample_rate, 0.2, 1.3, cycling=True)
        self.env.trigger()
        self.osc = SawGen(self.sample_rate, 440)
        self.fil = MoogVCFb(self.sample_rate, 880, 0.2)


    def process_block(self, buffer: np.ndarray) -> None:
        for n in range(buffer.shape[0]):
            for c in range(buffer.shape[1]):
                buffer[n, c] += 0.3 * self.fil.process_sample(self.env.process_sample(self.osc.process()))
