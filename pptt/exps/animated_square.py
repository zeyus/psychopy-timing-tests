"""Animated square experiment."""

from math import floor, ceil
from pathlib import Path
from typing import Literal

import numpy as np

from pptt.blocks.shapes import BounceHorizontal, PhotoDiodeSquare, Square
from pptt.io.port import ParallelPort
from pptt.io.sound import Note, Mic

from psychopy import visual, event, core  # type: ignore
from psychopy.event import Mouse  # type: ignore
from psychopy import logging, data  # type: ignore


async def animated_square(
        num_iter: int = 10000,
        trigger_every: int = 100,
        res: tuple[int, int] = (2560, 1440),
        port_addr: int = 0x378,
        speaker_sr: int = 44100,
        speaker_volume: float = 0.5,
        speaker_device: int | None = None,
        microphone_sr: int = 44100,
        microphone_channels: int = 1,
        microphone_device: int | None = None,
        data_dir: Path = Path('data'),
        trigger_square_pos: Literal['tl', 'tr', 'bl', 'br'] = 'br'):
    """Animate a square moving horizontally and bouncing off the edges of the screen.

    Parameters
    ----------
    num_iter : int
        Number of iterations to run the experiment.
    trigger_every : int
        Number of iterations to send a trigger signal.
    res : tuple[int, int]
        Screen resolution.
    port_addr : int
        Parallel port address.
    speaker_sr : int
        Speaker sample rate.
    speaker_volume : float
        Speaker volume.
    speaker_device : int | None
        Speaker device index.
    microphone_sr : int
        Microphone sample rate.
    microphone_channels : int
        Number of microphone channels.
    microphone_device : int | None
        Microphone device index.
    data_dir : Path
        Directory to save data files to.
    trigger_square_pos : Literal['tl', 'tr', 'bl', 'br']
        Location of the photodiode square.
    """

    # set up data logging
    data_file = data_dir / 'animated_square_timings'
    logging.data(f'Logging data to {data_file}')

    note = Note(
        sr=speaker_sr,
        volume=speaker_volume,
        device=speaker_device
    )
    win = visual.Window(res, fullscr=True, units='pix', color='black')
    mouse = Mouse(visible=True)


    refresh_rate = win.getActualFrameRate()
    if refresh_rate is None:
        raise ValueError('Could not determine refresh rate of the monitor')
    logging.data(f'Refresh rate: {refresh_rate}')

    # set pin high time to one frame
    pin_high_frames = 1

    timing_marker = PhotoDiodeSquare(win, 100, trigger_square_pos, (255, 255, 255))
    # square should be in the middle of the screen vertically
    square = Square(win, res[1] // 10, (0, 0), (255, 255, 255))
    bounce = BounceHorizontal(win, square, -(res[0]//2), res[0]//2, 5.0, True)

    exp_runtime = num_iter / refresh_rate # assuming no dropped frames

    port = ParallelPort(port_addr)
    pins_used = 3
    port_pinstate: list[Literal[0, 1]] = [
        0, # photo diode
        0, # mouse
        0, # sound
        0,
        0,
        0,
        0,
        0
    ]

    port_pinup_start_frame: list[None | int] = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None
    ]
    logging.data('Animated Square test started')
    logging.data(f'Number of iterations: {num_iter}')
    logging.data(f'Trigger every: {trigger_every}')
    logging.data(f'Screen resolution: {res}')
    logging.data(f'Parallel port address: 0x{port_addr:x}')
    # set all pins low
    port.set_pins(port_pinstate)


    # exp_data = data.ExperimentHandler(
    #     name='animated_square',
    #     extraInfo=,
    #     dataFileName=str(data_file)
    # )

    trial_data = data.TrialHandler(
        nReps=1,
        method='sequential',
        extraInfo={
            'num_iter': num_iter,
            'trigger_every': trigger_every,
            'res': res,
            'port_addr': port_addr,
            'speaker_sr': speaker_sr,
            'speaker_volume': speaker_volume,
            'speaker_device': speaker_device,
            'microphone_sr': microphone_sr,
            'microphone_device': microphone_device,
            'data_dir': data_dir,
            'trigger_square_pos': trigger_square_pos,
        },
        trialList=list({'idx': i} for i in range(num_iter)), # this shouldn't need all of them but we don't know which frame something occurs in
        name='animated_square'
    )

    # exp_data.addLoop(trial_data)
    # start mic
    mic = Mic(
        sr=microphone_sr,
        channels=microphone_channels,
        device=microphone_device)
    logging.data('Starting microphone')
    mic.record(exp_runtime + 1.0)  # type: ignore
    
    mouse.clickReset()
    mouse_down = False
    data_indices: set[int] = set()
    elapsed = core.Clock()
    for i, trial in enumerate(trial_data):
        should_trigger = False
        bounce.draw()
        nextFlip = win.getFutureFlipTime()

        # play sound every 2 seconds
        if i % floor(refresh_rate * 2) == 0:
            should_trigger = True
            note.play_on_flip(win)
            timing_marker.draw()
            port_pinstate[2] = 1
            logging.data(f'Trigger pin 2 high (sound) scheduled at {nextFlip}, state: {port_pinstate}')
            trial_data.addData('sound_onset', nextFlip)
            data_indices.add(trial_data.thisTrialN)
            port_pinup_start_frame[2] = i

        if mouse.getPressed()[0]:
            if not mouse_down:
                should_trigger = True
                timing_marker.draw()
                port_pinstate[1] = 1
                
                logging.data(f'Trigger pin 1 high (mouse) scheduled at {nextFlip}, state: {port_pinstate}')
                _, times = mouse.getPressed(getTime=True)
                logging.data(f'Mouse click at {times[0]}')  # type: ignore
                trial_data.addData('mouse_click', times[0])  # type: ignore
                trial_data.addData('mouse_click_trigger', nextFlip)
                data_indices.add(trial_data.thisTrialN)
                mouse.clickReset()
                mouse_down = True
                port_pinup_start_frame[1] = i
        else:
            mouse_down = False

        if i % trigger_every == 0:
            should_trigger = True
            timing_marker.draw()
            port_pinstate[0] = 1
            logging.data(f'Trigger pin 0 high (interval) scheduled at {nextFlip}, state: {port_pinstate}')
            trial_data.addData('regular_trigger', nextFlip)
            data_indices.add(trial_data.thisTrialN)
            port_pinup_start_frame[0] = i
        
        # if it's been more > pin_high_time since the last trigger, set the pin low
        for pin, start_frame in enumerate(port_pinup_start_frame):
            if start_frame is not None and i - start_frame > pin_high_frames:
                port_pinstate[pin] = 0
                logging.data(f'Trigger pin {pin} low scheduled at {nextFlip}, state: {port_pinstate}')
                trial_data.addData(f'pin_{pin}_low', nextFlip)
                data_indices.add(trial_data.thisTrialN)
                port_pinup_start_frame[pin] = None
                should_trigger = True
            if pin >= pins_used: # break early to avoid unnecessary checks
                break
        
        if should_trigger: # we send all pin values at once if any of them are high
            trial_data.addData('pin_state', " - ".join(map(str, port_pinstate)))  # type: ignore
            data_indices.add(trial_data.thisTrialN)
            # add timestamp
            trial_data.addData('trial_timestamp', elapsed.getTime())
            trial_data.addData('core_timestamp', core.getTime())
            win.callOnFlip(port.set_pins, port_pinstate)
        # poll mic (recommended to poll once per frame)
        mic.poll()
        win.flip()

        if 'escape' in event.getKeys():
            break

    # set all pins low
    port.set_pins([0, 0, 0, 0, 0, 0, 0, 0])
    win.close()
    logging.data('Stopping microphone')
    mic.stop()
    logging.data('Saving microphone clips')
    mic_out_file = data_dir / 'mic_recording.wav'
    if mic_out_file.exists():
        # add a number to the end of the file name
        i = 1
        while mic_out_file.exists():
            mic_out_file = data_dir / f'mic_recording_{i}.wav'
            i += 1
    mic.save(str(mic_out_file))

    # filter trial data
    trial_data.trialList = [trial_data.trialList[i] for i in sorted(data_indices)]
    ntrials = len(data_indices)

    trial_data.sequenceIndices = np.array([range(ntrials)])

    # mess up the data by removing all trials except the ones in data_indices
    names = trial_data.data.keys()
    np_idx = np.array(list(data_indices))
    for name in names:
        trial_data.data[name] = trial_data.data[name][np_idx]

    trial_data.saveAsText(
        data_file,
        dataOut='all_raw',
        appendFile=False,
        fileCollisionMethod='rename',
    )
    logging.info('Data saved to ' + str(data_file))
    logging.data('Animated Square test ended')
    
