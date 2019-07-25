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

fig, main_ax = plt.subplots()
fig.subplots_adjust(right=1.0 - 0.06 * (max(1, len(data) - 1)))

markers = itertools.cycle(MARKERS)

handles = []

new_ax = None

axes = []

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

for i, (label, ys) in enumerate(data.items()):
    if new_ax is None:
        new_ax = main_ax
    else:
        new_ax = main_ax.twinx()

    xs = np.arange(len(ys))
    h_plot, = new_ax.plot(xs, ys, label = label, linestyle = 'None', marker = markers.next(), color = np.random.rand(3,))

    if i >= 2:
        new_ax.spines["right"].set_position(("axes", 1 + 0.1 * (i-1)))
        make_patch_spines_invisible(new_ax)
        new_ax.spines["right"].set_visible(True)

    #new_ax.set_ylim((0,100000))

    handles.append(h_plot)
    axes.append(new_ax)

for m in mark:
    plt.axvline(x=m, color = 'red')

plt.legend(handles=handles)

#fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
