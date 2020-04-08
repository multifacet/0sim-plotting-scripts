#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

from sys import argv, exit
from os import environ

from paperstyle import FIGSIZE

USAGE = "Usage: [FREQ=freq_mhz] ./script is_exp min nbins width file \n where file = [too_low too_high bin0 bin1 ... name]... \\n [too_low too_high bin0 bin1 ... name]..."

if len(argv) < 6:
    print(USAGE)
    exit(1)

INTERVAL = 200

FREQ = float(environ["FREQ"]) if "FREQ" in environ else None

IS_EXP = argv[1] == "1"
MIN = int(argv[2])
NBINS = int(argv[3])
WIDTH = int(argv[4])
FILE = argv[5]

def parse_dataset(raw):
    raw = raw.split()
    NDATASETS = int(len(raw) / (NBINS + 3))

    max_val = 0
    data_labels = []
    data = []
    for i in range(NDATASETS):
        d = [int(raw[i*(NBINS+3)])] # too_low
        # data..., too_high
        d += map(lambda x: int(x), raw[i*(NBINS + 3) + 1 : (i+1)*(NBINS + 3) - 1])
        max_val = max(max_val, max(d))
        data.append(d)
        data_labels.append(raw[(i+1)*(NBINS + 3)-1])

    return (data, data_labels, max_val)

data_labels = []
data_per_step = []
n = 0
max_all = 0
NDATASETS = 0

with open(FILE, 'r') as f:
    for line in f.readlines():
        (data, dl, max_val) = parse_dataset(line.strip())
        NDATASETS = len(data)
        data_labels = dl
        max_all = max(max_all, max_val)
        n += 1
        data_per_step.append(data)

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

# Actually plot now
fig = plt.figure(1, figsize=FIGSIZE)

bars = []

TOTAL_WIDTH = 0.7
WIDTH = TOTAL_WIDTH / NDATASETS
x = np.arange(NBINS+2)

for (i, (d, l)) in enumerate(zip(data, data_labels)):
    bar = plt.bar(x + WIDTH / 2 - TOTAL_WIDTH / 2 + i * WIDTH, d, label=l, width=WIDTH)
    bars.append(bar)

plt.xticks(x, labels, rotation=60, ha='right')
plt.yscale('symlog')

plt.ylabel("Number of Page Faults")
plt.xlabel("Page Fault Latency (%s)" % ("cycles" if FREQ is None else "usec"))

plt.legend()

plt.ylim((0, max_all))
plt.tight_layout()

# Animate
text = plt.text(0.05, 0.95, str(0), transform = fig.axes[0].transAxes, fontsize='xx-large')

def animate(i):
    y = data_per_step[i]
    text.set_text(str(i))
    for bi, bs in enumerate(bars):
        for i, b in enumerate(bs):
            b.set_height(y[bi][i])

anim=animation.FuncAnimation(fig,animate,repeat=True,blit=False,frames=n,
                             interval=INTERVAL)

#anim.save('test.mp4', writer=animation.FFMpegWriter(fps=1000/INTERVAL))
anim.save('test.gif', writer='imagemagick', fps=1000/INTERVAL)
plt.show()
