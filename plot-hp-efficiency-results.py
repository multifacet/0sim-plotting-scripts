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

#WORKLOAD_ORDER=["mcf", "xz", "canneal", "thp-ubmk", "memcached", "mongodb", "mix"]
#WORKLOAD_ORDER=["mcf", "xz", "canneal", "memcached", "mongodb", "mix"]
KERNEL_ORDER=["Linux", "HawkEye", "CBMM"]

control = {}
data = {}

wklds = []
kernels = []
series = []

# Read data
with open(INFILE, 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        efficiency = float(row["Efficiency"])

        wkld = row["workload"]
        kernel = row["kernel"]
        frag = row["fragmentation"].lower() == "fragmented"

        #if not frag:
        #    continue
        #else:
        #    frag = False

        data[(kernel, wkld, frag)] = efficiency * 100.0
        series.append((wkld, frag))

        kernels.append(kernel)


kernels = sorted(list(set(kernels)), key = lambda k: KERNEL_ORDER.index(k))
kernels = {k : i for i, k in enumerate(kernels)}
series = list(sorted(set(series), key=lambda s: (s[1], s[0])))

nseries = len(series)
barwidth = TOTALBARWIDTH / nseries

fig = plt.figure(figsize=FIGSIZE)

print(kernels)
print(series)

for i, (wkld, frag) in enumerate(series):
    ys = list(filter(lambda d: d[1] == wkld and d[2] == frag, data))

    xs = np.array(list(map(lambda d: kernels[d[0]], ys))) \
            - TOTALBARWIDTH / 2 + i * TOTALBARWIDTH / nseries \
            + TOTALBARWIDTH / nseries / 2

    ys = list(map(lambda d: data[d], ys))

    if wkld == "canneal":
        color = "blue"
    elif wkld == "mcf":
        color = "orange"
    elif wkld == "memcached":
        color = "green"
    elif wkld == "mix":
        color = "red"
    elif wkld == "mongodb":
        color = "purple"
    else:
        color = "brown"

    #if frag:
    #    ys = [0 for y in ys]

    plt.bar(xs, ys,
            width=TOTALBARWIDTH / nseries, 
            label="%s%s" % (wkld, ", fragmented" if frag else ""),
            color=color,
            hatch="///" if frag else None,
            edgecolor="black")

plt.ylabel("% Backed by Huge Pages")

#plt.xlim((0.5, len(wklds) + 1 - 0.5))
plt.xlim((0.5, len(kernels)  - 0.5))
ticklabels = sorted(kernels, key=kernels.get)
plt.xticks(np.arange(len(kernels)) - 0.5, ticklabels,
        ha="center", rotation=-45.)
ticklabeltrans = transforms.ScaledTranslation(0.5, 0., fig.dpi_scale_trans)
for label in plt.gca().xaxis.get_majorticklabels():
    label.set_transform(label.get_transform() + ticklabeltrans)

if environ.get("NOLEGEND") is None:
    plt.legend(bbox_to_anchor=(0.5, 1), loc="lower center", ncol=2)

plt.grid()

plt.tight_layout()

plt.savefig("/tmp/%s.%s" % (OUTFNAME, "pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()

