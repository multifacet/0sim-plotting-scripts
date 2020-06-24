#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

from sys import argv, exit
from os import environ

USAGE = "Usage: [FREQ=freq_mhz] ./script is_exp min nbins width [too_low too_high bin0 bin1 ... name]... "

if len(argv) < 8:
    print(USAGE)
    exit(1)

FREQ = float(environ["FREQ"]) if environ["FREQ"] is not None else None

IS_EXP = argv[1] == "1"
MIN = int(argv[2])
NBINS = int(argv[3])
WIDTH = int(argv[4])

NDATASETS = int(len(argv[5:]) / (NBINS + 3))

data_labels = []
data = []
for i in range(NDATASETS):
    d = [int(argv[5 + i*(NBINS+3)])] # too_low
    # data..., too_high
    d += map(lambda x: int(x), argv[5 + i*(NBINS + 3) + 1 : 5 + (i+1)*(NBINS + 3) - 1])
    data.append(d)
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

# create some text bin labels for the plot.
labels = ["< {:.1f}".format(bin_upper_bounds[0])]
for (l, u) in zip(bin_lower_bounds, bin_upper_bounds):
    l = "[{:.1f}, {:.1f})".format(l, u)
    labels.append(l)
labels.append(">= {:.1f}".format(bin_upper_bounds[-1]))

# plot
TOTAL_WIDTH = 0.7
WIDTH = TOTAL_WIDTH / NDATASETS
x = np.arange(NBINS+2)

for (i, (d, l)) in enumerate(zip(data, data_labels)):
    plt.bar(x + WIDTH / 2 - TOTAL_WIDTH / 2 + i * WIDTH, d, label=l, width=WIDTH)

plt.xticks(x, labels, rotation=60, ha='right')
plt.yscale('log')

plt.ylabel("Number of Page Faults")
plt.xlabel("Page Fault Latency (%s)" % ("cycles" if FREQ is None else "usec"))

plt.legend()

plt.tight_layout()

plt.show()
