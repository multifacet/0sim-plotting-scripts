#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.transforms as transforms
import numpy as np

import re
import itertools
import random
import csv
from collections import OrderedDict
from cycler import cycler
from textwrap import fill

from sys import argv, exit
from os import environ

from paperstyle import FIGSIZE, IS_PDF, OUTFNAME, SMALL_PLOT

INFILE=argv[1]

TOTALBARWIDTH = 0.65

control = {}
data = {}

wklds = []
series = []

class Point:
    def __init__(self, mean, stdev, median, maxi, mini):
        self.mean = mean
        self.stdev = stdev
        self.median = median
        self.maxi = maxi
        self.mini = mini

    def normalize(self, control):
        self.mean = self.mean / control.mean
        self.median = self.median / control.median
        self.maxi = self.maxi / control.maxi
        self.mini = self.mini / control.mini

    def __repr__(self):
        return "mean=%f stdev=%f median=%f max=%f min=%f" % \
            (self.mean, self.stdev, self.median, self.maxi, self.mini)

# Read data
with open(INFILE, 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        mean = float(row["Mean"])
        stdev = float(row["Std"].replace("%", "")) / 100.
        median = float(row["Median"])
        maxi = float(row["Max"])
        mini = float(row["Min"])

        point = Point(mean, stdev, median, maxi, mini)

        wkld = row["workload"]
        kernel = row["kernel"]
        frag = row["fragmentation"] == "true"

        if kernel == "Linux":
            control[(wkld, frag)] = point
        else:
            data[(kernel, wkld, frag)] = point
            series.append((kernel, frag))

        wklds.append(wkld)


# Normalize against Linux 
for k, point in data.items():
    kernel, wkld, frag = k
    point.normalize(control[(wkld, frag)])

wklds = sorted(list(set(wklds)))
wklds = {w : i for i, w in enumerate(wklds)}
series = list(sorted(set(series), key=lambda s: (s[1], s[0])))

nseries = len(series)
barwidth = TOTALBARWIDTH / nseries

fig = plt.figure(figsize=FIGSIZE)

print(wklds)
print(series)

# horizontal dotted line at 1
horizontalxs = np.arange(len(wklds) + 2 * TOTALBARWIDTH) - TOTALBARWIDTH
horizontalys = np.array([1] * len(horizontalxs))
plt.plot(horizontalxs, horizontalys, color="black", lw=0.5, ls=":")

for i, (kernel, frag) in enumerate(series):
    ys = list(filter(lambda d: d[0] == kernel and d[2] == frag, data))

    xs = np.array(list(map(lambda d: wklds[d[1]], ys))) \
            - TOTALBARWIDTH / 2 + i * TOTALBARWIDTH / nseries \
            + TOTALBARWIDTH / nseries / 2

    ys = list(map(lambda d: data[d].median, ys))

    plt.bar(xs, ys,
            width=TOTALBARWIDTH / nseries, 
            label="%s%s" % (kernel, ", fragmented" if frag else ""),
            color="lightblue" if kernel == "CBMM" else "pink",
            hatch="///" if frag else None,
            edgecolor="black")

plt.ylabel("Normalized Runtime")

plt.xlim((0.5, len(wklds) - 0.5))
ticklabels = sorted(wklds, key=wklds.get)
plt.xticks(np.arange(len(wklds)) - 0.5, ticklabels,
        ha="center", rotation=-45.)
ticklabeltrans = transforms.ScaledTranslation(0.5, 0., fig.dpi_scale_trans)
for label in plt.gca().xaxis.get_majorticklabels():
    label.set_transform(label.get_transform() + ticklabeltrans)

plt.legend(bbox_to_anchor=(0.5, 1), loc="lower center", ncol=2)

plt.tight_layout()

plt.savefig("/tmp/%s.%s" % (OUTFNAME, "pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()

