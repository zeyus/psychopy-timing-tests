"""Shapes and shape animations"""
from psychopy.visual.rect import Rect
from psychopy.visual.window import Window
from psychopy.visual.shape import BaseShapeStim
from typing import Literal


class Square(Rect):
    def __init__(self, win: Window, size: int, pos: tuple[int, int], color: tuple[int, int, int]):
        super().__init__(win, width=size, height=size, pos=pos, fillColor=color, lineColor=color)

    def draw(self):
        super().draw()


class PhotoDiodeSquare(Square):
    def __init__(self, win: Window, size: int, corner: Literal['tl'] | Literal['tr'] | Literal['bl'] | Literal['br'] = 'br' , color: tuple[int, int, int] = (255, 255, 255)):
        if corner == 'tl':
            pos = (-win.size[0]/2 + size/2, win.size[1]/2 - size/2)
        elif corner == 'tr':
            pos = (win.size[0]/2 - size/2, win.size[1]/2 - size/2)
        elif corner == 'bl':
            pos = (-win.size[0]/2 + size/2, -win.size[1]/2 + size/2)
        elif corner == 'br':
            pos = (win.size[0]/2 - size/2, -win.size[1]/2 + size/2)
        super().__init__(win, size, pos, color)

    def draw(self):
        super().draw()


class EaseInEaseOut(BaseShapeStim):
    """Animate a shape from starting pos to ending pos easing the animation at the ends, can be repeated indefinitely"""
    def __init__(self, win: Window, shape: BaseShapeStim, start_pos: tuple[int, int], end_pos: tuple[int, int], duration: float, repeat: bool = False, bidirectional: bool = True):
        self.win = win
        self.shape = shape
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.repeat = repeat
        self.t = 0
        self.finished = False
        self.bidirectional = bidirectional

    def draw(self):
        if self.finished:
            return
        if self.t >= self.duration:
            if self.repeat:
                self.reset()
            else:
                self.finished = True
                return
        if self.bidirectional:
            if self.t < self.duration/2:
                self.shape.pos = self.ease_in_out(self.t, self.start_pos, self.end_pos, self.duration / 2)
            else:
                self.shape.pos = self.ease_in_out(self.t - self.duration/2, self.end_pos, self.start_pos, self.duration / 2)
        else:
            self.shape.pos = self.ease_in_out(self.t, self.start_pos, self.end_pos, self.duration)
        self.t += self.win.monitorFramePeriod
        self.shape.draw()
        

    def ease_in_out(self, t: float, b: tuple[int, int], c: tuple[int, int], d: float) -> tuple[int, int]:
        t /= d / 2
        if t < 1:
            return (c[0] - b[0]) / 2 * t * t + b[0], (c[1] - b[1]) / 2 * t * t + b[1]
        t -= 1
        return -(c[0] - b[0]) / 2 * (t * (t - 2) - 1) + b[0], -(c[1] - b[1]) / 2 * (t * (t - 2) - 1) + b[1]
    
    def reset(self):
        self.t = 0
        self.finished = False
        self.shape.pos = self.start_pos

    def stop(self):
        self.finished = True
        self.shape.pos = self.end_pos
        self.t = self.duration

    def start(self):
        self.finished = False
        self.t = 0
        self.shape.pos = self.start_pos


class BounceHorizontal(EaseInEaseOut):
    def __init__(self, win: Window, shape: BaseShapeStim, start_y: int, end_y: int, duration: float, repeat: bool = True):
        super().__init__(win, shape, (start_y, shape.pos[1]), (end_y, shape.pos[1]), duration, repeat)



class BounceVertical(EaseInEaseOut):
    def __init__(self, win: Window, shape: BaseShapeStim, start_x: int, end_x: int, duration: float, repeat: bool = True):
        super().__init__(win, shape, (start_x, shape.pos[1]), (end_x, shape.pos[1]), duration, repeat)

