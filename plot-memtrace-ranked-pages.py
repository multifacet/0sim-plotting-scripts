#!/usr/bin/env python3

from os import environ

if "NOX" in environ:
    import matplotlib
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np

from sys import argv, exit

from paperstyle import MARKERS, COLORS, IS_PDF, FIGSIZE

filename = argv[1]

data = []

with open(filename, 'r') as f:
    for line in f.readlines():
        parts = line.split()
        if len(parts) < 3:
            print("Skipping line %s" % line)
            continue
        freq = int(parts[1])
        data.append(freq)

NXTICKS = 10
NYTICKS = 10

if len(data) == 0:
    print("No data")
    exit(0)

ys = np.cumsum(data)

plt.figure(1, figsize=FIGSIZE)

plt.plot(ys)

xt = np.arange(0, len(data) * (1 + 1. / NXTICKS), len(data) / NXTICKS)
xl = [ int(i * (100 / NXTICKS)) for i in range(NXTICKS + 1)]
plt.xticks(ticks = xt, labels = xl)
plt.xlim((0, len(data)))

maxy = max(ys)
yt = np.arange(0, maxy * (1 + 1. / NYTICKS), maxy / NYTICKS)
yl = [ int(i * (100 / NYTICKS)) for i in range(NYTICKS + 1)]
plt.yticks(ticks = yt, labels = yl)
plt.ylim((0, maxy))

plt.ylabel("%% of memory accesses covered (out of %0.2E total)" % ys[-1])
plt.xlabel("% of memory TLB covers (ranked)")

plt.grid(True)

if "NOX" not in environ:
    plt.show()

plt.savefig('{}.ranked-pages.{}'.format(filename, "pdf" if IS_PDF else "png"), bbox_inches="tight")
