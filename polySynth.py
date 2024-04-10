# Stock Libraries
import time
import pyaudio
import numpy as np
import math
from typing import List
from pynput import keyboard
import multiprocessing
from multiprocessing.queues import Empty
from Generators import SinGen, SawGen
from Envelopes import Ar, Adsr
from VoiceAllocator import SynthVoice, VoiceAllocator

# Parameters for audio playback
SAMPLE_RATE = 44100
BLOCK_SIZE = 1024  # Number of frames per buffer

def midi_to_freq(midi: int) -> float:
    return 440 * 2**((midi-69)/12)

class Voice(SynthVoice):
    def __init__(self):
        super().__init__()

        self.sample_rate = SAMPLE_RATE
        self.gen = SawGen(self.sample_rate, 440)
        self.env = Adsr(self.sample_rate, 0.02, 0.2, 0.3, release_time=0.7)

    def process(self):
        return self.env.process_sample(self.gen.process())

    def get_gain(self):
        return self.env.get_gain()

    def trigger(self, noteID):
        self.noteID = noteID
        self.env.trigger()
        self.gen.set_new_frequency(midi_to_freq(noteID))

    def release(self):
        self.env.release()

    def is_released(self):
        # returns true if the envelope stage is the last one - in release phase
        return self.env.stage == self.env.phase_delta.size - 1

    def is_done(self) -> bool:
        return not self.env.triggered

class AudioProcessor():
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate: int = sample_rate
        self.key_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.key_listener.start()
        self.key_map = {"a": 60, "w": 61, "s": 62, "e": 63, "d": 64,
            "f": 65, "t": 66, "g": 67, "y": 68, "h": 69, "u": 70, "j": 71,
            "k": 72, "o": 73, "l": 74, "p": 75, ";": 76, "'": 77, "[": 78, "\\": 79}

    def on_press(self, key):
        try:
            self.va.trigger(self.key_map[key.char])
        except:
            pass

    def on_release(self, key):
        try:
            self.va.release(self.key_map[key.char])
        except:
            pass

    def prepare_to_play(self) -> None:
        self.va = VoiceAllocator()
        num_voices = 3
        for i in range(num_voices):
            voice = Voice()
            voice.env.set_release_skew(4)
            voice.env.set_attack_skew(2)
            self.va.add_voice(voice)

    def process_block(self, buffer: np.ndarray) -> None:
        self.va.process_block(buffer)

def main():
    # Get global variables (in case they are imported from another file)
    sample_rate: int = SAMPLE_RATE
    block_size: int = BLOCK_SIZE

    # instanciate the Audio Processor
    audio_processor = AudioProcessor(sample_rate)

    # instanciate objects within the Audio Processor
    audio_processor.prepare_to_play()

    # Function to process audio data in real-time
    def process_audio(in_data, frame_count, time_info, status):

        # Convert the input data to a numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        out = np.zeros_like(audio_data)[:, np.newaxis]

        # Attempt to listen for keyboard input without blocking
        audio_processor.process_block(out)


        # Convert the processed data back to bytes
        out_data = out.tobytes()

        return out_data, pyaudio.paContinue


    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open a stream with the specified callback function
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    frames_per_buffer=block_size,
                    input=True,
                    output=True,
                    stream_callback=process_audio)


    # Start the stream
    stream.start_stream()

    # Wait for the stream to finish (e.g., you can put your processing code in a loop)
    while stream.is_active():
        time.sleep(10)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate PyAudio
    p.terminate()

if __name__=="__main__":
    main()
