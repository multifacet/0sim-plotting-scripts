#!/usr/bin/env python2

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

from paperstyle import COLORS, IS_PDF

data = OrderedDict()

def rdtsc_to_msec(ticks, freq):
    return ticks / float(freq)

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
                data[label].append(rdtsc_to_msec(v - prev, freq))
            j += 1
            prev = v

plt.figure(1, figsize=(5, 3.5))

colors = itertools.cycle(COLORS)

handles = []

for label, xs in data.items():
    xs = np.sort(xs)
    cdfx = np.cumsum(xs)
    cdfy = np.linspace(0.0, 100.0, len(xs))
    h_plot, = plt.plot(cdfx, cdfy, label = label, linestyle = '-', marker = 'None', color = colors.next())
    handles.append(h_plot)

plt.legend(handles=handles, loc='lower right')

plt.ylim((0, 100))

plt.gca().set_xlim(left=0)

plt.xlabel('Total Time Elapsed (msec)')

plt.ylabel("% of Operations")

plt.grid(True)

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
