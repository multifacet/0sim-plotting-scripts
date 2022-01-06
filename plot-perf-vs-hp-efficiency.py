#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.transforms as transforms
import numpy as np

import re
import itertools
import random
import csv
import copy
from collections import OrderedDict
from cycler import cycler
from textwrap import fill

from sys import argv, exit
from os import environ

from paperstyle import FIGSIZE, IS_PDF, OUTFNAME, SMALL_PLOT

PERF_FILE = argv[1]
HP_EFF_FILE = argv[2]

COLORS = {"Linux": "yellow", "CBMM": "blue", "HawkEye": "red"}
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
        self.efficiency = 0

    def normalize(self, control):
        self.mean = self.mean / control.mean
        self.median = self.median / control.median
        self.maxi = self.maxi / control.maxi
        self.mini = self.mini / control.mini

    def __repr__(self):
        return "mean=%f stdev=%f median=%f max=%f min=%f" % \
            (self.mean, self.stdev, self.median, self.maxi, self.mini)

# Read data
with open(PERF_FILE, 'r') as f:
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

        if wkld == "thp-ubmk" or kernel == "Linux4.3":
            continue

        #if not frag:
        #    continue
        #else:
        #    frag = False

        if kernel == "Linux":
            control[(wkld, frag)] = copy.deepcopy(point)

        data[(kernel, wkld, frag)] = point
        series.append((kernel, frag))

        wklds.append(wkld)

with open(HP_EFF_FILE, 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        efficiency = float(row["Efficiency"])

        wkld = row["workload"]
        kernel = row["kernel"]
        frag = row["fragmentation"].lower() == "fragmented"

        data[(kernel, wkld, frag)].efficiency = efficiency

# Normalize against unfragmented Linux
for k, point in data.items():
    kernel, wkld, frag = k
    #point.normalize(control[(wkld, frag)])
    point.normalize(control[(wkld, False)])
    #print(kernel, wkld, frag, point)

fig = plt.figure(figsize=FIGSIZE)

series = list(sorted(set(series), key=lambda s: (s[1], s[0])))

for i, (kernel, frag) in enumerate(series):
    cur_kernel = list(filter(lambda d: d[0] == kernel and d[2] == frag, data))
    ys = list(map(lambda d: data[d].median, cur_kernel))
    xs = list(map(lambda d: data[d].efficiency, cur_kernel))

    plt.scatter(xs, ys,
        label="%s%s" % (kernel, ", fragmeneted" if frag else ""),
        marker = "X" if frag else "o",
        color = COLORS[kernel])

# horizontal dotted line at 1
horizontalxs = [-1, 0, 2]
horizontalys = np.array([1] * len(horizontalxs))
plt.plot(horizontalxs, horizontalys, color="black", lw=0.5, ls=":")

plt.ylabel("Normalized Runtime")
plt.ylim((0, 2.5))

plt.xlabel("% Backed by Huge Pages")
plt.xlim((-0.01, 1.01))

if environ.get("NOLEGEND") is None:
    plt.legend(bbox_to_anchor=(0.5, 1), loc="lower center", ncol=2)

plt.savefig("/tmp/%s.%s" % (OUTFNAME, "pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
