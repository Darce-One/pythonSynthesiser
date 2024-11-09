# Stock Libraries
import pyaudio
import numpy as np
import math
import time
from typing import List
from pynput import keyboard
import Generators as GEN
import Envelopes as ENV
import Filters as FIL
from pedalboard import Delay, Gain, Pedalboard, Phaser, Reverb

# Parameters for audio playback
SAMPLE_RATE = 44100
BLOCK_SIZE = 256  # Number of frames per buffer

class AudioProcessor():
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate: int = sample_rate

    def prepare_to_play(self) -> None:
        # Code goes in here...
        self.envs = [ENV.Ar(self.sample_rate, 0.1, 1.2, cycling=True), ENV.Ar(self.sample_rate, 0.1, 1.3, cycling=True)]
        for env in self.envs:
            env.trigger()
        self.oscs = [GEN.SawGen(self.sample_rate, 440), GEN.SawGen(self.sample_rate, 660)]
        self.fils = [FIL.MoogVCFb(self.sample_rate, 880, 0.2), FIL.MoogVCFb(self.sample_rate, 880, 0.2)]
        self.mod_osc = GEN.SinGen(self.sample_rate, 1)

        self.pedal_board = Pedalboard([Phaser(centre_frequency_hz=1300), Delay(delay_seconds=0.4, feedback=0.1)])


    def process_block(self, buffer: np.ndarray) -> None:
        for n in range(buffer.shape[0]):
            mod_osc = self.mod_osc.process()
            self.pedal_board[0].centre_frequency_hz = 1300 + (200*mod_osc)
            for c in range(buffer.shape[1]):
                buffer[n, c] += 0.3 * self.fils[c].process_sample(self.envs[c].process_sample(self.oscs[c].process()))
        processed_buffer = np.transpose(self.pedal_board(np.transpose(buffer), self.sample_rate, reset=False))
        buffer[:,:] = processed_buffer


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
        # audio_data = np.frombuffer(in_data, dtype=np.float32)
        # out = np.zeros_like(audio_data)[:, np.newaxis]
        out = np.zeros((frame_count, 2), dtype=np.float32)
        # print(out.shape)

        audio_processor.process_block(out)


        # Convert the processed data back to bytes
        out_data = out.tobytes()

        return out_data, pyaudio.paContinue

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open a stream with the specified callback function
    stream = p.open(format=pyaudio.paFloat32,
                    channels=2,
                    rate=sample_rate,
                    frames_per_buffer=block_size,
                    # input=True,
                    output=True,
                    stream_callback=process_audio)



    while stream.is_active():
        time.sleep(1)

    # Stop and close the stream
    stream.close()

    # Terminate PyAudio
    p.terminate()





if __name__=="__main__":
    main()
