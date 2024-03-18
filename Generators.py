from typing import List
import numpy as np
import math

class SinGen():
    def __init__(self, frequency: float, gain: float, sample_rate: int) -> None:
        self.frequency: float = frequency
        self.sample_rate: int = sample_rate
        self.phase: float = 0.0
        self.phase_delta: float = frequency / sample_rate
        self.gain = gain

    def set_new_frequency(self, new_frequency) -> None:
        self.frequency = new_frequency
        self._update_phase_delta()

    def _update_phase_delta(self) -> None:
        self.phase_delta = self.frequency / self.sample_rate


    def process(self) -> float:
        sample = math.sin(self.phase * 2 * np.pi) * self.gain
        self.phase += self.phase_delta
        if self.phase > 1.0:
            self.phase -= 1.0
        return sample
