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

plt.figure(1, figsize=(5, 3.5))

markers = itertools.cycle(MARKERS)

handles = []

for i, (label, ys) in enumerate(data.items()):
    ys = np.diff(ys)
    xs = np.arange(len(ys))
    h_plot, = plt.plot(xs, ys, label = label, linestyle = 'None', marker = markers.next(), color = np.random.rand(3,))

    handles.append(h_plot)

for m in mark:
    plt.axvline(x=m, color = 'red')

plt.yscale('log')

plt.ylabel("Time Elapsed (cycles)")
plt.xlabel("Operation Number")

plt.legend(handles=handles)

plt.savefig("/tmp/figure.pdf", bbox_inches="tight")
plt.show()
