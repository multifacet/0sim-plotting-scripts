#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.colors as mc
import matplotlib.patches as mpatches
import numpy as np

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

# file: {label: kb}
data = { }
ordered_labels = [ ]
ordered_fnames = sorted(os.listdir(INDIR))
max_y = 0

def parse_mem(memstr):
    units = memstr[-2:]
    val = memstr[:-2]

    return int(val) * (1 << 10 if units == "MB" else 1)

for filename in os.listdir(INDIR):
    data[filename] = { }

    with open(INDIR + filename, "r") as file:
        for line in file.readlines():
            if "SUMMARY" in line or "TOTAL:" in line:
                continue

            parts = line.split()
            dist = parts[0:4]
            mem = parse_mem(parts[5])
            label = " ".join(parts[6:]).strip()
            label = label if len(label) > 0 else "None"

            data[filename][label] = float(mem) / (1 << 20)

            ordered_labels.append(label)

    max_y = max(max_y, sum(data[filename].values()))

ordered_labels = sorted(list(set(ordered_labels)))

# 2D array
#   ys[fname][label]
ys = []

for fname in ordered_fnames:
    vals = []
    for label in ordered_labels:
        y = data[fname][label] if label in data[fname] else 0
        vals.append(y)
    ys.append(vals)

# transpose via python tricks
ys = [*zip(*ys)]

# lump together categories that consistently have less than 0.5% impact
to_remove = []
for i, label in enumerate(ordered_labels):
    freqenough = False
    for j in range(len(ordered_fnames)):
        if ys[i][j] >= max_y * 0.005:
            freqenough = True
    if not freqenough:
        to_remove.append(label)

other = [0 for f in ordered_fnames]
for label_to_remove in to_remove:
    i = ordered_labels.index(label_to_remove)
    del ordered_labels[i]
    for j in range(len(ys[i])):
        other[j] += ys[i][j]
    del ys[i]

ordered_labels.append("Other")
ys.append(other)

# plot the figure

plt.figure(1, figsize=FIGSIZE)

seed(0)

colors = [hash_to_color(hash(label)) for label in ordered_labels]

#print(ys)

dts = [datetime.strptime(fname, '%m-%d-%Y-%H-%M-%S.summary') for fname in ordered_fnames]
xs = [(dt - dts[0]).total_seconds() / (24. * 3600.) for dt in dts]

print(len(xs))
print(len(ys))
print(len(ys[0]))
print(ordered_labels)

plt.stackplot(xs, ys, baseline="zero", labels=ordered_labels, colors=colors, edgecolor="black")

plt.xlabel("Time (days)")
plt.ylabel("Physical Memory (GB)")

plt.xlim((0, max(xs)))
plt.ylim((0, max_y))

plt.xticks(rotation=90)

plt.grid(True)

plt.legend(loc="lower left", bbox_to_anchor=(0, 1.05), ncol=2)
#plt.tight_layout()

plt.savefig("%s.%s" % (OUTFNAME, ("pdf" if IS_PDF else "png")), bbox_inches="tight")

if not NOSHOW:
    plt.show()
