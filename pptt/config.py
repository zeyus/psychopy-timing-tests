from psychopy import prefs  # type: ignore

def set_psychopy_prefs() -> None:
    prefs.hardware["audioLib"] = ["PTB"]  # type: ignore
    prefs.hardware["audioLatencyMode"] = 4  # type: ignore