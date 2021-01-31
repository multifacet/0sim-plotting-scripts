#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import math

from sys import argv, exit
from os import environ

from paperstyle import FIGSIZE, IS_PDF

USAGE = "Usage: [FREQ=freq_mhz] ./script is_exp min nbins width [too_low too_high bin0 bin1 ... name]... "

if len(argv) < 8:
    print(USAGE)
    exit(1)

FREQ = float(environ["FREQ"]) if "FREQ" in environ else None
SIMPLE_X = "SIMPLE_X" in environ
PERCENTAGE_Y = "PERCENTAGE_Y" in environ

IS_EXP = argv[1] == "1"
MIN = int(argv[2])
NBINS = int(argv[3])
WIDTH = int(argv[4])

NDATASETS = int(len(argv[5:]) / (NBINS + 3))

sum_data = 0
data_labels = []
data = []
for i in range(NDATASETS):
    d = [int(argv[5 + i*(NBINS+3)])] # too_low
    # data..., too_high
    d += map(lambda x: int(x), argv[5 + i*(NBINS + 3) + 1 : 5 + (i+1)*(NBINS + 3) - 1])
    data.append(d)
    sum_data += sum(d)
    data_labels.append(argv[5 + (i+1)*(NBINS + 3)-1])

# compute the boundaries of each bin.
if IS_EXP: # exponential bins
    bin_lower_bounds = [MIN + (1<<i)*WIDTH for i in range(NBINS)]
    bin_upper_bounds = [MIN + (1<<(i+1))*WIDTH for i in range(NBINS)]

else: # linear bins
    bin_lower_bounds = [MIN + i*WIDTH for i in range(NBINS)]
    bin_upper_bounds = [MIN + (i+1)*WIDTH for i in range(NBINS)]

if FREQ is not None:
    bin_lower_bounds = list(map(lambda x: x / FREQ, bin_lower_bounds))
    bin_upper_bounds = list(map(lambda x: x / FREQ, bin_upper_bounds))

# plot
TOTAL_WIDTH = 0.7
WIDTH = TOTAL_WIDTH / NDATASETS
x = np.arange(NBINS+2)

plt.figure(figsize=FIGSIZE)

for (i, (d, l)) in enumerate(zip(data, data_labels)):
    if PERCENTAGE_Y:
        d = [float(d) / sum_data * 100.0 for d in d]
    plt.bar(x + WIDTH / 2 - TOTAL_WIDTH / 2 + i * WIDTH, d, label=l, width=WIDTH)

# create some text bin labels for the plot.
if SIMPLE_X:
    min_order = math.ceil(math.log10(bin_lower_bounds[0]))
    max_order = math.floor(math.log10(bin_lower_bounds[-1]))

    label_xs = [10**o for o in range(min_order, max_order+1)]

    width = math.log2(bin_upper_bounds[-1] - bin_lower_bounds[0])
    label_pos = [NBINS * math.log2(v / bin_lower_bounds[0]) / width for v in label_xs]

    def order_to_text(o):
        if o < 0:
            return "%d ns" % (10 ** (o+3))
        elif o < 3:
            return "%d us" % (10 ** o)
        elif o < 6:
            return "%d ms" % (10 ** (o-3))
        else:
            return "%d s" % (10 ** (o-6))

    labels = [order_to_text(o) for o in range(min_order, max_order+1)]

    plt.xticks(label_pos, labels, rotation=60, ha='right')

else:
    labels = ["< {:.1f}".format(bin_lower_bounds[0])]
    for (l, u) in zip(bin_lower_bounds, bin_upper_bounds):
        l = "[{:.1f}, {:.1f})".format(l, u)
        labels.append(l)
    labels.append(">= {:.1f}".format(bin_upper_bounds[-1]))

    plt.xticks(x, labels, rotation=60, ha='right')

plt.yscale('log')

if PERCENTAGE_Y:
    plt.ylabel("Percentage of Page Faults")
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(decimals=5))
else:
    plt.ylabel("Number of Page Faults")

if SIMPLE_X:
    plt.xlabel("Page Fault Latency")
else:
    plt.xlabel("Page Fault Latency (%s)" % ("cycles" if FREQ is None else "usec"))

plt.legend()

plt.tight_layout()

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
