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
from VoiceAllocator import SynthVoice, VoiceAllocator

# Parameters for audio playback
SAMPLE_RATE = 44100
BLOCK_SIZE = 1024  # Number of frames per buffer

def midi_to_freq(midi: int) -> float:
    return 440 * 2**((midi-69)/12)

class AudioProcessor():
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate: int = sample_rate

    def prepare_to_play(self) -> None:
        self.gen = SinGen(self.sample_rate, 440)
        self.env = Adsr(self.sample_rate, 0.02, 0.2, 0.3, release_time=0.7)
        self.vo = SynthVoice(self.gen, self.env, 0.2)
        self.vo.set_release_skew(4)
        self.vo.set_attack_skew(2)
        self.va = VoiceAllocator(self.vo, num_voices=12)

    def process_block(self, buffer: np.ndarray) -> None:
        for i in range(buffer.shape[0]):
                buffer[i] += self.va.process()




def on_press(queue, key):
    try:
        # Try to get the character of the key pressed
        queue.put(f"Pressed: {key.char}")
    except AttributeError:
        # Special keys (like space, enter, etc.) do not have a char attribute
        # queue.put(f"Pressed: {str(key)}")
        pass

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
                if item[0] == "P":
                    match item[-1]:
                        case "a":
                            audio_processor.va.trigger(60)

                        case "w":
                            audio_processor.va.trigger(61)

                        case "s":
                            audio_processor.va.trigger(62)

                        case "e":
                            audio_processor.va.trigger(63)

                        case "d":
                            audio_processor.va.trigger(64)

                        case "f":
                            audio_processor.va.trigger(65)

                        case "t":
                            audio_processor.va.trigger(66)

                        case "g":
                            audio_processor.va.trigger(67)

                        case "y":
                            audio_processor.va.trigger(68)

                        case "h":
                            audio_processor.va.trigger(69)

                        case "u":
                            audio_processor.va.trigger(70)

                        case "j":
                            audio_processor.va.trigger(71)

                        case "k":
                            audio_processor.va.trigger(72)

                        case "o":
                            audio_processor.va.trigger(73)

                        case "l":
                            audio_processor.va.trigger(74)

                        case "p":
                            audio_processor.va.trigger(75)

                        case ";":
                            audio_processor.va.trigger(76)

                        case "'":
                            audio_processor.va.trigger(77)

                        case "]":
                            audio_processor.va.trigger(78)

                        case "\\":
                            audio_processor.va.trigger(79)

                elif item[0] == "R":
                    match item[-1]:
                        case "a":
                            audio_processor.va.release(60)

                        case "w":
                            audio_processor.va.release(61)

                        case "s":
                            audio_processor.va.release(62)

                        case "e":
                            audio_processor.va.release(63)

                        case "d":
                            audio_processor.va.release(64)

                        case "f":
                            audio_processor.va.release(65)

                        case "t":
                            audio_processor.va.release(66)

                        case "g":
                            audio_processor.va.release(67)

                        case "y":
                            audio_processor.va.release(68)

                        case "h":
                            audio_processor.va.release(69)

                        case "u":
                            audio_processor.va.release(70)

                        case "j":
                            audio_processor.va.release(71)

                        case "k":
                            audio_processor.va.release(72)

                        case "o":
                            audio_processor.va.release(73)

                        case "l":
                            audio_processor.va.release(74)

                        case "p":
                            audio_processor.va.release(75)

                        case ";":
                            audio_processor.va.release(76)

                        case "'":
                            audio_processor.va.release(77)

                        case "]":
                            audio_processor.va.release(78)

                        case "\\":
                            audio_processor.va.release(79)


                if item == "END":
                    exit()
                # print(item)
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
