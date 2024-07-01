"""Animated square experiment."""

from pptt.blocks.shapes import BounceHorizontal, PhotoDiodeSquare, Square
from pptt.io.port import ParallelPort

from psychopy import visual, event
from psychopy.event import Mouse
from psychopy.logging import data

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

    win = visual.Window(res, fullscr=True, units='pix', color='black')
    mouse = Mouse(visible=True)

    refresh_rate = win.getActualFrameRate()

    timing_marker = PhotoDiodeSquare(win, 100, 'br', (255, 255, 255))
    # square should be in the middle of the screen vertically
    square = Square(win, res[1] // 10, (0, 0), (255, 255, 255))
    bounce = BounceHorizontal(win, square, -(res[0]//2), res[0]//2, 5.0, True)

    port = ParallelPort(port_addr)
    data('Animated Square test started')
    data(f'Number of iterations: {num_iter}')
    data(f'Trigger every: {trigger_every}')
    data(f'Screen resolution: {res}')
    data(f'Port address: {port_addr}')
    last_trigger: int | None = None
    mouse.clickReset()
    mouse_down = False
    for i in range(num_iter):
        bounce.draw()
        if mouse.getPressed()[0]:
            if not mouse_down:
                timing_marker.draw()
                nextFlip = win.getFutureFlipTime()
                win.callOnFlip(port.send_trigger, 2)
                data(f'Trigger high (mouse) scheduled at {nextFlip}')
                _, times = mouse.getPressed(getTime=True)
                data(f'Mouse click at {times[0]}')
                last_trigger = i
                mouse.clickReset()
                mouse_down = True
        else:
            mouse_down = False

        if i % trigger_every == 0:
            timing_marker.draw()
            nextFlip = win.getFutureFlipTime()
            win.callOnFlip(port.send_trigger, 1)
            data(f'Trigger high (interval) scheduled at {nextFlip}')
            last_trigger = i
        
        # if it's been more 1ms or more send a low signal
        if last_trigger is not None and (i - last_trigger) * (1/refresh_rate) >= 0.001:
            nextFlip = win.getFutureFlipTime()
            win.callOnFlip(port.send_trigger, 0)
            data(f'Trigger low scheduled at {nextFlip}')
            last_trigger = None
        win.flip()

        if 'escape' in event.getKeys():
            break

    win.close()