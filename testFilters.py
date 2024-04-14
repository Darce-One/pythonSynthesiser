import numpy as np
from typing import List
import math
import matplotlib.pyplot as plt
from numpy.fft import fft
import soundfile as sf
from copy import deepcopy
from Generators import SinGen, SawGen
from Filters import TwoPoleFilter, MoogVCFb
from Envelopes import Ar, Adsr


# PROJECT SETTINGS:
SAMPLE_RATE: int = 44100
TIME_IN_SECONDS: float = 0.2
BLOCK_SIZE: int = 256
NUM_CHANNELS: int = 1


class AudioProcessor():
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate: int = sample_rate

    def prepare_to_play(self) -> None:
        self.vcf = MoogVCFb(self.sample_rate, 700, 0.5)



    def process_block(self, buffer: np.ndarray) -> None:
        for n in range(buffer.shape[0]):
            for c in range(buffer.shape[1]):
                buffer[n, c] = self.vcf.process_sample(buffer[n, c]) * 0.1




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
    # out = (np.random.rand(num_samples, num_channels).astype(np.float32) * 2 - 1)
    out = np.zeros((num_samples, num_channels), dtype=np.float32)

    comparison = deepcopy(out)

    # Make it a Kronecker delta
    out[2] = 1.0

    # Time vector
    tvec = np.linspace(0, num_samples-1, num_samples)/sample_rate

    # Frequency vector
    fvec = np.linspace(0, num_samples-1, num_samples) * sample_rate / num_samples

    # instanciate objects within the Audio Processor
    audio_processor.prepare_to_play()

    # Process each block individually
    for i in range(time_in_blocks):
        audio_processor.process_block(out[(i*block_size):((i+1)*block_size), :])

    # sf.write("out.wav", out, sample_rate, subtype="FLOAT")

    out_FFT = abs(fft(out))

    plt.loglog(fvec, out_FFT)
    plt.xlim((20, 20000))
    # plt.plot(tvec, out)
    plt.show()


if __name__=="__main__":
    main()
