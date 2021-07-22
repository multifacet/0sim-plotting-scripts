#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

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
[FREQ=freq_mhz] ./script <stylesfile> <which>
"""

if len(argv) < 3:
    print("./Usage: %s" %  USAGE_STR)
    exit(1)

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

def shorten(l):
    out = l

    for b, a in SHORTER_NAMES.items():
        out = out.replace(b, a)

    return out

WHICH=[]
with open(argv[2]) as f:
    labels = map(lambda x: x.strip(), f.readlines())
    WHICH = list(map(shorten, labels))

#CYCLER = (cycler(color=['r', 'g', 'b', 'y', 'c', 'm', 'k']) + cycler(linestyle=['-', '--', ':', '-.']))
#colormap = plt.cm.nipy_spectral
#colors = [colormap(i) for i in np.linspace(0, 1, NPLOTS)]
#styles = itertools.cycle(['-', '--', ':', '-.'])
#plt.gca().set_prop_cycle('color', colors)

plt.figure(figsize=FIGSIZE)

lines = []
for l in WHICH:
    c, s= style(l)
    line = Line2D([0], [0], color=c, ls=s)
    lines.append(line)

    #handle = plt.plot([1], [1], color=c, ls=s)[0]
    #lines.append(handle)

#plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
#plt.legend(bbox_to_anchor=(-0.3, 1.05), loc='lower left')
#plt.legend(bbox_to_anchor=(-0.05, 1.05), loc='lower left')

#plt.gca().get_xaxis().set_visible(False)
#plt.gca().get_yaxis().set_visible(False)
plt.gca().axis('off')

legend = plt.legend(lines, map(nice_label, WHICH), frameon=False, ncol=3, prop={'size': 8})
plt.tight_layout()

def export_legend(legend, filename):
    fig  = legend.figure
    fig.canvas.draw()
    bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi="figure", bbox_inches=bbox)

export_legend(legend, "/tmp/%s.%s" % (OUTFNAME, ("pdf" if IS_PDF else "png")))
#plt.savefig("/tmp/%s.%s" % (OUTFNAME, ("pdf" if IS_PDF else "png")))
plt.show()

