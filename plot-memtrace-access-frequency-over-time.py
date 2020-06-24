#!/usr/bin/env python3

from os import environ

if "NOX" in environ:
    import matplotlib
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import sys

from math import log

filename = sys.argv[1]

# [[(addr, count, age)]]
data = []

with open(filename, "r") as f:
    tmp = []
    for line in f.readlines():
        if line.strip() == "===":
            data.append(tmp)
            tmp = []
        else:
            split = line.split()
            addr  = int(split[0], 16)
            #tmp.append((addr, int(split[1]), int(split[2])))
            tmp.append(int(split[1]))

# Collect info over time
p00 = []
p25 = []
p50 = []
p75 = []
p100= []

for dump in data:
    mi, lower, med, upper, ma = np.quantile(dump, [0, 0.25, 0.5, 0.75, 1])
    p00.append(mi)
    p25.append(lower)
    p50.append(med)
    p75.append(upper)
    p100.append(ma)

fig = plt.figure()

plt.plot(p50, 'k-')

xs = np.arange(len(p25))
plt.fill_between(xs, p00, p100, color="orange")
plt.fill_between(xs, p25, p75, color="red")

plt.yscale('log')

plt.ylabel("Access Frequency (i.e. $\lambda$)")
plt.xlabel('Time (# memory accesses, chunks of 1-billion accesses)')

plt.xlim(left=0)

legend = [Line2D([0], [0], color="black"),
          Line2D([0], [0], color="red", lw=8),
          Line2D([0], [0], color="orange", lw=8)]

plt.legend(legend, ['Median', 'Interquartile Range', 'Range'], loc="upper left")

plt.grid(True)

plt.tight_layout()

if "NOX" not in environ:
    plt.show()

plt.savefig('{}.dist.png'.format(filename))
