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

# Read data
with open(INFILE, 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        efficiency = float(row["Efficiency"])

        wkld = row["workload"]
        kernel = row["kernel"]
        frag = row["fragmentation"].lower() == "true"

        data[(kernel, wkld, frag)] = efficiency
        series.append((kernel, frag))

        wklds.append(wkld)


wklds = sorted(list(set(wklds)))
wklds = {w : i for i, w in enumerate(wklds)}
series = list(sorted(set(series), key=lambda s: (s[1], s[0])))

nseries = len(series)
barwidth = TOTALBARWIDTH / nseries

fig = plt.figure(figsize=FIGSIZE)

print(wklds)
print(series)

for i, (kernel, frag) in enumerate(series):
    ys = list(filter(lambda d: d[0] == kernel and d[2] == frag, data))

    xs = np.array(list(map(lambda d: wklds[d[1]], ys))) \
            - TOTALBARWIDTH / 2 + i * TOTALBARWIDTH / nseries \
            + TOTALBARWIDTH / nseries / 2

    ys = list(map(lambda d: data[d], ys))

    if kernel == "CBMM":
        color = "lightblue"
    elif kernel == "Hawkeye":
        color = "pink"
    else:
        color = "yellow"

    print(kernel + " " + color)

    plt.bar(xs, ys,
            width=TOTALBARWIDTH / nseries, 
            label="%s%s" % (kernel, ", fragmented" if frag else ""),
            color=color,
            hatch="///" if frag else None,
            edgecolor="black")

plt.ylabel("Huge Page Usage")

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

