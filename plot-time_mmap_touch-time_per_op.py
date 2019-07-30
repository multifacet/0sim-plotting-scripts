#!/usr/bin/env python2

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

#FREQ = 3500000.0 # khz

MARKERS = ['.', '>', '<', '*', 'v', '^', 'D', 'X', 'P', 'p', 's']

#print("Assuming frequency is %d KHz" % FREQ)

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
                #data[label].append(v - prev)
            j += 1
            prev = v

plt.figure(1, figsize=(5, 3.5))

markers = itertools.cycle(MARKERS)

handles = []

def ops_to_gb(x):
    return float(x)*(1<<12) / (1 << 30) * 10

for label, ys in data.items():
    xs = np.arange(len(ys))
    xs = map(ops_to_gb, xs)
    h_plot, = plt.plot(xs, ys, label = label, linestyle = 'None', marker = markers.next())
    handles.append(h_plot)

plt.legend(handles=handles)

plt.gca().set_xlim(left=0)
plt.gca().set_ylim(bottom=0)

plt.xlabel('Memory Used (GB)')

plt.ylabel("Total Time Elapsed (msec)")
#plt.ylabel("Total Time Elapsed (cycles)")

plt.grid(True)

plt.savefig("/tmp/figure.png", bbox_inches="tight")
plt.show()
