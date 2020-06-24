#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

from paperstyle import COLORS, MARKERS, IS_PDF, FIGSIZE, LINE_STYLES, SLIDE_PLOT, HIDDEN

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

plt.figure(1, figsize=FIGSIZE)

colors = itertools.cycle(COLORS)
linestyles = itertools.cycle(LINE_STYLES)

handles = []

for label, xs in data.items():
    cdfx = np.sort(xs)
    cdfy = np.linspace(0.0, 100.0, len(xs))
    ls = '-' if SLIDE_PLOT else next(linestyles)
    if label in HIDDEN:
        ls = 'None'
        label = None
    lw = 3 if SLIDE_PLOT else 1
    h_plot, = plt.plot(cdfx, cdfy, label = label, linestyle = ls, linewidth=lw, marker = 'None', color = next(colors))
    handles.append(h_plot)

plt.legend(handles=handles, loc='upper left')

plt.xscale('log')

plt.ylim((0, 100))

plt.xlabel('Latency of Operations (%s)' % UNIT)
plt.ylabel("% of Operations")

plt.title('')

plt.grid(True)

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
