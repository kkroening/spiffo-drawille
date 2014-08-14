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


amplitude = ui.Control("amp", 1, -2, 2)
frequency = ui.Control("freq", 1.0, 0.1, 5)
phase = ui.Control("phase", 0.0, -1, 1)
resolution = ui.Control("res", 5, 1, 10)
speed = ui.Control("speed", 1, -2, 2)

controls = [
    amplitude,
    frequency,
    phase,
    #resolution
]

ui_width = width / 5
ui_height = ui.VERTICAL_PIXELS_PER_CHAR * len(controls) + 10
ui_x = width - 4 - ui_width
ui_y = 4

ui_inst = ui.UI(ui_x, ui_y, ui_width, ui_height, controls)

plot_width = int(width * 2/3.);
plot_height = int(height * 2/3.);
plot_centerx = width/2
plot_centery = height/2
plot_left = plot_centerx - plot_width/2
plot_top = plot_centery - plot_height/2
plot_right = plot_centerx + plot_width/2
plot_bottom = plot_centery + plot_height/2


def render(c):
    #
    # Draw axes.
    #
    ui.draw_line(c, plot_left, plot_centery, plot_right, plot_centery)

    #
    #
    # Draw plot
    count = resolution.value * 20
    for n in range(int(count)):
        i = n / count
        x = plot_left + i * plot_width
        y = plot_centery - plot_height/4. * amplitude.value * math.sin(2 * math.pi * (frequency.value * i +  phase.value))
        if n != 0 and not ((x < 0 or x > width) and (y < 0 or y > width) and (prevx < 0 or prevx > height) and (prevy < 0 or prevy > height)):
            ui.draw_line(c, prevx, prevy, x, y)
        prevx = x
        prevy = y

    ui_inst.render(c)


def update(c, deltaTime):
    pass


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
