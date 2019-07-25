#!/usr/bin/env python2

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

MARKERS = ['.', '>', '<', '*', 'v', '^', 'D', 'X', 'P', 'p', 's']

data = OrderedDict()

mark = []

for arg in argv[1:]:
    label = arg
    filename = arg
    if ":" in arg:
        label, filename = arg.split(":")
    data[label] = []

    with open(filename, 'r') as f:
        for line in f.readlines():
            try:
                val = float(line.strip().replace(',', ''))
                data[label].append(val)
            except ValueError:
                print("bad float: %s" % line)

            if line[0] == '=':
                mark.append(len(data[label]))

fig, ax = plt.subplots()

markers = itertools.cycle(MARKERS)

handles = []

for i, (label, ys) in enumerate(data.items()):
    xs = np.arange(len(ys))
    h_plot, = ax.plot(xs, ys, label = label, linestyle = 'None', marker = markers.next(), color = np.random.rand(3,))

    handles.append(h_plot)

for m in mark:
    plt.axvline(x=m, color = 'red')

#ax.set_ylim((0,100000))

plt.legend(handles=handles)

#fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
