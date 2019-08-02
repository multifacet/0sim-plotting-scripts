#!/usr/bin/env python2

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

from paperstyle import COLORS, IS_PDF

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

colors = itertools.cycle(COLORS)

handles = []

for label, xs in data.items():
    cdfx = np.sort(xs)
    cdfy = np.linspace(0.0, 100.0, len(xs))
    h_plot, = plt.plot(cdfx, cdfy, label = label, linestyle = 'None', marker = markers.next(), color = colors.next())
    handles.append(h_plot)

plt.legend(handles=handles, loc='lower right')

plt.xscale('log')

plt.ylim((0, 100))

plt.xlabel('Latency of Operations (%s)' % UNIT)
plt.ylabel("% of Operations")

plt.grid(True)

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
