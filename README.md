# The Python Synthesiser

This project is a simplified recreation of the JUCE plugin processor, to make prototyping plugins ideas easier. So far, the files are created for offline use.

The project settings can be found in `main.py`. These include `SAMPLE_RATE`, `BLOCK_SIZE`, and `TIME_IN_SECONDS`.

The audio processing happens in the `AudioProcessor` class, found in `AudioProcessor.py`.

# Env setup

`conda create -n pythonSynthesiser`

`conda activate pythonSynthesiser`

`conda install python=3.10 numpy=1.26.4`

`conda install conda-forge::librosa`

`conda install matplotlib`

`python3 -m pip install pyaudio --global-option="build_ext" --global-option="-I/opt/homebrew/include" --global-option="-L/opt/homebrew/lib"`

# Poly Synth

run `python polySynth.py`
to have the computer keyboard becomes a piano keyboard. You may need to allow application access to the keyboard in system settings
