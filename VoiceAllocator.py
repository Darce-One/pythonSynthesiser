from Generators import SinGen, SawGen, Phasor
from Envelopes import Ar, Adsr
from typing import List
import copy
import numpy as np

from singleKeyPress import midi_to_freq

class SynthVoice():
    def __init__(self):
        self.env = None
        self.gain = 0.0
        self.noteID = -1

    def __repr__(self) -> str:
        return f"Synth voice. noteID: {self.noteID}, stage: {self.env.stage}, released: {self.is_released}, done: {self.is_done}"

    def midi_to_freq(self, midi: int) -> float:
        return 440 * 2**((midi-69)/12)

    def get_noteID(self) -> int:
        return self.noteID

    def process_block(self, buffer: np.ndarray):
        for i in range(buffer.shape[0]):
            buffer[i] += self.process()

    def process(self) -> float:
        return 0.0

    def get_gain(self):
        return 0.0

    def is_done(self):
        return bool(False);

    def trigger(self, noteID):
        pass

    def release(self):
        pass

    def is_released(self):
        return bool(False)

class VoiceAllocator():
    def __init__(self) -> None:
        self.voices: List[SynthVoice] = []

    def add_voice(self, voice: SynthVoice):
        self.voices.append(voice)

    def _find_done_voice(self) -> int:
        for idx, voc in enumerate(self.voices):
            if voc.is_done():
                return idx
        # if no voices are done, returns -1
        return -1

    def _find_same_voice(self, noteID: int) -> int:
        for idx, voc in enumerate(self.voices):
            if noteID == voc.get_noteID():
                return idx
        # if no voices match, returns -1
        return -1

    def _find_quietest_voice(self) -> int:
        lowest_gain = 10.0
        lowest_gain_idx = -1
        for idx, voc in enumerate(self.voices):
            # Penalise unreleased voices by ading one to their gain.
            voc_gain = voc.get_gain() + int(not voc.is_released())
            if  voc_gain < lowest_gain:
                lowest_gain_idx = idx
                lowest_gain = voc.get_gain()
        if lowest_gain_idx == -1:
            raise SystemError("Error finding quietest voice.")
        return lowest_gain_idx

    def _voice_idx_to_steal(self, noteID: int) -> int:
        done_voc = self._find_done_voice()
        if done_voc != -1:
            return done_voc

        same_voc = self._find_same_voice(noteID)
        if same_voc != -1:
            return same_voc

        return self._find_quietest_voice()

    def trigger(self, noteID: int) -> None:
        # Find available voice:
        voc_id = self._voice_idx_to_steal(noteID)
        self.voices[voc_id].trigger(noteID)
        print(f"Triggered voice {voc_id}")

    def release(self, noteID: int) -> None:
        idx = 0
        for voc in self.voices:
            if voc.noteID == noteID and not voc.is_released():
                voc.release()
                print(F"Released voice {idx}")
            idx+=1

    def process_block(self, buffer: np.ndarray):
        for voc in self.voices:
            voc.process_block(buffer)

    def process(self) -> float:
        sample: float = 0.0
        for voc in self.voices:
            sample += voc.process()
        return sample
