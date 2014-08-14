#!/usr/bin/env python
import drawille
import curses
import math
from time import sleep
import locale
import os
import pygame
import termios
import sys
import tty
import select

locale.setlocale(locale.LC_ALL,"")

stdscr = curses.initscr()
stdscr.refresh()


#
# Hard-coded constants that match Drawille's behavior.
#
HORIZONTAL_PIXELS_PER_CHAR = 2
VERTICAL_PIXELS_PER_CHAR = 4


size = drawille.getTerminalSize()
width = (size[0]-1) * HORIZONTAL_PIXELS_PER_CHAR
height = (size[1]-1) * VERTICAL_PIXELS_PER_CHAR


def draw_solid_rect(c, x1, y1, x2, y2):
    for x in range(x1, x2+1):
        for y in range(y1, y2+1):
            c.set(x, y)

def draw_rect_border(c, x1, y1, x2, y2):
    draw_line(c, x1, y1, x2, y1)
    draw_line(c, x2, y1, x2, y2)
    draw_line(c, x2, y2, x1, y2)
    draw_line(c, x1, y2, x1, y1)

def clear_rect(c, x1, y1, x2, y2):
    for x in range(x1, x2+1):
        for y in range(y1, y2+1):
            c.unset(x, y)

def draw_rect(c, x1, y1, x2, y2):
    clear_rect(c, x1, y1, x2, y2)
    draw_rect_border(c, x1, y1, x2, y2)

def draw_line(c, x1, y1, x2, y2):
    for x, y in drawille.line(x1, y1, x2, y2):
        c.set(x, y)


class Control:
    def __init__(self, name, value, min_value, max_value):
        self.name = name
        self.value = float(value)
        self.min_value = float(min_value)
        self.max_value = float(max_value)

    def render(c):
        for x in range(self.x, self.x + self.width + 1):
            for y in range(self.y, self.y + self.height + 1):
                if x == self.x or x == self.width or y == self.y or y == self.height:
                    c.set(x, y)
                else:
                    c.unset(x, y)

UI_LEFT_MARGIN = 4
UI_NAME_CHARS  = 8
UI_RIGHT_MARGIN = 8

class UI:
    def __init__(self, x, y, width, height, controls):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.controls = controls
        self.selected_control_id = 0

    def render(self, c):
        #
        # Draw main box.
        #
        draw_rect(c, self.x, self.y, self.x + self.width, self.y + self.height)

        left = self.x + UI_LEFT_MARGIN + HORIZONTAL_PIXELS_PER_CHAR
        top = self.y + VERTICAL_PIXELS_PER_CHAR

        #
        # Align left and top to character boundary.
        #
        left = left - (left % HORIZONTAL_PIXELS_PER_CHAR)
        top = top - (top % VERTICAL_PIXELS_PER_CHAR)

        name_left  = left + HORIZONTAL_PIXELS_PER_CHAR * 2

        line_top = top

        for control in self.controls:
            c.set_text(name_left, line_top, control.name)
            minvalue_left = name_left + (UI_NAME_CHARS + 2) * HORIZONTAL_PIXELS_PER_CHAR
            c.set_text(minvalue_left, line_top, str(int(control.min_value)))
            maxvalue_left = self.x + self.width - UI_RIGHT_MARGIN - 2 * HORIZONTAL_PIXELS_PER_CHAR
            maxvalue_left = maxvalue_left - (maxvalue_left % HORIZONTAL_PIXELS_PER_CHAR)
            c.set_text(maxvalue_left, line_top, str(int(control.max_value)))
            bar_left = minvalue_left + 3 * HORIZONTAL_PIXELS_PER_CHAR + 2
            bar_right = maxvalue_left - 3 * HORIZONTAL_PIXELS_PER_CHAR - 2
            bar_actual = bar_left + int((bar_right - bar_left) * (control.value - control.min_value) / (control.max_value - control.min_value))
            #bar_actual = bar_right
            draw_solid_rect(c, bar_left, line_top, bar_actual, line_top+1)
            line_top = line_top + VERTICAL_PIXELS_PER_CHAR

        c.set_text(left, top + VERTICAL_PIXELS_PER_CHAR * self.selected_control_id, "*")
        selected_bar_top = top + self.selected_control_id * VERTICAL_PIXELS_PER_CHAR - 1
        draw_rect_border(c, bar_left - 2, selected_bar_top, bar_right + 2, selected_bar_top + VERTICAL_PIXELS_PER_CHAR)

    def next_control(self):
        self.selected_control_id = self.selected_control_id + 1
        if self.selected_control_id >= len(self.controls):
            self.selected_control_id = 0

    def prev_control(self):
        self.selected_control_id = self.selected_control_id - 1
        if self.selected_control_id < 0:
            self.selected_control_id = len(self.controls) - 1

    def decrease_control(self):
        control = self.controls[self.selected_control_id]
        control.value = control.value - 1/10. * (control.max_value - control.min_value)
        if control.value < control.min_value:
            control.value = control.min_value

    def increase_control(self):
        control = self.controls[self.selected_control_id]
        control.value = control.value + 1/10. * (control.max_value - control.min_value)
        if control.value > control.max_value:
            control.value = control.max_value


a1 = Control("a1", 5.0, 0, 5)
a2 = Control("a2", 2.2, 0, 5)
a3 = Control("a3", 0.2, 0, 5)
c1 = Control("c1", 0.11, 0.05, 0.25)
c2 = Control("c2", 0.05, 0.05, 0.25)
c3 = Control("c3", 0.12, 0.05, 0.25)
w1 = Control("w1", 3.0, -10, 10)
w2 = Control("w2", 4.25, -10, 10)
w3 = Control("w3", 1.0, -10, 10)
dw1 = Control("dw1", 0.8, -10, 10)
dw2 = Control("dw2", -0.069, -10, 10)
dw3 = Control("dw3", -1.0, -10, 10)
max_freq = Control("max_freq", 12.0, -30, 30)
p1 = Control("p1", 0.0, -1, 1)
p2 = Control("p2", 0.0, -1, 1)
p3 = Control("p3", 0.0, -1, 1)
dp1 = Control("dp1", 0.0, -2, 2)
dp2 = Control("dp2", -0.0132, -2, 2)
dp3 = Control("dp3", 0.0, -2, 2)
speed = Control("speed", 2.0, -5, 5)
cycles = Control("cycles", 2.0, 0, 5)
resolution = Control("res", 6, 1, 10)


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
ui_height = VERTICAL_PIXELS_PER_CHAR * len(controls) + 10
ui_x = width - 4 - ui_width
ui_y = 4

ui = UI(ui_x, ui_y, ui_width, ui_height, controls)


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
    ui.render(c)

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


def init_input():
    global old_settings
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

def poll_input():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def cleanup_input():
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def __main__(stdscr):
    try:
        init_input()

        c = drawille.Canvas()
        while 1:
            render(c)

            f = c.frame(0, 0, width, height)
            stdscr.addstr(0, 0, '{0}\n'.format(f))
            stdscr.refresh()

            if poll_input():
                key = sys.stdin.read(1)
                if key == 'q':
                    break
                elif key == 'k':
                    ui.prev_control()
                elif key == 'j':
                    ui.next_control()
                elif key == 'h':
                    ui.decrease_control()
                elif key == 'l':
                    ui.increase_control()

            sleep(1.0/20)
            update(c, 1.0/20 * speed.value) # FIXME: use clock.
            c.clear()

    finally:
        cleanup_input()


if __name__ == '__main__':
    from sys import argv
    curses.wrapper(__main__)
