"""Sound I/O class for pptt."""

import psychtoolbox as ptb  # type: ignore
from psychopy.hardware.speaker import SpeakerDevice  # type: ignore
from psychopy.hardware.microphone import MicrophoneDevice  # type: ignore
from psychopy.hardware.manager import getDeviceManager  # type: ignore
from psychopy.sound import AudioClip, Sound, AudioDeviceInfo  # type: ignore
from psychopy.sound.microphone import Microphone  # type: ignore
from psychopy.visual import Window  # type: ignore
from psychopy import prefs  # type: ignore
from psychopy import logging  # type: ignore
from pathlib import Path
import os

# ensure that the audio library is set to PTB
prefs.hardware["audioLib"] = ["PTB"]  # type: ignore
# make sure we fail if we don't get control of the audio device
prefs.hardware["audioLatencyMode"] = 4  # type: ignore

class Note:
    """Class for playing a single note."""
    
    def __init__(self, note: str = "A", duration: float = 0.1, sr: int = 44100, volume: float = 0.5, device: int | None = None):
        """Initializes the sound.
        
        Args:
            note: The note to play.
            duration: The duration of the note in seconds.
            sr: The sample rate of the note.
            volume: The volume of the note.
        """
        self.note = note
        self.duration = duration
        if device is None:
            logging.warn("No speaker device specified.")
            devices = SpeakerDevice.getAvailableDevices()
            if len(devices) == 0:
                raise ValueError("No speaker devices found.")
            logging.info(f"Available speaker devices: {devices}")
            device1 = devices[0]
            logging.info(f"Using speaker device: {device}")
            device = device1['index']  # type: ignore
        self.device = device
        self.sound = Sound(
            value=note,
            secs=duration,
            sampleRate=sr,
            volume=volume,
            speaker=device
        )
    
    def play(self, delay: float = 0.0):
        """Plays the sound.
        
        Args:
            delay: The delay before playing the sound.
        """
        if delay == 0.0:
            self.sound.play()
            return
        self.sound.play(when=ptb.GetSecs() + delay)

    def play_on_flip(self, win: Window, delay: float = 0.0):
        """Plays the sound on the next flip of the window.
        
        Args:
            win: The window about to be flipped.
            delay: The delay before playing the sound (after the `win.flip()`).
        """
        if delay == 0.0:
            self.sound.play(when=win.getFutureFlipTime(clock='ptb'))
            return
        self.sound.play(when=win.getFutureFlipTime(clock='ptb') + delay)

    def __del__(self):
        """Closes the sound."""
        try:
            if self.sound.isPlaying:
                self.sound.stop()
        except AttributeError:
            pass

class Mic:
    """Class for microphone recording."""

    def __init__(self, sr: int = 44100, output_folder: Path = Path(os.getcwd()) / "recordings", device: int | None = None):
        """Initializes the microphone.
        
        Args:
            sr: The sample rate of the recording.
            output_folder: The folder to save the recordings to.
            device: The microphone device to use.
        """

        self.sr = sr
        self.output_folder = output_folder
        if device is None:
            logging.warn("No microphone device specified.")
            devices = MicrophoneDevice.getAvailableDevices()
            if len(devices) == 0:
                raise ValueError("No microphone devices found.")
            logging.info(f"Available microphone devices: {devices}")
            device1 = devices[0]
            logging.info(f"Using microphone device: {device1}")
            device = device1['index']  # type: ignore
        self.device = device
        logging.warn(f"Using microphone device index: {device}")
        self.mic = Microphone(
            device=device,
            sampleRateHz=sr,
            channels=1,
            streamBufferSecs=5.0,
            recordingFolder=output_folder,
        )
    
    def record(self, duration: float | None = None):
        """Records the sound."""
        self.mic.record(duration)
    
    def get_data(self):
        """Gets the recorded data."""
        return self.mic.getRecording()
    
    def stop(self):
        """Stops the recording."""
        if self.mic.recording:
            self.mic.stop()
    
    def save(self, filename: str):
        """Saves the recording to a file."""
        rec: AudioClip = self.mic.getRecording()
        rec.save(filename)
        
    def poll(self):
        """Polls the microphone."""
        return self.mic.poll()

    def __del__(self):
        """Closes the microphone."""
        try:
            if self.mic.recording:
                self.mic.stop()
            self.mic.close()
        except AttributeError:
            pass
