#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.ticker import MultipleLocator

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

MOVING_AVERAGE_WINDOW=1

XBUFFER=2

control = None
data = []

with open(INFILE, 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        start = row["Start"]
        load_walk_active = float(row["dtlb_load_misses.walk_active:u"])
        store_walk_active = float(row["dtlb_store_misses.walk_active:u"])
        cpu_unhalted = float(row["cpu_clk_unhalted.thread_any:u"])
        runtime = float(row["Runtime (s)"])

        if start == "none":
            control = (load_walk_active, store_walk_active, cpu_unhalted, runtime)
            continue

        if start == "thp":
            continue

        data.append((load_walk_active, store_walk_active, cpu_unhalted, runtime))

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

#normalized_runtime = moving_average([d[3] / control[3] * 100. for d in data], MOVING_AVERAGE_WINDOW)
#store_walk_cycles = moving_average([100 - (control[1] / control[2] - d[1] / d[2])*100. for d in data], MOVING_AVERAGE_WINDOW)
#load_walk_cycles = moving_average([100 - (control[0] / control[2] - d[0] / d[2])*100. for d in data], MOVING_AVERAGE_WINDOW)

normalized_runtime = moving_average([d[3] / control[3] * 100. - 100. for d in data], MOVING_AVERAGE_WINDOW)
store_walk_cycles = moving_average([(d[1] / d[2] - control[1] / control[2])*100. for d in data], MOVING_AVERAGE_WINDOW)
load_walk_cycles = moving_average([(d[0] / d[2] - control[0] / control[2])*100. for d in data], MOVING_AVERAGE_WINDOW)

#store_walk_cycles = moving_average([((d[1] / d[2]) / (control[1] / control[2]))*100. for d in data], MOVING_AVERAGE_WINDOW)
#load_walk_cycles = moving_average([((d[0] / d[2]) / (control[0] / control[2]))*100. for d in data], MOVING_AVERAGE_WINDOW)

xs = np.arange(0, len(normalized_runtime))

#fig, ax1 = plt.subplots()
#ax2 = ax1.twinx()
plt.figure(figsize=FIGSIZE)
#fig, axs = plt.subplots(2)
gs = gridspec.GridSpec(2, 1)
gs.update(wspace=0.025, hspace=0.05)
#ax1 = axs[0]
#ax2 = axs[1]
ax1 = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])

ax1.plot(xs, [0]*len(xs), color="black", lw=0.5, ls=":")
ax2.plot(xs, [0]*len(xs), color="black", lw=0.5, ls=":")
#ax1.plot(xs, [100]*len(xs), color="black", lw=0.5, ls=":")
#ax2.plot(xs, [100]*len(xs), color="black", lw=0.5, ls=":")

ax1.plot(normalized_runtime, color=(179/255., 167/255., 39/255.), label="Runtime")
ax1.set_ylabel("Norm.\nRuntime")

ax2.plot(store_walk_cycles, color="red", label = "Store Walk Cycles")
ax2.plot(load_walk_cycles, color="blue", label = "Load Walk Cycles")
ax2.set_ylabel("Norm. Page\nWalk Cycles")

ax1.set_xlim((0 - XBUFFER, len(xs)+XBUFFER))
ax2.set_xlim((0 - XBUFFER, len(xs)+XBUFFER))

ax1.get_xaxis().set_visible(False)
#ax1.set_ylim(top=105)

ax2.set_xlabel("Address Range")
#ax2.get_xaxis().set_ticks([])
#ax2.set_ylim(bottom=0)
ax2.set_xticks(np.arange(101), minor=True)

#ax1.yaxis.get_major_formatter().set_scientific(False)
#ax2.yaxis.get_major_formatter().set_scientific(False)
ax1.ticklabel_format(useOffset=False, style='plain')
ax2.ticklabel_format(useOffset=False, style='plain')
ax1.yaxis.set_label_position("right")
ax2.yaxis.set_label_position("right")

#plt.figlegend()

plt.tight_layout()

plt.savefig("/tmp/%s.%s" % (OUTFNAME, "pdf" if IS_PDF else "png"), bbox_inches="tight")
#plt.show()
