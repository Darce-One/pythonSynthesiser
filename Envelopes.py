import numpy as np
import numba
from numba.experimental import jitclass
from typing import List

@jitclass
class Adsr():
    sample_rate: numba.int32
    cycling: numba.int32
    stage: numba.int32
    phase: numba.float32
    phase_delta: numba.float32[:]
    skew_factors: numba.float32[:]
    triggered: numba.int32
    done: numba.int32
    attack_time: numba.float32
    release_time: numba.float32
    decay_time: numba.float32
    sustain: numba.float32
    resulting_sustain: numba.float32
    just_released: numba.int32


    def __init__(self, sample_rate: int, attack_time: float = 0.05, decay_time: float = 0.05,
        sustain: float = 1.0, release_time: float = 0.05) -> None:

        self.set_sustain_level(sustain)
        self.sample_rate = sample_rate
        self.stage: int = 0 # Stage of the ADSR: 0 for attack, 1 for decay, 2 for sustain, 3 for release.
        self.phase: float = 0.0
        self.phase_delta: np.ndarray[np.float32] = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        self.triggered: bool = False
        self.just_released: bool = False
        self.skew_factors: np.ndarray[np.float32] = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.set_attack_time(attack_time)
        self.set_decay_time(decay_time)
        self.set_release_time(release_time)


    def set_attack_time(self, attack_time) -> None:
        if attack_time < 0.0:
            raise ValueError("Attack time must be a positive float")
        self.attack_time: float = attack_time
        self._set_attack_phase_delta()

    def _set_attack_phase_delta(self) -> None:
        self.phase_delta[0] = 1 / (self.sample_rate * self.attack_time)

    def set_attack_skew(self, skew_factor:float) -> None:
        if skew_factor < 0.0:
            raise ValueError("Attack skew must be a positive real number")
        self.skew_factors[0] = skew_factor

    def set_decay_time(self, decay_time) -> None:
        if decay_time < 0.0:
            raise ValueError("Decay time must be a positive float")
        self.decay_time: float = decay_time
        self._set_decay_phase_delta()

    def _set_decay_phase_delta(self) -> None:
        self.phase_delta[1] = - (1 - self.sustain) / (self.sample_rate * self.decay_time)

    def set_decay_skew(self, skew_factor:float) -> None:
        if skew_factor < 0.0:
            raise ValueError("Decay skew must be a positive real number")
        self.skew_factors[1] = skew_factor

    def set_sustain_level(self, sustain_level: float):
        if sustain_level < 0.0 or sustain_level> 1.0:
            raise ValueError("Sustain level out of bounds")
        self.sustain = sustain_level
        self.resulting_sustain = sustain_level

    def set_release_time(self, release_time) -> None:
        if release_time < 0.0:
            raise ValueError("Release time must be a positive float")
        self.release_time: float = release_time
        self._set_release_phase_delta()

    def _set_release_phase_delta(self) -> None:
        self.phase_delta[3] = - self.resulting_sustain / (self.sample_rate * self.release_time)

    def set_release_skew(self, skew_factor:float) -> None:
        if skew_factor < 0.0:
            raise ValueError("Release skew must be a positive real number")
        self.skew_factors[3] = skew_factor

    def _trigger_release_phase(self) -> None:
        # self.just_released = False
        self.resulting_sustain = self.get_gain()
        self.phase = self.resulting_sustain
        self.stage = 3
        self._set_release_phase_delta()

    def trigger(self) -> None:
        self.triggered = True
        self.resulting_sustain = self.sustain
        self.stage = 0

    def release(self) -> None:
        # self.just_released = True
        self._trigger_release_phase()


    def _check_for_transition(self) -> None:
        # if self.just_released == True:
        #     self._trigger_release_phase()
        #     return

        if self.stage == 0:
            if self.phase >= 1.0:
                self.stage = 1
            else:
                return

        if self.stage == 1:
            if self.phase <= self.sustain:
                self.stage = 2
                self.sustain = self.phase
            else:
                return

        if self.stage == 3:
            if self.phase <= 0:
                self.stage = 0
                self.phase = 0
                self.triggered = False
            else:
                return

    def get_gain(self) -> float:
        if self.stage == 0:
            return self.phase**self.skew_factors[0]

        elif self.stage == 1:
            if self.sustain == 1.0:
                return 1.0
            def transform(p, sus):
                return ((p - sus)/(1 - sus))
            def inv_transform(trans, sus):
                return (trans * (1 - sus)) + sus
            return inv_transform(transform(self.phase, self.sustain)**self.skew_factors[1], self.sustain)

        elif self.stage == 2:
            return self.phase

        else:
            if self.sustain == 0.0:
                return 0.0
            def transform(p, sus):
                return p / sus
            def inv_transform(trans, sus):
                return trans * sus
            return inv_transform(transform(self.phase, self.sustain)**self.skew_factors[3], self.sustain)

    def process_sample(self, sample: float) -> float:
        if self.triggered == False:
            return 0.0
        else:
            gain = self.get_gain()
            self.phase += self.phase_delta[self.stage]
            self._check_for_transition()
            return sample * gain





class Ar():
    # For Numba Jitting
    sample_rate: numba.int32
    cycling: numba.int32
    stage: numba.int32
    phase: numba.float32
    phase_delta: numba.float32[:]
    skew_factor: numba.float32[:]
    triggered: numba.int32
    done: numba.int32
    attack_time: numba.float32
    release_time: numba.float32


    def __init__(self, sample_rate: int, attack_time: float, release_time: float, cycling: bool = False) -> None:
        self.sample_rate = sample_rate
        self.cycling = cycling
        self.stage: int = 0 # 0 for attack, 1 for release
        self.phase: float = 0.0
        self.phase_delta: np.ndarray[np.float32] = np.array([0.0, 0.0], dtype=np.float32)
        self.skew_factor: np.ndarray[np.float32] = np.array([1.0, 1.0], dtype=np.float32)
        self.triggered = False
        # self.done = False
        self.set_attack_time(attack_time)
        self.set_release_time(release_time)

    def set_attack_time(self, attack_time: float) -> None:
        self.attack_time = attack_time
        self.phase_delta[0] = 1 / (self.sample_rate * self.attack_time)

    def set_release_time(self, release_time:float) -> None:
        self.release_time = release_time
        self.phase_delta[1] = -1 / (self.sample_rate * self.release_time)

    def set_attack_skew(self, skew_factor: float) -> None:
        if skew_factor < 0.0:
            raise ValueError("Attack Skew must be a positive real number")
        self.skew_factor[0] = skew_factor

    def set_release_skew(self, skew_factor: float) -> None:
        if skew_factor < 0.0:
            raise ValueError("Release Skew must be a positive real number")
        self.skew_factor[1] = skew_factor

    def trigger(self) -> None:
        self.triggered = True
        # self.done = False
        self.stage = 0

    def release(self) -> None:
        # do nothing
        pass

    def _check_for_transition(self) -> None:
        if self.stage == 0:
            if self.phase >= 1.0:
                self.stage = 1
            else:
                return

        if self.stage == 1:
            if self.phase <= 0:
                if self.cycling == True:
                    self.stage = 0
                else:
                    # self.done = True
                    self.triggered = False
            else:
                return
    def get_gain(self):
        return self.phase**self.skew_factor[self.stage]

    def process_sample(self, sample):
        # if self.done == True:
        #     return 0.0
        if self.triggered == False:
            return 0.0
        else:
            gain = self.get_gain()
            self.phase += self.phase_delta[self.stage]
            self._check_for_transition()
            return sample * gain
