# Stock Libraries
import numpy as np
from Envelopes import Adsr
import soundfile as sf
import math
from typing import List
import matplotlib.pyplot as plt

# PROJECT SETTINGS:
SAMPLE_RATE: int = 44100
TIME_IN_SECONDS: float = 10
BLOCK_SIZE: int = 256
NUM_CHANNELS: int = 1

class AudioProcessor():
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate: int = sample_rate

    def prepare_to_play(self) -> None:
        self.env = Adsr(self.sample_rate, 0.2, 2, 0.2, 3)
        self.env.set_attack_skew(3)
        self.env.set_decay_skew(2)
        self.env.set_release_skew(3)
        self.env.trigger()

    def process_block(self, buffer: np.ndarray) -> None:
        for i in range(buffer.shape[0]):
            for c in range(buffer.shape[1]):
                buffer[i,c] += self.env.process_sample(1)




def main():
    # Get global variables (in case they are imported from another file)
    sample_rate: int = SAMPLE_RATE
    time_in_seconds: float = TIME_IN_SECONDS
    block_size: int = BLOCK_SIZE
    num_channels = NUM_CHANNELS

    # Calculate derived variables
    time_in_samples: int = math.ceil(time_in_seconds * sample_rate)
    time_in_blocks: int = math.ceil(time_in_samples / block_size)
    num_samples:int = time_in_blocks * block_size

    # instanciate the Audio Processor
    audio_processor = AudioProcessor(sample_rate)

    # initialise offline audio buffer
    out = np.zeros((num_samples, num_channels), dtype=np.float32)

    # instanciate objects within the Audio Processor
    audio_processor.prepare_to_play()

    # Process each block individually
    for i in range(time_in_blocks):
        audio_processor.process_block(out[(i*block_size):((i+1)*block_size), :])
        if i == 300:
            audio_processor.env.release()

    plt.plot(out)
    plt.show()
    # # export the audio clip
    # sf.write("out.wav", out, sample_rate, subtype="FLOAT")




if __name__=="__main__":
    main()
