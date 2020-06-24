#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

data = []

with open("/home/mark/nobackup/memtrace/exp_11__ycsb__-workload_A_-system_Memcached_-vm_size200-cores4-2020-04-06-09-33-32.trace.5927.3.ranked-pages", 'r') as f:
    for line in f.readlines():
        parts = line.split()
        if len(parts) < 3:
            print("Skipping line %s" % line)
            continue
        freq = int(parts[1])
        data.append(freq)

NXTICKS = 10
NYTICKS = 10

ys = np.cumsum(data)

plt.plot(ys)

xt = np.arange(0, len(data) * (1 + 1. / NXTICKS), len(data) / NXTICKS)
xl = [ int(i * (100 / NXTICKS)) for i in range(NXTICKS + 1)]
plt.xticks(ticks = xt, labels = xl)
plt.xlim((0, len(data)))

maxy = max(ys)
yt = np.arange(0, maxy * (1 + 1. / NYTICKS), maxy / NYTICKS)
yl = [ int(i * (100 / NYTICKS)) for i in range(NYTICKS + 1)]
plt.yticks(ticks = yt, labels = yl)
plt.ylim((0, maxy))

plt.ylabel("% of memory accesses covered")
plt.xlabel("% of memory TLB covers (ranked)")

plt.grid(True)

plt.show()
