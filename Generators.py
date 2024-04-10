from typing import List
import math
import numpy as np

class Phasor():
    def __init__(self, sample_rate: int, frequency: float) -> None:
        self.frequency: float = frequency
        self.sample_rate: int = sample_rate
        self.phase: float = 0.0
        self.phase_delta: float = frequency / sample_rate
        self.gain = 1

    def set_new_frequency(self, new_frequency) -> None:
        self.frequency = new_frequency
        self._update_phase_delta()

    def _update_phase_delta(self) -> None:
        self.phase_delta = self.frequency / self.sample_rate

    def _update_phase(self) -> None:
        self.phase += self.phase_delta
        if self.phase > 1.0:
            self.phase -= 1.0


    def set_gain(self, new_gain) -> None:
        self.gain = new_gain


    def process_block(self, buffer: np.ndarray):
        for i in range(buffer.shape[0]):
            buffer[i] += self.process()

    def process(self) -> float:
        sample = self.phase * self.gain
        self._update_phase()
        return sample



class SinGen(Phasor):
    def __init__(self, sample_rate: int, frequency: float, gain: float = 1.0) -> None:
        super().__init__(sample_rate, frequency)
        self.gain = gain

    def process(self) -> float:
        sample = math.sin(self.phase * 2 * math.pi) * self.gain
        self._update_phase()
        return sample

class SawGen(Phasor):
    def __init__(self, sample_rate: int, frequency: float, gain: float = 1.0) -> None:
        super().__init__(sample_rate, frequency)
        self.gain = gain

    def process(self) -> float:
        sample = (2 * self.phase - 1) * self.gain
        self._update_phase()
        return sample
