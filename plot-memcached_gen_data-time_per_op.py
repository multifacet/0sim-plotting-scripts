#!/usr/bin/env python2

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

from papercolors import MARKERS, COLORS

REGEX = r'^DONE [0-9]+ Duration { secs: ([0-9]+), nanos: ([0-9]+) }( [0-9]+)?$'

SCALE = 1E6
UNIT = 'msec'

VALUE_SIZE = 1 << 19

data = OrderedDict()

for arg in argv[1:]:
    label, filename = arg.split(":")
    data[label] = []

    with open(filename, 'r') as f:
        for line in f.readlines():
            m = re.match(REGEX, line)

            if m is None:
                print("ERROR: no match for line %s" % line)
                #exit(1)
                continue

            time = int(m.group(1)) * 1E9 + float(m.group(2))

            data[label].append(time / SCALE)

plt.figure(1, figsize=(5, 3.5))

markers = itertools.cycle(MARKERS)
colors = itertools.cycle(COLORS)

handles = []

def ops_to_gb(x):
    return x * 100. * VALUE_SIZE / (1 << 30)

for label, ys in data.items():
    xs = np.arange(len(ys))
    xs = map(ops_to_gb, xs)
    h_plot, = plt.plot(xs, ys, label = label, linestyle = 'None', marker = markers.next(), color = colors.next())
    handles.append(h_plot)

plt.legend(handles=handles)

plt.yscale('log')

plt.gca().set_xlim(left=0)
plt.gca().set_ylim(bottom=1)

plt.xlabel('Memory used (GB)')

plt.ylabel('Latency of Operations (%s)' % UNIT)

plt.grid(True)

#plt.savefig("/tmp/figure.pdf", bbox_inches="tight")
plt.savefig("/tmp/figure.png", bbox_inches="tight")
plt.show()
