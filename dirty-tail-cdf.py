#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from numpy import ma
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import FixedFormatter, FixedLocator

import re
import itertools
from collections import OrderedDict
from cycler import cycler

from sys import argv, exit
from os import environ

from paperstyle import FIGSIZE, IS_PDF, OUTFNAME

USAGE_STR = "[FREQ=freq_mhz] ./script <nines> <label> <P0> <P1> ... <P100> <label> <P0> <P1> ... <P100> ..."
if len(argv[2:]) % 102 != 0:
    print("./Usage: %s" %  USAGE_STR)

FREQ = float(environ["FREQ"]) if "FREQ" in environ else None
NINES = float(argv[1])
NPLOTS = int(len(argv[2:]) / 102)

plt.figure(figsize=FIGSIZE)

#CYCLER = (cycler(color=['r', 'g', 'b', 'y', 'c', 'm', 'k']) + cycler(linestyle=['-', '--', ':', '-.']))
colormap = plt.cm.nipy_spectral
colors = [colormap(i) for i in np.linspace(0, 1, NPLOTS)]
styles = itertools.cycle(['-', '--', ':', '-.'])
plt.gca().set_prop_cycle('color', colors)

class CloseToOne(mscale.ScaleBase):
    name = 'close_to_one'

    def __init__(self, axis, **kwargs):
        mscale.ScaleBase.__init__(self)
        self.nines = int(NINES)

    def get_transform(self):
        return self.Transform(self.nines)

    def set_default_locators_and_formatters(self, axis):
        axis.set_major_locator(FixedLocator(
                np.array([100-10**(2-k) for k in range(1+self.nines)])))
        axis.set_major_formatter(FixedFormatter(
                [str(100-10**(2-k)) for k in range(1+self.nines)]))


    def limit_range_for_scale(self, vmin, vmax, minpos):
        return vmin, min(100 - 10**(2-self.nines), vmax)

    class Transform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            masked = ma.masked_where(a > 100-10**(2-1-self.nines), a)
            if masked.mask.any():
                return -ma.log10(1-a/100.) * 100.
            else:
                return -np.log10(1-a/100.) * 100.

        def inverted(self):
            return CloseToOne.InvertedTransform(self.nines)

    class InvertedTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            return 100. - 10**(2-a/100.)

        def inverted(self):
            return CloseToOne.Transform(self.nines)

mscale.register_scale(CloseToOne)


ys = [y for y in range(0, 101)] # 0 ..= 100
ys = [y * NINES / 100. for y in ys] # 0 ..= nines
ys = [100. - 10. ** (2 - y) for y in ys] # log space

s = ""

for i in range(NPLOTS):
    label = argv[2+i*102]
    #label = label.split("(")[0]
    xs = [float(x) for x in argv[2+i*102+1:2+(i+1)*102]]
    if FREQ is not None:
        xs = [x / FREQ for x in xs]
    ls = next(styles)
    if label in []:
        plt.plot(xs, ys, label=label, linewidth=0)
    else:
        plt.plot(xs, ys, label=label, linestyle=ls)

    s+=label

print(s)

plt.xscale("symlog")
plt.xticks(rotation=90)
plt.xlabel("Latency (%s)" % ("cycles" if FREQ is None else "usec"))
plt.xlim((1,1e7))

plt.ylabel("Percentile")
plt.yscale("close_to_one")

plt.grid(True)

if environ.get("NOLEGEND") is None:
    plt.legend(bbox_to_anchor=(0, 1.05), loc='lower left')
#plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
#plt.legend(loc='lower right')

plt.tight_layout()

plt.savefig("/tmp/%s.%s" % (OUTFNAME, ("pdf" if IS_PDF else "png")), bbox_inches="tight")
plt.show()
