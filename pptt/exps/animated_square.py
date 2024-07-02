"""Animated square experiment."""

from math import floor

from pptt.blocks.shapes import BounceHorizontal, PhotoDiodeSquare, Square
from pptt.io.port import ParallelPort
from pptt.io.sound import Note

from psychopy import visual, event  # type: ignore
from psychopy.event import Mouse  # type: ignore
from psychopy.logging import data  # type: ignore

async def animated_square(
        num_iter: int = 10000,
        trigger_every: int = 100,
        res: tuple[int, int] = (2560, 1440),
        port_addr: int = 0x378):
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
    """

    note = Note(
        sr=48000,
    )
    win = visual.Window(res, fullscr=True, units='pix', color='black')
    mouse = Mouse(visible=True)


    refresh_rate = win.getActualFrameRate()
    if refresh_rate is None:
        raise ValueError('Could not determine refresh rate of the monitor')
    data(f'Refresh rate: {refresh_rate}')

    # set pin high time to one frame
    pin_high_frames = 1

    timing_marker = PhotoDiodeSquare(win, 100, 'br', (255, 255, 255))
    # square should be in the middle of the screen vertically
    square = Square(win, res[1] // 10, (0, 0), (255, 255, 255))
    bounce = BounceHorizontal(win, square, -(res[0]//2), res[0]//2, 5.0, True)

    port = ParallelPort(port_addr)
    pins_used = 3
    port_pinstate = [
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
    data('Animated Square test started')
    data(f'Number of iterations: {num_iter}')
    data(f'Trigger every: {trigger_every}')
    data(f'Screen resolution: {res}')
    data(f'Parallel port address: 0x{port_addr:x}')

    mouse.clickReset()
    mouse_down = False
    for i in range(num_iter):
        should_trigger = False
        bounce.draw()
        nextFlip = win.getFutureFlipTime()

        # play sound every 2 seconds
        if i % floor(refresh_rate * 2) == 0:
            should_trigger = True
            note.play_on_flip(win)
            timing_marker.draw()
            port_pinstate[2] = 1
            data(f'Trigger pin 2 high (sound) scheduled at {nextFlip}, state: {port_pinstate}')
            port_pinup_start_frame[2] = i

        if mouse.getPressed()[0]:
            if not mouse_down:
                should_trigger = True
                timing_marker.draw()
                port_pinstate[1] = 1
                
                data(f'Trigger pin 1 high (mouse) scheduled at {nextFlip}, state: {port_pinstate}')
                _, times = mouse.getPressed(getTime=True)
                data(f'Mouse click at {times[0]}')  # type: ignore
                mouse.clickReset()
                mouse_down = True
                port_pinup_start_frame[1] = i
        else:
            mouse_down = False

        if i % trigger_every == 0:
            should_trigger = True
            timing_marker.draw()
            port_pinstate[0] = 1
            data(f'Trigger pin 0 high (interval) scheduled at {nextFlip}, state: {port_pinstate}')
            port_pinup_start_frame[0] = i
        
        # if it's been more > pin_high_time since the last trigger, set the pin low
        for pin, start_frame in enumerate(port_pinup_start_frame):
            if start_frame is not None and i - start_frame > pin_high_frames:
                port_pinstate[pin] = 0
                data(f'Trigger pin {pin} low scheduled at {nextFlip}, state: {port_pinstate}')
                port_pinup_start_frame[pin] = None
            if pin >= pins_used: # break early to avoid unnecessary checks
                break
        
        if should_trigger: # we send all pin values at once if any of them are high
            win.callOnFlip(port.set_pins, port_pinstate)
        
        win.flip()

        if 'escape' in event.getKeys():
            break

    win.close()
