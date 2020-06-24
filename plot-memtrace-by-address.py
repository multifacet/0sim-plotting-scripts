#!/usr/bin/env python3

from os import environ

if "NOX" in environ:
    import matplotlib
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import sys

from math import log

filename = sys.argv[1]

# [[(addr, count, age)]]
data = []
per_addr = {}

with open(filename, "r") as f:
    tmp = []
    for line in f.readlines():
        if line.strip() == "===":
            data.append(tmp)
            tmp = []
        else:
            split = line.split()
            addr  = int(split[0], 16)
            tmp.append((addr, int(split[1]), int(split[2])))

            if split[0] not in per_addr:
                per_addr[addr] = [(0, None)]

# Collect info over time per-address
for dump in data:
    visited = set()
    for (addr, count, age) in dump:
        per_addr[addr].append((count, age))
        visited.add(addr)

    # fill in blanks for the others
    for not_visited in set(per_addr.keys()) - visited:
        per_addr[not_visited].append((0, None))

fig = plt.figure()

big_array = []

for addr in sorted(per_addr.keys(), reverse=True):
    data = per_addr[addr]
    counts = [log(d[0]) if d[0] > 1 else d[0] for d in data]
    #counts = [d[0] for d in data]
    counts = np.diff(counts)
    big_array.append(counts)
    #plt.plot(counts, label=addr)

print("processed")

#LABEL_FREQ=1000
#labels = list(map(lambda x: hex(x), sorted(per_addr.keys(), reverse=True)))[::LABEL_FREQ]

im = plt.imshow(big_array, cmap = "Greys", aspect='auto')
cbar = plt.colorbar(im)
cbar.set_label("Log Number of accesses")

plt.ylabel('Huge page Address (sorted)')
plt.xlabel('Time (# memory accesses, chunks of 1-billion accesses)')
plt.gca().set_yticklabels(plt.gca().get_yticks(), {'family':'monospace'})
#plt.yticks(np.arange(0, len(labels)*LABEL_FREQ, LABEL_FREQ), labels)
plt.yticks([])

ax = fig.axes[0]
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)

plt.tight_layout()

if "NOX" not in environ:
    plt.show()

plt.savefig('{}.png'.format(filename))
