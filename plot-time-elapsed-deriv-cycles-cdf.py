#!/usr/bin/env python2

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

from paperstyle import MARKERS, COLORS, IS_PDF

data = OrderedDict()
data1 = OrderedDict()

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
    data1[label] = []

    with open(filename, 'r') as f:
        for line in f.readlines():
            try:
                val = float(line.strip().replace(',', ''))
                data[label].append(val)
            except ValueError:
                print("bad float: %s" % line)

    if snd_filename is not None:
        with open(snd_filename, 'r') as f:
            for line in f.readlines():
                try:
                    val = float(line.strip().replace(',', ''))
                    data1[label].append(val)
                except ValueError:
                    print("bad float: %s" % line)

plt.figure(1, figsize=(5, 3.5))

markers = itertools.cycle(MARKERS)
colors = itertools.cycle(COLORS)

handles = []

for i, (label, xs) in enumerate(data.items()):
    xs = np.diff(xs)
    before = len(xs)
    xs = filter(lambda x: x > 0, xs) # TODO
    after = len(xs)
    print(label, before - after)
    cdfx = np.sort(xs)
    cdfy = np.linspace(0.0, 100.0, len(xs))

    h_plot, = plt.plot(cdfx, cdfy, label = "%s-local" % label, linestyle = '-', marker = 'None', color = colors.next())

    handles.append(h_plot)

markers = itertools.cycle(MARKERS)
colors = itertools.cycle(COLORS)

for i, (label, xs) in enumerate(data1.items()):
    xs = np.diff(xs)
    before = len(xs)
    xs = filter(lambda x: x > 0, xs) # TODO
    after = len(xs)
    print(label, before - after)
    cdfx = np.sort(xs)
    cdfy = np.linspace(0.0, 100.0, len(xs))

    if len(xs) > 0:
        h_plot, = plt.plot(cdfx, cdfy, label = "%s-nonlocal" % label, linestyle = '--', marker = 'None', color = colors.next())
        handles.append(h_plot)

plt.ylim((0, 100))

plt.xscale('log')

plt.ylabel("% of Measurements")
plt.xlabel("$\Delta$ Time (cycles)")

plt.legend(handles=handles, loc='lower right')

plt.grid(True)

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
