from pynput import keyboard
import multiprocessing

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
    while True:
        item = queue.get()
        if item == "END":
            break
        print(item)



if __name__ == "__main__":
    queue = multiprocessing.Queue()

    producer_process = multiprocessing.Process(target=producer, args=(queue,))
    consumer_process = multiprocessing.Process(target=consumer, args=(queue,))

    producer_process.start()
    consumer_process.start()

    producer_process.join()
    consumer_process.join()
