from Generators import SinGen, SawGen, Phasor
from Envelopes import Ar, Adsr
from typing import List
import copy
import numpy as np

from singleKeyPress import midi_to_freq

class SynthVoice():
    def __init__(self, generator: Phasor, envelope, gain: float):
        self.gen = generator
        self.env = envelope
        self.gain = gain
        self.noteID = -1

    def __repr__(self) -> str:
        return f"Synth voice. noteID: {self.noteID}, stage: {self.env.stage}, released: {self.is_released}, done: {self.is_done}"

    def midi_to_freq(self, midi: int) -> float:
        return 440 * 2**((midi-69)/12)

    def get_noteID(self) -> int:
        return self.noteID

    def get_gain(self) -> float:
        return self.env.get_gain()

    def process(self) -> float:
        return self.gain * self.env.process_sample(self.gen.process())

    def trigger(self, noteID: int) -> None:
        self.noteID = noteID
        self.env.trigger()
        self.gen.set_new_frequency(midi_to_freq(noteID))

    def release(self) ->None:
        try:
            self.env.release()
        except:
            pass

    def is_released(self) -> bool:
        # returns true if the envelope stage is the last one - in release phase
        return self.env.stage == self.env.phase_delta.size - 1

    def is_done(self) -> bool:
        return not self.env.triggered

    def set_attack_time(self, attack_time) -> None:
        self.env.set_attack_time(attack_time)

    def set_attack_skew(self, attack_skew) -> None:
        self.env.set_attack_skew(attack_skew)

    def set_decay_time(self, decay_time) -> None:
        try:
            self.env.set_attack_time(decay_time)
        except:
            pass

    def set_decay_skew(self, decay_skew) -> None:
        try:
            self.env.set_attack_skew(decay_skew)
        except:
            pass

    def set_release_time(self, release_time) -> None:
        self.env.set_attack_time(release_time)

    def set_release_skew(self, release_skew) -> None:
        self.env.set_attack_skew(release_skew)



class VoiceAllocator():
    def __init__(self, synth_voice: SynthVoice, num_voices: int = 3) -> None:
        self.num_voices: int = num_voices
        self.voices: List[SynthVoice] = self._make_voice_array(synth_voice)

    def _make_voice_array(self, synth_voice) -> List[SynthVoice]:
        voices: List[SynthVoice] = []
        for i in range(self.num_voices):
            voices.append(copy.deepcopy(synth_voice))
        return voices

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

    def process(self) -> float:
        sample: float = 0.0
        for voc in self.voices:
            sample += voc.process()
        return sample





def test():
    sample_rate = 44100
    gen = SinGen(sample_rate, 440)
    env = Adsr(sample_rate)
    vo = SynthVoice(gen, env, 0.1)
    va = VoiceAllocator(vo)
    # del gen, env

    # va.voices[0].trigger(200)
    # va.voices[2].trigger(300)
    #
    va.trigger(60)
    va.trigger(61)


    for voc in va.voices:
        print(voc.is_done())


if __name__ == "__main__":
    test()
