# Stock Libraries
import numpy as np
import soundfile as sf
import math
from typing import List

# Project Libraries
from AudioProcessor import AudioProcessor

# PROJECT SETTINGS:
SAMPLE_RATE: int = 44100
TIME_IN_SECONDS: float = 5.0
BLOCK_SIZE: int = 256


def main():
    # Get global variables (in case they are imported from another file)
    sample_rate: int = SAMPLE_RATE
    time_in_seconds: float = TIME_IN_SECONDS
    block_size: int = BLOCK_SIZE

    # Calculate derived variables
    time_in_samples: int = math.ceil(time_in_seconds * sample_rate)
    time_in_blocks: int = math.ceil(time_in_samples / block_size)

    # instanciate the Audio Processor
    audio_processor = AudioProcessor(sample_rate, block_size)

    # create offline audio buffer
    out: List[List[float]] = [[], []]

    # instanciate objects within the Audio Processor
    audio_processor.prepare_to_play()

    # Process each block individually
    for i in range(time_in_blocks):
        audio_processor.process_block()
        out[0] = audio_processor.get_left_channel()
        out[1] = audio_processor.get_right_channel()

    # export the audio clip
    out_as_array = np.array(out, dtype=np.float32).transpose()
    sf.write("out.wav", out_as_array, sample_rate, subtype="FLOAT")




if __name__=="__main__":
    main()
