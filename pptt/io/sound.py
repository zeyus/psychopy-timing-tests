"""Sound I/O class for pptt."""

import psychtoolbox as ptb  # type: ignore
from psychopy.sound import Sound  # type: ignore
from psychopy.sound.microphone import Microphone  # type: ignore
from psychopy.visual import Window  # type: ignore
from psychopy import prefs  # type: ignore
from pathlib import Path
import os

# ensure that the audio library is set to PTB
prefs.hardware["audioLib"] = ["PTB"]  # type: ignore
# make sure we fail if we don't get control of the audio device
prefs.hardware["audioLatencyMode"] = 4  # type: ignore

class Note:
    """Class for playing a single note."""
    
    def __init__(self, note: str = "A", duration: float = 0.1, sr: int = 44100, volume: float = 0.5):
        """Initializes the sound.
        
        Args:
            note: The note to play.
            duration: The duration of the note in seconds.
            sr: The sample rate of the note.
            volume: The volume of the note.
        """
        self.note = note
        self.duration = duration
        self.sound = Sound(
            value=note,
            secs=duration,
            sampleRate=sr,
            volume=volume
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
        if self.sound.isPlaying:
            self.sound.stop()

class AsyncMic:
    """Class for asynchronous microphone recording."""

    def __init__(self, duration: float = 1.0, sr: int = 44100, output_folder: Path = Path(os.getcwd()) / "recordings"):
        """Initializes the microphone.
        
        Args:
            duration: The duration of the recording in seconds.
            sr: The sample rate of the recording.
        """
        
        self.duration = duration
        self.sr = sr
        self.mic = Microphone(
            sampleRateHz=sr,
            channels=1,
            recordingFolder=output_folder,
        )
        raise NotImplementedError("This class is not yet implemented.")
    
    def record(self):
        """Records the sound."""
        self.mic.record(self.duration)
    
    def get_data(self):
        """Gets the recorded data."""
        return self.mic.getRecording()

    def __del__(self):
        """Closes the microphone."""
        self.mic.stop()
