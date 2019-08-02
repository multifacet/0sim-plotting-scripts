#!/usr/bin/env python2

import matplotlib.pyplot as plt
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import FixedFormatter, FixedLocator

import numpy as np
from numpy import ma

import re
import itertools
from collections import OrderedDict

from sys import argv, exit

from paperstyle import MARKERS, COLORS, IS_PDF

data = OrderedDict()
data1 = OrderedDict()

for arg in argv[1:]:
    label = arg
    filename = arg
    snd_filename = None
    if ":" in arg:
        spl = arg.split(":")
        if len(spl) == 2:
            label, filename = spl
        else:
            label, filename, snd_filename = spl
    data[label] = []
    data1[label] = []

    with open(filename, 'r') as f:
        for line in f.readlines():
            try:
                val = float(line.strip().replace(',', ''))
                data[label].append(val)
            except ValueError:
                print("bad float: %s" % line)

    if snd_filename is not None:
        with open(snd_filename, 'r') as f:
            for line in f.readlines():
                try:
                    val = float(line.strip().replace(',', ''))
                    data1[label].append(val)
                except ValueError:
                    print("bad float: %s" % line)

# Source: https://stackoverflow.com/questions/31147893/logarithmic-plot-of-a-cumulative-distribution-function-in-matplotlib
class CloseToOne(mscale.ScaleBase):
    name = 'close_to_one'

    def __init__(self, axis, **kwargs):
        mscale.ScaleBase.__init__(self)
        self.nines = kwargs.get('nines', 5)

    def get_transform(self):
        return self.Transform(self.nines)

    def set_default_locators_and_formatters(self, axis):
        axis.set_major_locator(FixedLocator(
                np.array([(1-10**(-k)) * 100.0 for k in range(1+self.nines)])))
        axis.set_major_formatter(FixedFormatter(
                [str((1-10**(-k))*100.0) for k in range(1+self.nines)]))


    def limit_range_for_scale(self, vmin, vmax, minpos):
        return vmin, min((1 - 10**(-self.nines))*100.0, vmax)

    class Transform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            masked = ma.masked_where(a > (1-10**(-1-self.nines))*100.0, a)
            if masked.mask.any():
                return -ma.log10(100.0-a)
            else:
                return -np.log10(100.0-a)

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
            return (1. - 10**(-a)) * 100.0

        def inverted(self):
            return CloseToOne.Transform(self.nines)

mscale.register_scale(CloseToOne)

plt.figure(1, figsize=(5, 3.5))

markers = itertools.cycle(MARKERS)
colors = itertools.cycle(COLORS)

handles = []

for i, (label, xs) in enumerate(data.items()):
    xs = np.diff(xs)
    before = len(xs)
    xs = filter(lambda x: x > 0, xs) # TODO
    after = len(xs)
    print(label, before - after)
    cdfx = np.sort(xs)
    cdfy = np.linspace(0.0, 100.0, len(xs))

    h_plot, = plt.plot(cdfx, cdfy, label = "%s-local" % label, linestyle = '-', marker = 'None', color = colors.next())

    handles.append(h_plot)

markers = itertools.cycle(MARKERS)
colors = itertools.cycle(COLORS)

for i, (label, xs) in enumerate(data1.items()):
    xs = np.diff(xs)
    before = len(xs)
    xs = filter(lambda x: x > 0, xs) # TODO
    after = len(xs)
    print(label, before - after)
    cdfx = np.sort(xs)
    cdfy = np.linspace(0.0, 100.0, len(xs))

    if len(xs) > 0:
        h_plot, = plt.plot(cdfx, cdfy, label = "%s-nonlocal" % label, linestyle = '--', marker = 'None', color = colors.next())
        handles.append(h_plot)

plt.ylim((0, 99.999))

plt.xscale('log')
plt.yscale('close_to_one')

plt.ylabel("% of Measurements")
plt.xlabel("$\Delta$ Time (cycles)")

plt.legend(handles=handles, loc='lower right')

plt.grid(True)

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
