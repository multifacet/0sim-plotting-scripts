#!/usr/bin/env python3

from os import environ

if "NOX" in environ:
    import matplotlib
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np

from sys import argv, exit

filename = argv[1]

MARKER_LINE = "Histogram of # averted TLB misses (# averted: frequency):"

data = {}

start = False

with open(filename, 'r') as f:
    for line in f.readlines():
        if line.strip() == MARKER_LINE:
            start = True
            continue

        if not start:
            continue

        a, f = line.split()
        data[int(a)] = int(f)

if len(data) == 0:
    print("no data")
    exit(0)

xs = []
ys = []

for n in range(min(data.keys()), max(data.keys()) + 1):
    if n in data:
        xs.append(n)
        ys.append(data[n])
    else:
        xs.append(n)
        ys.append(0)

plt.plot(xs, ys)

plt.yscale('symlog')
plt.xscale('symlog')

plt.xlim(left = 0)
plt.ylim(bottom = 0)

plt.xlabel("Number of Averted TLB misses")
plt.ylabel("Number of Huge Pages")

if "NOX" not in environ:
    plt.show()

plt.savefig('{}.averted.png'.format(filename))
