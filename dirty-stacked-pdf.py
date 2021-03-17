#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict
from cycler import cycler

from sys import argv, exit
from os import environ

from paperstyle import FIGSIZE, IS_PDF, OUTFNAME

USAGE_STR = "[FREQ=freq_mhz] ./script <label> <bin0>:<count0> <bin1>:<count1> ... <label> <bin>:<count>..."
if len(argv[1:]) < 3:
    print("./Usage: %s" %  USAGE_STR)

FREQ = float(environ["FREQ"]) if "FREQ" in environ else None

#CYCLER = (cycler(color=['r', 'g', 'b', 'y', 'c', 'm', 'k']) + cycler(linestyle=['-', '--', ':', '-.']))
colormap = plt.cm.nipy_spectral
colors = [colormap(i) for i in np.linspace(0, 1, len([0 for a in argv[1:] if "(" in a]))]
hatches = itertools.cycle(['///', '\\\\\\', '|||', '---', '+++', 'xxx', 'OOO', '...', '***'])
plt.gca().set_prop_cycle('color', colors)

plt.figure(figsize=(8,8))

args = list(argv[1:])
longest_xs = [] # shared xs
yss = [] # list of lists of ys
labels = []
while len(args) > 0:
    label = args.pop(0)
    assert("(" in label) # sanity check -- the name of each category should have the count in parens at the end

    xs = []
    ys = []
    while len(args) > 0 and  "(" not in args[0]:
        x,perc = args.pop(0).split(":")
        x = float(x)
        perc = float(perc)

        if FREQ is not None:
            x = x / FREQ

        xs.append(x)
        ys.append(perc)

    if len(xs) > len(longest_xs):
        longest_xs = xs
    yss.append(ys)
    labels.append(label)

# need to ensure all ys in yss have the same length
ys_maxlen = max(map(lambda ys: len(ys), yss))
for i in range(len(yss)):
    yss[i] += [0] * (ys_maxlen - len(yss[i]))

yss.reverse() # so heavier categories end up on the bottom -- easier to read
labels.reverse()
yss = np.row_stack(yss)
perc = yss / yss.sum().astype(float) * 100.0

stacks = plt.stackplot(longest_xs, perc, labels=labels)

for stack, hatch in zip(stacks, hatches):
    stack.set_hatch(hatch)

plt.xscale("symlog")
plt.xticks(rotation=90)
plt.xlabel("Latency (%s)" % ("cycles" if FREQ is None else "usec"))

plt.ylabel("Percent")
#plt.yscale("symlog")

plt.grid(True)

#plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.legend(bbox_to_anchor=(0, 1.05), loc='lower left')

plt.tight_layout()

plt.savefig("/tmp/%s.%s" % (OUTFNAME, ("pdf" if IS_PDF else "png")), bbox_inches="tight")
plt.show()
