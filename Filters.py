import math
from typing import List
import numpy as np
from numpy.linalg import inv


class TwoPoleFilter():
    def __init__(self, cutoff: float, resonance: float, sample_rate: int, safety=0.9) -> None:
        self.cutoff: float = cutoff
        self.safety = safety
        self.sample_rate: int = sample_rate
        self.yn_1: float = 0.0
        self.yn_2: float = 0.0
        self.a_1 = 0.0
        self.a_2 = 0.0
        self.resonance = 0.0
        self._set_resonance(resonance)
        self._calculate_theta_c()
        self._calculate_a_1()
        self._calculate_a_2()

    def _set_resonance(self, res: float) -> None:
        if self.safety is not None:
            self.resonance = np.maximum(0.05, np.minimum(res, self.safety))
        else:
            self.resonance = res

    def _calculate_theta_c(self) -> None:
        self.theta_c: float = 2 * math.pi * self.cutoff / self.sample_rate

    def _calculate_a_1(self) -> None:
        self.a_1 = -2 * self.resonance * math.cos(self.theta_c)

    def _calculate_a_2(self) -> None:
        self.a_2 = self.resonance * self.resonance

    def set_new_cutoff(self, new_cutoff) -> None:
        self.cutoff: float = new_cutoff
        self._calculate_theta_c()
        self._calculate_a_1()
        self._calculate_a_2()

    def set_new_resonance(self, new_res) -> None:
        self._set_resonance(new_res)
        self._calculate_a_2()

    def process_sample(self, sample: float) -> float :
        out_sample = sample + (self.a_1 * self.yn_1) + (self.a_2 * self.yn_2)
        self.yn_2 = self.yn_1
        self.yn_1 = out_sample
        return out_sample

    def process_buffer(self, buffer: np.ndarray):
        if len(buffer.shape) != 2:
            raise BufferError("Ensure that the buffer coming in has two dimensions")

        if buffer.shape[1] > 1:
            print("WARNING: filter only processing first channel!")

        for i in range(len(buffer)):
            buffer[i] = self.process_sample(buffer[i])

class MoogVCFb():
    def __init__(self, sample_rate: int, cutoff: float, resonance: float):
        self.sample_rate = sample_rate
        self._k = 1 / sample_rate
        self._eye = np.eye(4)
        self._set_resonance(resonance)
        self.set_cutoff(cutoff)
        self._b = self._w0 * np.array([1, 0, 0, 0]).reshape(4,1)
        self._c = np.array([0, 0, 0, 1]).reshape(1,4)
        self._x = np.array([0, 0, 0, 0]).reshape(4,1)

    def _update_A(self):
        self._Ay = self._w0 * np.array([[-1, 0, 0, -4*self._r], [1, -1, 0, 0], [0, 1, -1, 0], [0, 0, 1, -1]])
        self._update_intermediary_matrices()

    def _update_intermediary_matrices(self):
        self._Bee = self._eye - (self._k*self._Ay)
        self._B_inv = inv(self._Bee)

    def set_cutoff(self, cutoff: float):
        self._f0 = cutoff
        self._w0 = 2 * math.pi * self._f0
        self._update_A()

    def set_resonance(self, resonance: float):
        if resonance < 0 or resonance > 0.99:
            raise ValueError("Resonance must be a float between 0 - 0.99")
        self._r = resonance
        self._update_A()

    def _set_resonance(self, resonance: float):
        if resonance < 0 or resonance >= 0.99:
            raise ValueError("Resonance must be a float between 0 - 0.99")
        self._r = resonance

    def process_sample(self, sample: float):
        self._x = self._B_inv @ (self._x + (self._k * self._b * sample))

        # self._x = np.linalg.solve(self._B, self._x + self._k*self._b*sample)
        return (self._c @ self._x)[0,0]



if __name__=="__main__":
    sample_rate = 44100
    f0 = 600
    r = 0.2
    k = 1/sample_rate
    w0 = 2 * math.pi * f0

    A = w0 * np.array([[-1, 0, 0, -4*r], [1, -1, 0, 0], [0, 1, -1, 0], [0, 0, 1, -1]])
    B = np.eye(4) - k*A
    B_inv = inv(B)

    b = w0 * np.array([1, 0, 0, 0]).reshape(4,1)
    c = np.array([0, 0, 0, 1]).reshape(1,4)
    x = np.array([0.0, 0.0, 0.0, 0.0]).reshape(4,1)

    new_x = B_inv @ (x + (k * b * 0.2))
    outsample = (c @ new_x)[0,0]

    print(f"A shape = {A.shape}")
    print(f"B shape = {B.shape}")
    print(f"B_inv shape = {B_inv.shape}")
    print(F"x shape = {x.shape}")
    print(f"new_x shape = {new_x.shape}")
    print(f"out shape = {outsample.shape}")
