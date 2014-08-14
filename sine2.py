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


amplitude1 = ui.Control("amp1", 1, 0, 2)
amplitude2 = ui.Control("amp2", 0, 0, 2)
frequency1 = ui.Control("freq1", 1.0, 0.1, 5)
frequency2 = ui.Control("freq2", 2.0, 0.1, 5)
phase1 = ui.Control("phase1", 0.0, -1, 1)
phase2 = ui.Control("phase2", 0.0, -1, 1)
resolution = ui.Control("res", 5, 1, 10)
speed = ui.Control("speed", 1, -2, 2)

time = 0

controls = [
    amplitude1,
    amplitude2,
    frequency1,
    frequency2,
    phase1,
    phase2,
    #resolution,
    speed
]

class Plot:
    def __init__(self, plot_centerx, plot_centery, plot_width, plot_height):
        self.centerx = plot_centerx
        self.centery = plot_centery
        self.width = plot_width
        self.height = plot_height
        self.update_alignment()

    #
    # Recalculate alignment after moving/resizing plot.
    #
    def update_alignment(self):
        self.left = self.centerx - self.width/2
        self.top = self.centery - self.height/2
        self.right = self.centerx + self.width/2
        self.bottom = self.centery + self.height/2

    def draw_centered_axes(self, c):
        ui.draw_line(c, self.left, self.centery, self.right, self.centery)
        ui.draw_line(c, self.centerx, self.top, self.centerx, self.bottom)

    def draw_left_aligned_axes(self, c):
        ui.draw_line(c, self.left, self.centery, self.right, self.centery)
        ui.draw_line(c, self.left, self.top, self.left, self.bottom)


class SinePlot(Plot):
    def render(self, c):
        self.draw_left_aligned_axes(c)

        count = resolution.value * 20
        for n in range(int(count)):
            i = n / count
            x = self.left + i * self.width
            y1 = self.height/4. * amplitude1.value * math.sin(2 * math.pi * (frequency1.value * i +  phase1.value))
            y2 = self.height/4. * amplitude2.value * math.sin(2 * math.pi * (frequency2.value * i +  phase2.value))
            y = self.centery - (y1 + y2)
            if n != 0 and not ((x < 0 or x > width) and (y < 0 or y > width) and (prevx < 0 or prevx > height) and (prevy < 0 or prevy > height)):
                ui.draw_line(c, prevx, prevy, x, y)
            prevx = x
            prevy = y

        if mode != 0:
            x = self.left + time * self.width
            y1 = int(self.height/4. * amplitude1.value * math.sin(2 * math.pi * (frequency1.value * time + phase1.value)))
            y2 = int(self.height/4. * amplitude2.value * math.sin(2 * math.pi * (frequency2.value * time + phase2.value)))
            y = self.centery - (y1 + y2)
            ui.draw_ellipse(c, x, y, 5, 5, 16)

class PhaseSpace1DPlot(Plot):
    def render(self, c):
        self.draw_centered_axes(c)

        x = self.centerx
        y1 = int(self.height/4. * amplitude1.value * math.sin(2 * math.pi * (frequency1.value * time + phase1.value)))
        y2 = int(self.height/4. * amplitude2.value * math.sin(2 * math.pi * (frequency2.value * time + phase2.value)))
        y = self.centery - (y1 + y2)
        ui.draw_ellipse(c, x, y, 5, 5, 16)


class PhaseSpace2DPlot(Plot):
    def render(self, c):
        self.draw_centered_axes(c)

        x1 = int(self.width/4. * amplitude1.value * math.cos(2 * math.pi * (frequency1.value * time + phase1.value)))
        x2 = int(self.width/4. * amplitude2.value * math.cos(2 * math.pi * (frequency2.value * time + phase2.value)))
        y1 = int(self.height/4. * amplitude1.value * math.sin(2 * math.pi * (frequency1.value * time + phase1.value)))
        y2 = int(self.height/4. * amplitude2.value * math.sin(2 * math.pi * (frequency2.value * time + phase2.value)))
        x = self.centerx + x1 + x2
        y = self.centery - (y1 + y2)

        ui.draw_ellipse(c, self.centerx, self.centery, self.width/4. * amplitude1.value, self.height/4. * amplitude1.value, 100)
        ui.draw_ellipse(c, self.centerx + x1, self.centery - y1, self.width/4. * amplitude2.value, self.height/4. * amplitude2.value, 100)

        ui.draw_ellipse(c, x, y, 5, 5, 16)


ui_width = width / 5
ui_height = ui.VERTICAL_PIXELS_PER_CHAR * len(controls) + 10
ui_x = width - 4 - ui_width
ui_y = 4

ui_inst = ui.UI(ui_x, ui_y, ui_width, ui_height, controls)

sine_plot = SinePlot(width/2, height/2, width*2/3, height*2/3)
phaseSpace1DPlot = PhaseSpace1DPlot(width*1/3, height*3/4, height*1/2, height*1/2)
phaseSpace2DPlot = PhaseSpace2DPlot(width*2/3, height*3/4, height*1/2, height*1/2)


def render(c):
    sine_plot .render(c)
    if mode >= 2:
        phaseSpace1DPlot.render(c)
    if mode >= 3:
        phaseSpace2DPlot.render(c)
    ui_inst.render(c)


def update(c, deltaTime):
    global time
    time += deltaTime
    if time > 1:
        time = 0
    elif time < 0:
        time = 1

mode = 0
max_mode = 4

def on_set_mode():
    if mode < 2:
        sine_plot.centerx = width/2
        sine_plot.centery = height/2
        sine_plot.width = width*2/3
        sine_plot.height = height*2/3
    else:
        sine_plot.centerx = width/2
        sine_plot.centery = height/4
        #sine_plot.width = width*1/3
        sine_plot.height = height*2/5

    sine_plot.update_alignment()
        

on_set_mode()

def next_mode():
    global mode
    mode += 1
    if mode >= max_mode:
        mode = max_mode - 1
    on_set_mode()

def prev_mode():
    global mode
    mode -= 1
    if mode < 0:
        mode = 0
    on_set_mode()

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
                elif key == 'n':
                    next_mode()
                elif key == 'p':
                    prev_mode()

            sleep(1.0/20)
            update(c, 1.0/20 * speed.value) # FIXME: use clock.
            c.clear()

    finally:
        ui.cleanup_input()


if __name__ == '__main__':
    from sys import argv
    curses.wrapper(__main__)
