#!/usr/bin/python3

import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation

try:
    import dgi
except ImportError as e:
    import os, sys
    libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')
    sys.path.append(libdir)
    import dgi

# samples from XAM come in at 16kHz; we use a moving average to produce
# a smoothed measure at a lower rate and then show 10 seconds of data
# graph is updated only fast enough to ensure smooth scrolling

WINDOW     = 160
POINTS_SEC = 16000 // WINDOW
POINTS     = 10 * POINTS_SEC
REFRESH    = 33 # redraw graph this many times per second

window = collections.deque([]*WINDOW,WINDOW)
points = collections.deque([float('nan')]*POINTS,POINTS)

fig, ax = plt.subplots()
line, = ax.plot([0,]*POINTS)
ax.set_ylim(0,10000) # set y scale from 0 to 10mA

with dgi.DGI() as dev:
    power = dev.power()

    def update(data):
        line.set_ydata(data)
        return line,

    def data_gen():
        window_count = 0
        points_count = 0
        for sample_type, sample in power.poll():
            if sample_type == 'PRI':
                window.append(sample)
                window_count += 1
                if window_count == WINDOW:
                    # we update the graph at 16000 / WINDOW Hz
                    window_count = 0
                    points.append(sum(window)/WINDOW)
                    points_count += 1
                    if points_count == POINTS_SEC // REFRESH:
                        points_count = 0
                        yield points

    ani = animation.FuncAnimation(fig, update, data_gen, interval=0, blit=True)
    plt.show()
