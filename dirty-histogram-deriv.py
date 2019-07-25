#!/usr/bin/env python2

import matplotlib.pyplot as plt
import numpy as np

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

parts = argv[1].split(":")

nbins = int(parts[0])
filename = parts[1]
data = []

with open(filename, 'r') as f:
    prev = None

    for line in f.readlines():
        try:
            val = float(line.strip().replace(',', ''))

            if prev is None:
                prev = val
                continue

            # dirty filter for outliers...
            #if (val - prev) >= 2.5E6:
            #    continue

            data.append(val - prev)
            prev = val

        except ValueError:
            print("skipping %s" % line)

#plt.hist(data, bins = nbins, range = [0, 500000])
plt.hist(data, bins = nbins)

plt.yscale("log")

plt.show()
