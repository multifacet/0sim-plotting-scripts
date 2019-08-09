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

from paperstyle import MARKERS, COLORS, IS_PDF, FIGSIZE

freq = OrderedDict()
data = OrderedDict()
data1 = OrderedDict()
has_data1 = False

YSCALE = argv[1]

for arg in argv[2:]:
    label, filename, snd_filename, freq_khz = arg.split(":")

    if snd_filename == '':
        snd_filename = None

    data[label] = []
    data1[label] = []
    freq[label] = freq_khz

    with open(filename, 'r') as f:
        for line in f.readlines():
            try:
                val = float(line.strip().replace(',', ''))
                data[label].append(val)
            except ValueError:
                print("bad float: %s" % line)

    if snd_filename is not None:
        has_data1 = True
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

# Choose units (milliseconds or microseconds) heuristically

def get_minish():
    dat = next(iter(data))
    dat = sorted(np.diff(data[dat]))
    if len(dat) < 100:
        return min(dat)
    else:
        l = len(dat) / 10
        return dat[l]

def get_maxish():
    dat = next(iter(data))
    dat = sorted(np.diff(data[dat]))
    if len(dat) < 100:
        return max(dat)
    else:
        l = len(dat) / 10
        return dat[-l]

millis = get_maxish() / 1E3 > 9999
units = "msec" if millis else "usec"
units_f = (lambda x, khz: x / float(khz)) if millis else (lambda x, khz: x * 1000.0 / float(khz))

plt.figure(1, figsize=FIGSIZE)

markers = itertools.cycle(MARKERS)
colors = itertools.cycle(COLORS)

handles = []

for i, (label, xs) in enumerate(data.items()):
    xs = np.diff(xs)
    before = len(xs)
    xs = filter(lambda x: x > 0, xs)
    after = len(xs)
    print(label, before - after)
    xs = map(lambda x: units_f(x, freq[label]), xs)
    cdfx = np.sort(xs)
    cdfy = np.linspace(0.0, 100.0, len(xs))

    legend_label = "%s-local" % label if has_data1 else label

    mark_freq = [len(xs) / 10,
            (-len(xs) / 20000) if YSCALE == 'close_to_one' else (-len(xs) / 10)]

    h_plot, = plt.plot(cdfx, cdfy, label = legend_label, linestyle = '-', marker = markers.next(), markevery=mark_freq, color = colors.next())

    handles.append(h_plot)

markers = itertools.cycle(MARKERS)
colors = itertools.cycle(COLORS)

for i, (label, xs) in enumerate(data1.items()):
    xs = np.diff(xs)
    before = len(xs)
    xs = filter(lambda x: x > 0, xs)
    after = len(xs)
    print(label, before - after)
    xs = map(lambda x: units_f(x, freq[label]), xs)
    cdfx = np.sort(xs)
    cdfy = np.linspace(0.0, 100.0, len(xs))

    legend_label = "%s-nonlocal" % label if has_data1 else label

    mark_freq = [len(xs) / 10,
            (-len(xs) / 50000) if YSCALE == 'close_to_one' else (-len(xs) / 10)]

    if len(xs) > 0:
        h_plot, = plt.plot(cdfx, cdfy, label = legend_label, linestyle = '--', marker = markers.next(), markevery=mark_freq, color = colors.next())
        handles.append(h_plot)

plt.ylim((0, 99.999) if YSCALE == "close_to_one" else (0, 100))

plt.xscale('log')
plt.yscale(YSCALE)

plt.ylabel("% of Measurements")
plt.xlabel("$\Delta$ Time (%s)" % units)

plt.legend(handles=handles, loc='lower right')

plt.grid(True)

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")
plt.show()
