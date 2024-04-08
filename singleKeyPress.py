# Stock Libraries
import pyaudio
import numpy as np
import math
from typing import List
from pynput import keyboard
import multiprocessing
from multiprocessing.queues import Empty
from Generators import SinGen, SawGen
from Envelopes import Ar, Adsr

# Parameters for audio playback
SAMPLE_RATE = 44100
BLOCK_SIZE = 1024  # Number of frames per buffer

def midi_to_freq(midi: int) -> float:
    return 440 * 2**((midi-69)/12)

class AudioProcessor():
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate: int = sample_rate

    def prepare_to_play(self) -> None:
        self.sin_gens = SinGen(self.sample_rate, 440, 0.1)
        self.envelopes = Adsr(self.sample_rate, 2, 0.2, 0.2, 1.4)
        self.envelopes.set_attack_skew(2)
        self.envelopes.set_decay_skew(0.7)
        self.envelopes.set_release_skew(4)
        self.envelopes.trigger()

    def process_block(self, buffer: np.ndarray) -> None:
        for i in range(buffer.shape[0]):
                buffer[i] += self.envelopes.process_sample(self.sin_gens.process())




def on_press(queue, key):
    try:
        # Try to get the character of the key pressed
        queue.put(f"Pressed: {key.char}")
    except AttributeError:
        # Special keys (like space, enter, etc.) do not have a char attribute
        queue.put(f"Pressed: {str(key)}")

    # Stop listener if 'Esc' key is pressed
    if key == keyboard.Key.esc:
        queue.put("END")
        return False  # Return False to stop the listener

def on_release(queue, key):
    try:
        # Send message indicating the key was released
        queue.put(f"Released: {key.char}")
    except AttributeError:
        # For special keys
        queue.put(f"Released: {str(key)}")

def producer(queue):
    # Setup the listener to monitor keyboard input
    with keyboard.Listener(
            on_press=lambda event: on_press(queue, event),
            on_release=lambda event: on_release(queue, event)) as listener:
        listener.join()

def consumer(queue):
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
        while True:
            try:
                item = queue.get_nowait()
                if item == "Pressed: a":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(60))
                    audio_processor.envelopes.trigger()

                if item[:5] == "Relea":
                    audio_processor.envelopes.release()

                if item == "Pressed: s":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(62))
                    audio_processor.envelopes.trigger()

                if item == "Pressed: d":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(64))
                    audio_processor.envelopes.trigger()

                if item == "Pressed: f":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(65))
                    audio_processor.envelopes.trigger()

                if item == "Pressed: g":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(67))
                    audio_processor.envelopes.trigger()

                if item == "Pressed: h":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(69))
                    audio_processor.envelopes.trigger()

                if item == "Pressed: j":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(71))
                    audio_processor.envelopes.trigger()

                if item == "Pressed: k":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(72))
                    audio_processor.envelopes.trigger()

                if item == "Pressed: l":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(74))
                    audio_processor.envelopes.trigger()

                if item == "Pressed: ;":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(76))
                    audio_processor.envelopes.trigger()

                if item == "Pressed: '":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(77))
                    audio_processor.envelopes.trigger()

                if item == "Pressed: \\":
                    audio_processor.sin_gens.set_new_frequency(midi_to_freq(79))
                    audio_processor.envelopes.trigger()


                if item == "END":
                    exit()
                print(item)
                # Process the item here as needed before affecting the audio output
                # For example, modify 'out' based on the item
            except Empty:
                # If the queue is empty, just continue and process the audio as usual
                break



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
        pass

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate PyAudio
    p.terminate()


def main():

    queue = multiprocessing.Queue()

    producer_process = multiprocessing.Process(target=producer, args=(queue,))
    consumer_process = multiprocessing.Process(target=consumer, args=(queue,))





    producer_process.start()
    consumer_process.start()

    producer_process.join()
    consumer_process.join()




if __name__=="__main__":
    main()
