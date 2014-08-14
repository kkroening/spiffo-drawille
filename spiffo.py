#!/usr/bin/env python
from time import sleep
import ui
import curses
import drawille
import locale
import math
import sys

locale.setlocale(locale.LC_ALL,"")

stdscr = curses.initscr()
stdscr.refresh()


size = drawille.getTerminalSize()
width = (size[0]-1) * ui.HORIZONTAL_PIXELS_PER_CHAR
height = (size[1]-1) * ui.VERTICAL_PIXELS_PER_CHAR


a1 = ui.Control("a1", 5.0, 0, 5)
a2 = ui.Control("a2", 2.2, 0, 5)
a3 = ui.Control("a3", 0.2, 0, 5)
c1 = ui.Control("c1", 0.11, 0.05, 0.25)
c2 = ui.Control("c2", 0.05, 0.05, 0.25)
c3 = ui.Control("c3", 0.12, 0.05, 0.25)
w1 = ui.Control("w1", 3.0, -10, 10)
w2 = ui.Control("w2", 4.25, -10, 10)
w3 = ui.Control("w3", 1.0, -10, 10)
dw1 = ui.Control("dw1", 0.8, -10, 10)
dw2 = ui.Control("dw2", -0.069, -10, 10)
dw3 = ui.Control("dw3", -1.0, -10, 10)
max_freq = ui.Control("max_freq", 12.0, -30, 30)
p1 = ui.Control("p1", 0.0, -1, 1)
p2 = ui.Control("p2", 0.0, -1, 1)
p3 = ui.Control("p3", 0.0, -1, 1)
dp1 = ui.Control("dp1", 0.0, -2, 2)
dp2 = ui.Control("dp2", -0.0132, -2, 2)
dp3 = ui.Control("dp3", 0.0, -2, 2)
speed = ui.Control("speed", 2.0, -5, 5)
cycles = ui.Control("cycles", 2.0, 0, 5)
resolution = ui.Control("res", 6, 1, 10)


controls = [
    a1,
    a2,
    #a3,
    c1,
    c2,
    #c3,
    #w1,
    #w2,
    #w3,
    dw1,
    dw2,
    #dw3,
    max_freq,
    #p1,
    #p2,
    #p3,
    dp1,
    dp2,
    #dp3,
    speed,
    cycles,
    resolution
]

ui_width = width / 6
ui_height = ui.VERTICAL_PIXELS_PER_CHAR * len(controls) + 10
ui_x = width - 4 - ui_width
ui_y = 4

ui_inst = ui.UI(ui_x, ui_y, ui_width, ui_height, controls)


def render_spirograph(c):
    for n in range(int(cycles.value * resolution.value*100)):
        i = float(n) / float(resolution.value*100)
        pow1 = math.pow(c1.value, i)
        pow2 = math.pow(c2.value, i)
        pow3 = math.pow(c3.value, i)
        x1 = a1.value * 100 * pow1 * math.cos(math.pi*2*(i*w1.value + p1.value))
        y1 = a1.value * 100 * pow1 * math.sin(math.pi*2*(i*w1.value + p1.value))
        x2 = a2.value * 100 * pow2 * math.cos(math.pi*2*(i*w2.value + p2.value))
        y2 = a2.value * 100 * pow2 * math.sin(math.pi*2*(i*w2.value + p2.value))
        x3 = a3.value * 100 * pow3 * math.cos(math.pi*2*(i*w3.value + p3.value))
        y3 = a3.value * 100 * pow3 * math.sin(math.pi*2*(i*w3.value + p3.value))
        x = (x1 + x2 + x3)*width/500 + width/2
        y = (y1 + y2 + y3)*height/500 + height/2
        if n != 0 and not ((x < 0 or x > width) and (y < 0 or y > width) and (prevx < 0 or prevx > height) and (prevy < 0 or prevy > height)):
            for px,py in drawille.line(prevx, prevy, x, y):
                c.set(px, py)
        prevx = x
        prevy = y

def render(c):
    render_spirograph(c)
    ui_inst.render(c)

def update(c, deltaTime):
    global w1, w2, w3, dw1, dw2, dw3, p1, p2, p3, dp1, dp2, dp3
    w1.value += dw1.value*deltaTime
    if w1.value > max_freq.value:
        w1.value = -max_freq.value
    elif w1.value < -max_freq.value:
        w1.value = max_freq.value
    w2.value += dw2.value*deltaTime
    if w2.value > max_freq.value:
        w2.value = -max_freq.value
    elif w2.value < -max_freq.value:
        w2.value = max_freq.value
    w3.value += dw3.value*deltaTime
    if w3.value > max_freq.value:
        w3.value = -max_freq.value
    elif w3.value < -max_freq.value:
        w3.value = max_freq.value
    p1.value += dp1.value * deltaTime
    p2.value += dp2.value * deltaTime
    p3.value += dp3.value * deltaTime

def __main__(stdscr):
    try:
        ui.init_input()

        c = drawille.Canvas()
        while 1:
            render(c)

            f = c.frame(0, 0, width, height)
            stdscr.addstr(0, 0, '{0}\n'.format(f))
            stdscr.refresh()

            if ui.poll_input():
                key = sys.stdin.read(1)
                if key == 'q':
                    break
                elif key == 'k':
                    ui_inst.prev_control()
                elif key == 'j':
                    ui_inst.next_control()
                elif key == 'h':
                    ui_inst.decrease_control()
                elif key == 'l':
                    ui_inst.increase_control()

            sleep(1.0/20)
            update(c, 1.0/20 * speed.value) # FIXME: use clock.
            c.clear()

    finally:
        ui.cleanup_input()


if __name__ == '__main__':
    from sys import argv
    curses.wrapper(__main__)
