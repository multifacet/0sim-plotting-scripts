#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.colors as mc
import matplotlib.patches as mpatches
import numpy as np

import re
import itertools
from collections import OrderedDict
from random import random, seed

from sys import argv, exit

from paperstyle import MARKERS, COLORS, IS_PDF, FIGSIZE

INFILE=argv[1]

# READ/PARSE DATA

all_flags = {}
data = []

with open(INFILE, "r") as f:
    for line in f.readlines():
        if "SUMMARY" in line:
            break

        parts = line.split()
        pfns, size, flags = parts[0], parts[1], parts[2:]

        if "-" in pfns:
            start, end = pfns.split("-")
            start, end = int(start, 16), int(end, 16)
        else:
            start, end = int(pfns, 16), int(pfns, 16)

        flags = " ".join((str(f.strip()) for f in flags))
        flags = flags.replace("CompoundHead", "Compound")
        flags = flags.replace("CompoundTail", "Compound")
        if flags not in all_flags:
            all_flags[flags] = len(all_flags)

        data.append((start, end, size, flags))

print(all_flags)

# PLOT

plt.figure(1, figsize=FIGSIZE)

seed(0)

colors = [(1,1,1)] + [(random(),random(),random()) for i in range(len(all_flags))]
new_map = mc.LinearSegmentedColormap.from_list('new_map', colors, N=len(all_flags))

flattened = []
for start, end, size, flags in data:
    npages = end - start + 1
    fi = all_flags[flags]

    flattened += [float(fi)] * npages

# complete the last GB
flattened += [float(all_flags["Nopage"])] * (512 * 512 - len(flattened) % (512 * 512))
flattened = np.reshape(flattened, (-1, 512 * 512))

# plot
plt.imshow(flattened, interpolation='none', aspect='auto', cmap=new_map)

plt.xlabel("Page within gigabyte (PFN mod $2^{18}$)")
plt.ylabel("Gigabyte of physical memory (PFN / $2^{18}$)")

# build legend
legend_handles = []
for flags, fi in all_flags.items():
    p = mpatches.Patch(color=new_map(fi), label="[%d] %s" % (fi, flags))
    legend_handles.append(p)
plt.legend(handles=legend_handles, fontsize=8, ncol=2, loc='lower center', bbox_to_anchor=(0.5, 1))

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
