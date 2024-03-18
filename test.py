# Stock Libraries
import pyaudio
import numpy as np
import math
from typing import List

# Project Libraries
from AudioProcessor import AudioProcessor

# Parameters for audio playback
SAMPLE_RATE = 44100
BLOCK_SIZE = 1024  # Number of frames per buffer







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

        audio_processor.process_block(out)


        # Your signal processing code goes here


        # Convert the processed data back to bytes
        # out_data = np.array(processed_audio, dtype=np.float32)
        #
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
        pass

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate PyAudio
    p.terminate()




if __name__=="__main__":
    main()
