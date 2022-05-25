#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.colors as mc
import matplotlib.patches as mpatches
import numpy as np

import math
import re
import itertools
from collections import OrderedDict
from random import random, seed
import os
from datetime import datetime

from sys import argv, exit

from paperstyle import MARKERS, COLORS, IS_PDF, OUTFNAME, NOSHOW, FIGSIZE, hash_to_color

"""
Command to generate INDIR:

for f in $(ls /p/multifacet/users/markm/results2/frag-csl/fina.cs.wisc.edu/) ; do echo $f ; ls /tmp/fina-snapshots/$f.summary || (echo $f ;  /nobackup/kpageflags-snapshot-5.17/target/release/kpfsnapshot -f /p/multifacet/users/markm/results2/frag-csl/fina.cs.wisc.edu/$f/kpageflags.gz --gzip --ignore Active --ignore Dirty --ignore Referenced --ignore Private --summary | tee /tmp/fina-snapshots/$f.summary ) &  done
"""

# path to directory with summary files
INDIR=argv[1] + "/"

# file: {label: []}
data = { }
# file: {label: [[lower, upper]]}
errs = { }
# file: {label: memory}
mems = { }
ordered_labels = [ ]
ordered_fnames = sorted(os.listdir(INDIR))

def parse_mem(memstr):
    units = memstr[-2:]
    val = memstr[:-2]

    return int(val) * (1 << 10 if units == "MB" else 1)

for filename in os.listdir(INDIR):
    data[filename] = { }
    errs[filename] = { }
    mems[filename] = { }

    with open(INDIR + "/" + filename, "r") as file:
        for line in file.readlines():
            if "SUMMARY" in line or "TOTAL:" in line:
                continue

            parts = line.split()
            dist = parts[0:5]
            mem = parse_mem(parts[5])
            label = " ".join(parts[6:]).strip()
            label = label if len(label) > 0 else "None"

            p50 = int(dist[2])
            data[filename][label] = p50 # median
            # TODO: maybe plot min/max with scatter?
            #errs[filename][label] = [p50 - int(dist[1]),int(dist[3]) - p50] # 25%, 75%
            errs[filename][label] = [p50 - int(dist[0]),int(dist[4]) - p50] # min, max
            mems[filename][label] = mem

            ordered_labels.append(label)

ordered_labels = sorted(list(set(ordered_labels)))

# 2D array
#   ys[fname][label]
ys = []
# errs[fname][label][0 or 1 for lower/upper]
yerrs = []

for fname in ordered_fnames:
    vals = []
    evals = []
    for label in ordered_labels:
        y = data[fname][label] if label in data[fname] else 0
        e = errs[fname][label] if label in errs[fname] else [0, 0]
        vals.append(y)
        evals.append(e)
    ys.append(vals)
    yerrs.append(evals)

# transpose via python tricks
def transpose(arr2d):
    return [*zip(*arr2d)]

ys = transpose(ys)
yerrs = transpose(yerrs)

# calculate the max memory per label
maxmemlabel = { }

for i, label in enumerate(ordered_labels):
    maxmemlabel[label] = 0
    for file in ordered_fnames:
        m = mems[file][label] if label in mems[file] else 0
        maxmemlabel[label] = max(maxmemlabel[label], m)

maxmemall = max(maxmemlabel.values())

# lump together categories that consistently have less than 0.5% impact and leave out the error bars
to_remove = []
for i, label in enumerate(ordered_labels):
    if maxmemlabel[label] < maxmemall * 0.005:
        to_remove.append(label)

other = [0 for f in ordered_fnames]
for label_to_remove in to_remove:
    i = ordered_labels.index(label_to_remove)
    del ordered_labels[i]
    for j in range(len(ys[i])):
        other[j] = max(other[j], ys[i][j])
    del ys[i]
    del yerrs[i]

ordered_labels.append("Max Other")
ys.append(other)
yerrs.append([[0,0] for y in ys[0]])

# plot the figure

N = len(ordered_labels)

SCOLS = 2
SROWS = int(math.ceil(N / SCOLS))

print(N, SCOLS, SROWS)

#fig = plt.figure(1, figsize=FIGSIZE)
fig, axs = plt.subplots(SROWS, SCOLS, figsize=FIGSIZE, sharex="all", sharey="all")
axs = list(np.concatenate(axs).flat)

seed(0)

#colors = {label : hash_to_color(hash(label), 0.3) for label in ordered_labels}
colors = {label : hash_to_color(hash(label)) for label in ordered_labels}

#print(ys)
#print(yerrs)

dts = [datetime.strptime(fname, '%m-%d-%Y-%H-%M-%S.summary') for fname in ordered_fnames]
xs = [(dt - dts[0]).total_seconds() / (24. * 3600.) for dt in dts]

print(len(xs))
print(len(ys))
print(len(ys[0]))
print(ordered_labels)

plots = []

for li, label in enumerate(ordered_labels):
    #plt.subplot(N, 1, li + 1, sharex=ax)
    yerr = transpose(yerrs[li])
    #plt.errorbar(xs, ys[li], yerr=transpose(yerrs[li]), label=label, color=colors[label], capsize=1.0)
    h, = axs[li].plot(xs, ys[li], label=label, color=colors[label])
    plots.append(h)
    axs[li].plot(xs, yerr[0], label=label, color=colors[label], linestyle=':')
    #plots.append(h)
    axs[li].plot(xs, yerr[1], label=label, color=colors[label], linestyle='--')
    #plots.append(h)

#plt.xlabel("Time (days)")
fig.text(0.5, 0, "Time (days)", ha="center")
#plt.ylabel("Median, IRQ of contiguous chunk size (pages)")
fig.text(0, 0.5, "Median, IRQ of contiguous chunk size (order)", va="center", rotation="vertical")

plt.subplots_adjust(wspace=0.05, hspace=0.2)

plt.xticks(rotation=90)
plt.xlim((0, max(xs)))

plt.ylim((0, 2**10))
#plt.yscale("symlog", basey=2)
plt.yscale("symlog", base=2)
yticks = [2**i for i in np.arange(0, 11, 5)]
yticklabels = [str(i) for i in np.arange(0, 11, 5)]
plt.yticks(yticks, yticklabels)

#plt.grid(True)

labels = []
for l in ordered_labels:
    #for m in ["Median", "Min", "Max"]:
    for m in ["Median"]:
        labels.append(l + " " + m)
fig.legend(plots, labels, loc="lower left", bbox_to_anchor=(1, 0), ncol=1)
#plt.tight_layout()

plt.savefig("%s.%s" % (OUTFNAME, ("pdf" if IS_PDF else "png")), bbox_inches="tight")

if not NOSHOW:
    plt.show()
