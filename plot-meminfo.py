#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

from sys import argv, exit

"""
Usage: ./plot Field label:file ...
"""

field = argv[1]

# {label: [values]}
data = {}

for a in argv[2:]:
    label, fname = a.split(':')

    fdata = []

    with open(fname, 'r') as f:
        for line in f.readlines():
            parts = line.strip().split()

            if parts[0] == field:
                val = int(parts[1])
                fdata.append(val)
            else:
                print("doesn't match: %s" % parts)

    data[label] = fdata

for label in data:
    plt.plot(data[label], label=label, marker='o')

plt.grid(True)

plt.legend()

plt.show()

