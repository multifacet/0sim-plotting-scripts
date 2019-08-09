#!/usr/bin/env python2

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

from paperstyle import COLORS, IS_PDF, MARKERS, FIGSIZE

data = OrderedDict()

def rdtsc_to_usec(ticks, freq):
    return ticks / float(freq) * 1000.0

for arg in argv[1:]:
    label, filename, freq = arg.split(":")
    data[label] = []

    freq = int(freq) # KHz

    with open(filename, 'r') as f:
        first = int(f.readline()[8:].strip())
        last = int(f.readline()[7:].strip())

        # take only 1 in 10 data points. These are smooth curves so reducing
        # resolution shouldn't hurt. However, it will allow data to fit in
        # memory.
        j = 0
        prev = first
        for line in f.readlines():
            v = int(line.strip())
            if j % 100 == 0 and j > 0: # discard the first
                data[label].append(rdtsc_to_usec(v - prev, freq))
            j += 1
            prev = v

plt.figure(1, figsize=FIGSIZE)

markers = itertools.cycle(MARKERS)
colors = itertools.cycle(COLORS)

handles = []

for label, xs in data.items():
    cdfx = np.sort(xs)
    cdfy = np.linspace(0.0, 100.0, len(xs))
    mark_freq = [len(xs) / 10, -len(xs) / 10]
    h_plot, = plt.plot(cdfx, cdfy, label = label, linestyle = '-', marker = markers.next(), markevery=mark_freq, color = colors.next())
    handles.append(h_plot)

plt.legend(handles=handles, loc='lower right')

plt.ylim((0, 100))

plt.xscale('log')

plt.xlabel('$\Delta$ Time (usec)')

plt.ylabel("% of Operations")

plt.grid(True)

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
