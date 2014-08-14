#!/usr/bin/env python
import drawille
import curses
import math
from time import sleep
import locale
import os

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


a1 = 500.0
a2 = 220.0
a3 = 20.0
c1 = 0.11
c2 = 0.06
c3 = 0.12
w1 = 3.0
w2 = 4.25
w3 = 1.0
dw1 = 0.8
dw2 = -0.069
dw3 = -1.0
max_freq = 12.0
p1 = 0.0
p2 = 0.0
p3 = 0.0
dp1 = 0.0
dp2 = -0.0132
dp3 = 0.0
speed = 2.0
cycles = 2.0
resolution = 600

ui_width = width / 6
ui_height = height / 3
ui_x = width - 4 - ui_width
ui_y = 4


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
        self.value = value
        self.min_value = min_value
        self.max_value = max_value

    def render(c):
        for x in range(self.x, self.x + self.width + 1):
            for y in range(self.y, self.y + self.height + 1):
                if x == self.x or x == self.width or y == self.y or y == self.height:
                    c.set(x, y)
                else:
                    c.unset(x, y)

UI_LEFT_MARGIN = 4
UI_NAME_CHARS  = 8
UI_RIGHT_MARGIN = 4

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
            c.set_text(minvalue_left, line_top, str(control.min_value))
            maxvalue_left = self.x + self.width - UI_RIGHT_MARGIN - 2 * HORIZONTAL_PIXELS_PER_CHAR
            maxvalue_left = maxvalue_left - (maxvalue_left % HORIZONTAL_PIXELS_PER_CHAR)
            c.set_text(maxvalue_left, line_top, str(control.max_value))
            bar_left = minvalue_left + 3 * HORIZONTAL_PIXELS_PER_CHAR
            bar_right = maxvalue_left - 3 * HORIZONTAL_PIXELS_PER_CHAR
            bar_actual =bar_left + int((bar_right - bar_left) * (control.value - control.min_value) / float(control.max_value - control.min_value))
            #bar_actual = bar_right
            draw_solid_rect(c, bar_left, line_top, bar_actual, line_top+1)
            line_top = line_top + VERTICAL_PIXELS_PER_CHAR

        c.set_text(left, top + VERTICAL_PIXELS_PER_CHAR * self.selected_control_id, "*")
        c.set_text(left, top, "*")


controls = [
    Control("test", 3, 0, 10),
    Control("test2", 4, 0, 10),
    Control("test3", 4, 0, 10)
]
ui = UI(ui_x, ui_y, ui_width, ui_height, controls)

def render_spirograph(c):
    for n in range(int(cycles * resolution)):
        i = float(n) / float(resolution)
        pow1 = math.pow(c1, i)
        pow2 = math.pow(c2, i)
        pow3 = math.pow(c3, i)
        x1 = a1 * pow1 * math.cos(math.pi*2*(i*w1 + p1))
        y1 = a1 * pow1 * math.sin(math.pi*2*(i*w1 + p1))
        x2 = a2 * pow2 * math.cos(math.pi*2*(i*w2 + p2))
        y2 = a2 * pow2 * math.sin(math.pi*2*(i*w2 + p2))
        x3 = a3 * pow3 * math.cos(math.pi*2*(i*w3 + p3))
        y3 = a3 * pow3 * math.sin(math.pi*2*(i*w3 + p3))
        x = (x1 + x2 + x3)*width/500 + width/2
        y = (y1 + y2 + y3)*height/500 + height/2
        if not ((x < 0 or x > width) and (y < 0 or y > width) and (prevx < 0 or prevx > height) and (prevy < 0 or prevy > height)):
            if n != 0:
                for px,py in drawille.line(prevx, prevy, x, y):
                    c.set(px, py)
        prevx = x
        prevy = y

def render(c):
    render_spirograph(c)
    ui.render(c)

def update(c, deltaTime):
    global w1, w2, w3, dw1, dw2, dw3, p1, p2, p3, dp1, dp2, dp3
    w1 += dw1*deltaTime
    if w1 > max_freq:
        w1 = -max_freq
    elif w1 < -max_freq:
        w1 = max_freq
    w2 += dw2*deltaTime
    if w2 > max_freq:
        w2 = -max_freq
    elif w2 < -max_freq:
        w2 = max_freq
    w3 += dw3*deltaTime
    if w3 > max_freq:
        w3 = -max_freq
    elif w3 < -max_freq:
        w3 = max_freq
    p1 += dp1 * deltaTime
    p2 += dp2 * deltaTime
    p3 += dp3 * deltaTime


def __main__(stdscr):
    c = drawille.Canvas()
    while 1:
        render(c)

        #f = c.frame(0, 0, 180, 140)
        f = c.frame(0, 0, width, height)
        stdscr.addstr(0, 0, '{0}\n'.format(f))
        stdscr.refresh()

        sleep(1.0/20)
        update(c, 1.0/20 * speed) # FIXME: use clock.
        c.clear()


if __name__ == '__main__':
    from sys import argv
    curses.wrapper(__main__)
