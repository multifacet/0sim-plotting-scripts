#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
from matplotlib.font_manager import FontProperties

import re

from sys import argv, exit

from paperstyle import IS_PDF

FILE = argv[1]

INTERVAL = 30

RE = r'Node \d, zone\s+(DMA|DMA32|Normal)((\s+\d+)+)'

data = []

def parse_line(line):
    m = re.match(RE, line.strip())
    if m is None:
        print("No match: \"%s\"" % line)
        return

    vals = m.group(2)
    vals = map(int, vals.split())

    return vals

with open(FILE, 'r') as f:
    while True:
        dma_line = f.readline()

        if dma_line == '':
            break

        dma32_line = f.readline()
        normal_line = f.readline()

        dma_vals = parse_line(dma_line)
        dma32_vals = parse_line(dma32_line)
        normal_vals = parse_line(normal_line)

        total_vals = [sum(x) for x in zip(dma_vals, dma32_vals, normal_vals)]

        data.append(total_vals)

x = np.arange(len(data)) * INTERVAL
x = x / 3600

# normalize all values to get percentages
def normalize(sample):
    total = sum(sample)
    return [s * 100. / total for s in sample]

# get the amount of free memory
def nfree(sample):
    # num free pages
    total = 0
    for (order, n) in enumerate(sample):
        total += n << order

    # convert to GB
    total <<= 12 # bytes
    total = float(total) / (1 << 30)

    return total

ndata = list(map(normalize, data))
tdata = list(map(nfree, data))

ndata_transpose = [*zip(*ndata)]

labels = ["Order %d" % i for i in range(len(data[0]))]

colors = cm.rainbow(np.linspace(1, 0, len(labels)))

plt.figure(1, figsize=(5, 3.5))
gs = mpl.gridspec.GridSpec(2, 2, height_ratios = [6, 1], width_ratios = [20, 1], wspace = 0.05, hspace = 0.07)

# main plot

ax0 = plt.subplot(gs[0, 0])

ax0.stackplot(x, *ndata_transpose, labels=labels, colors=colors)

ax0.set_ylabel("% of Free Pages")
ax0.set_ylim((0, 100))

plt.setp(ax0.get_xticklabels(), visible=False)

ax0.grid(True)

# Color bar

cbax = plt.subplot(gs[0, 1])

bounds = np.arange(0, len(labels), 1)
ticks = list(range(0, len(labels), 4)) + [len(labels)-1]
cmap = mpl.colors.ListedColormap(cm.rainbow(np.linspace(1, 0, len(labels))))
norm = mpl.colors.Normalize(vmin=-0.5, vmax=len(labels)-0.5)
cb = mpl.colorbar.ColorbarBase(cbax, cmap=cmap, norm=norm, ticks=ticks, spacing='proportional', orientation='vertical')
cb.set_label('Free List Order')

# little plot with # pages

ax1 = plt.subplot(gs[1, 0], sharex = ax0)

ax1.plot(x, tdata, color="k")

ax1.set_xlabel("Time (hours)")
ax1.set_xlim((0, max(x)))
ax1.set_ylabel("Free Phys\nMem (GB)")

plt.grid(True)

# save and show
plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
