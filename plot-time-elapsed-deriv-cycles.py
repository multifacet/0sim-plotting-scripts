#!/usr/bin/env python2

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

from paperstyle import MARKERS, COLORS, IS_PDF

data = OrderedDict()

mark = set([])

for arg in argv[1:]:
    label = arg
    filename = arg
    snd_filename = None
    if ":" in arg:
        spl = arg.split(":")
        if len(spl) == 2:
            label, filename = spl
        else:
            label, filename, snd_filename = spl
    data[label] = []

    with open(filename, 'r') as f:
        for line in f.readlines():
            try:
                val = float(line.strip().replace(',', ''))
                data[label].append(val)
            except ValueError:
                print("bad float: %s" % line)

            if line[0] == '=':
                mark.add(len(data[label]))


    if snd_filename is not None:
        mark.add(len(data[label]))

        with open(snd_filename, 'r') as f:
            for line in f.readlines():
                try:
                    val = float(line.strip().replace(',', ''))
                    data[label].append(val)
                except ValueError:
                    print("bad float: %s" % line)

                if line[0] == '=':
                    mark.add(len(data[label]))

plt.figure(1, figsize=(5, 3.5))

markers = itertools.cycle(MARKERS)
colors = itertools.cycle(COLORS)

handles = []

for i, (label, ys) in enumerate(data.items()):
    ys = np.diff(ys)
    xs = np.arange(len(ys))
    h_plot, = plt.plot(xs, ys, label = label, linestyle = 'None', marker = markers.next(), color = colors.next())

    handles.append(h_plot)

for m in mark:
    plt.axvline(x=m, color = 'red')

plt.gca().set_xlim(left=0)
plt.gca().set_ylim(bottom=1)

plt.yscale('log')

plt.ylabel("$\Delta$ Time (cycles)")
plt.xlabel("Operation Number")

plt.legend(handles=handles)

plt.grid(True)

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
