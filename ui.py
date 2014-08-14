#!/usr/bin/env python
from time import sleep
import drawille
import os
import select
import sys
import termios
import tty

#
# Hard-coded constants that match Drawille's behavior.
#
HORIZONTAL_PIXELS_PER_CHAR = 2
VERTICAL_PIXELS_PER_CHAR = 4


size = drawille.getTerminalSize()
width = (size[0]-1) * HORIZONTAL_PIXELS_PER_CHAR
height = (size[1]-1) * VERTICAL_PIXELS_PER_CHAR


def fill_rect(c, x1, y1, x2, y2):
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
            fill_rect(c, bar_left, line_top, bar_actual, line_top+1)
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


def init_input():
    global old_settings
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

def poll_input():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def cleanup_input():
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
