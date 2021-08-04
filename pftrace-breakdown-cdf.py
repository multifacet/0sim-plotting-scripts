#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
import random
from collections import OrderedDict
from cycler import cycler
from textwrap import fill

from sys import argv, exit
from os import environ

from paperstyle import FIGSIZE, IS_PDF, OUTFNAME, SMALL_PLOT

USAGE_STR = """
[FREQ=freq_mhz] ./script <stylesfile> <label> <P0> <P1> ... <P100> <label> <P0> <P1> ... <P100> ...
where <stylesfile> is a list of labels, one per line
"""

if len(argv[2:]) % 102 != 0:
    print("./Usage: %s" %  USAGE_STR)

FREQ = float(environ["FREQ"]) if "FREQ" in environ else None
NPLOTS = int(len(argv[2:]) / 102)

SHORTER_NAMES = {
        "HUGE_PAGE": "HUGE",
        "HUGE_ALLOC_FAILED": "HAFAIL",
        "HUGE_SPLIT": "HSPLT",
        "HUGE_PROMOTION_FAILED": "HPFAIL",
        "HUGE_PROMOTION": "HPROMO",
        "HUGE_COPY": "CPY",
        "CLEARED_MEM": "CLR",
        "ALLOC_FALLBACK_RETRY": "RTRY",
        "ALLOC_FALLBACK_RECLAIM": "RCLM",
        "ALLOC_FALLBACK_COMPACT": "CMPT",
        "ALLOC_FALLBACK": "FLBK",
        "ALLOC_PREZEROED": "PREZ",
        "ALLOC_NODE_RECLAIM": "SHRNK",
        "ZERO": "ZERO",
        "EXEC": "EXEC",
        "NUMA": "NUMA",
        "WP": "WP",
        }

LINESTYLES={} # label: (color, style)
with open(argv[1]) as f:
    labels = list(map(lambda x: x.strip(), f.readlines()))

    colormap = plt.cm.nipy_spectral
    styles = ['-', '--', ':', '-.']
    colors = [colormap(i) for i in np.linspace(0, 1, len(labels) / (len(styles) - 1))]
    combos = itertools.product(styles, colors)

    for (label, (style, color)) in zip(labels, combos):
        LINESTYLES[label] = (color, style)

def style(l):
    label = l.split("(")[0]
    return LINESTYLES[label]

def nice_label(raw):
    nice = raw.replace(",", ", ")
    nice = nice.replace("(", " (")
    n = 25 if SMALL_PLOT else 35
    nice = fill(nice, n)
    return nice

#CYCLER = (cycler(color=['r', 'g', 'b', 'y', 'c', 'm', 'k']) + cycler(linestyle=['-', '--', ':', '-.']))
#colormap = plt.cm.nipy_spectral
#colors = [colormap(i) for i in np.linspace(0, 1, NPLOTS)]
#styles = itertools.cycle(['-', '--', ':', '-.'])
#plt.gca().set_prop_cycle('color', colors)

plt.figure(figsize=FIGSIZE)

def shorten(l):
    out = l

    for b, a in SHORTER_NAMES.items():
        out = out.replace(b, a)

    return out

for i in range(NPLOTS):
    label = shorten(argv[2+i*102])
    xs = [float(x) for x in argv[2+i*102+1:2+(i+1)*102]]
    if FREQ is not None:
        xs = [x / FREQ for x in xs]
    ys = [y for y in range(0, 101)] # 0 ..= 100
    c, s = style(label)
    plt.plot(xs, ys, label=nice_label(label), color=c, linestyle=s)

    print(label.split("(")[0])

plt.xscale("symlog")
plt.xticks(rotation=90)
plt.xlabel("Latency (%s)" % ("cycles" if FREQ is None else "usec"))

plt.ylabel("Percentile")

plt.grid(True)

if environ.get("NOLEGEND") is None:
    plt.legend(bbox_to_anchor=(-0.05, 1.05), loc='lower left')
    #plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    #plt.legend(bbox_to_anchor=(-0.3, 1.05), loc='lower left')
else:
    plt.xlim((1, 1e6))

#plt.tight_layout()

plt.savefig("/tmp/%s.%s" % (OUTFNAME, ("pdf" if IS_PDF else "png")), bbox_inches="tight")
#plt.savefig("/tmp/%s.%s" % (OUTFNAME, ("pdf" if IS_PDF else "png")))
plt.show()
