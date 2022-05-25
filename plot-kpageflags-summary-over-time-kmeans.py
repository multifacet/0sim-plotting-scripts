#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.colors as mc
import matplotlib.patches as mpatches
import numpy as np
import networkx as nx

import re
import itertools
from collections import OrderedDict
from random import random, seed
import os
from datetime import datetime, timedelta
from sklearn.cluster import KMeans, OPTICS, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler, scale
from scipy import signal, stats

from sys import argv, exit

from paperstyle import MARKERS, COLORS, IS_PDF, OUTFNAME, NOSHOW, FIGSIZE, hash_to_color

################################################################################
# Read and clean up the data
################################################################################

# path to directory with class directories
INDIR=argv[1] + "/"

# machine: {dt: {label: kb}}
data = { }
ordered_labels = [ ]
ordered_dts = []
ordered_machines = [ ]

def parse_mem(memstr):
    units = memstr[-2:]
    val = memstr[:-2]

    return int(val) * (1 << 10 if units == "MB" else 1)

for mclass in filter(lambda e: e.is_dir(), os.scandir(INDIR)):
    for machine in filter(lambda e: e.is_dir(), os.scandir(mclass.path)):
        data[machine.name] = { }
        dtdir = os.listdir(machine.path)

        for dtname in dtdir:
            # round to nearest half hour
            dt = datetime.strptime(dtname, '%m-%d-%Y-%H-%M-%S.summary')
            dt = dt - (dt - datetime.min) % timedelta(minutes=30)

            data[machine.name][dt] = {}

            with open(machine.path + "/" + dtname, "r") as file:
                for line in file.readlines():
                    if "SUMMARY" in line or "TOTAL:" in line:
                        continue

                    parts = line.split()
                    dist = parts[0:4]
                    mem = parse_mem(parts[5])
                    label = " ".join(parts[6:]).strip()
                    label = label if len(label) > 0 else "None"

                    data[machine.name][dt][label] = float(mem) / (1 << 20)

                    ordered_labels.append(label)

            # Normalize
            total = sum(data[machine.name][dt].values())
            for label in data[machine.name][dt].keys():
                data[machine.name][dt][label] /= total

            ordered_dts.append(dt)
        ordered_machines.append(machine.name)

ordered_machines = sorted(list(set(ordered_machines)))
ordered_labels = sorted(list(set(ordered_labels)))
ordered_dts = sorted(list(set(ordered_dts)))

ordered_flat_dts_labels = list(itertools.product(ordered_dts, ordered_labels))

print(len(ordered_machines))
print(len(ordered_labels))
print(len(ordered_dts))
#print(ordered_flat_dts_labels)

# discard timesteps for which we don't have data from (almost) all machines
def dt_missing_in_machines(dt):
    missing = []
    for m in ordered_machines:
        if not dt in data[m]:
            missing.append(m)

    return missing

dts_to_remove = [dt for dt in ordered_dts if len(dt_missing_in_machines(dt)) >= 3]

ordered_dts = [dt for dt in ordered_dts if len(dt_missing_in_machines(dt)) < 3]
for m in ordered_machines:
    for dt in dts_to_remove:
        #print(dt, dt_missing_in_machines(dt))
        if dt in data[m]:
            del data[m][dt]

print(len(ordered_dts))

# Most of the timestamps are missing from 1 or 2 machines, e.g., due to the
# machine restarting during the snapshot. Dropping all of these timestamps
# would cause a lot of data discarding, so instead we fill it in from the
# nearest completed snapshot.
def previous_dt(dt, m):
    idx = ordered_dts.index(dt)
    for i in range(1, 10): # 10 should be more than enough...
        other_idx = idx - i
        if other_idx >= 0:
            other = ordered_dts[other_idx]
            if other in data[m]:
                return other

        other_idx = idx + i
        if other_idx < len(ordered_dts):
            other = ordered_dts[other_idx]
            if other in data[m]:
                return other

    print(dt, m)
    raise None

dts_to_fill_in = [dt for dt in ordered_dts if 0 < len(dt_missing_in_machines(dt)) < 3]
for dt in dts_to_fill_in:
    for m in dt_missing_in_machines(dt):
        pdt = previous_dt(dt, m)
        #print(dt, pdt)
        data[m][dt] = data[m][pdt]

################################################################################
# Preprocessing to capture or ignore various features
#
# There are several different ideas here...
################################################################################

# Raw Data
# 2D array
#   ys[machine][flattened dt + label]
#
# Pros: easy to understandd
# Cons: by making each timestep a different dimension, we are forcing the exact
# timing of peaks and troughs to be important. But instead we want the
# proportions of memory usage and the overall pattern.
#ys = []
#for machine in ordered_machines:
#    m = []
#    for dt, label in ordered_flat_dts_labels:
#        if machine in data and dt in data[machine] and label in data[machine][dt]:
#            val = data[machine][dt][label]
#        else:
#            val = 0
#        m.append(val)
#    ys.append(m)

# Mean, average difference from previous timestamp for each set of flags, max
# periodogram spike
#
# 2D array
#   ys[machine][label +0/1/2/3] = mean if 0, avgdiff if 1, max period if 2,3
#
# Goal: the mean captures proportions of different flags, while the average
# difference from the previous timestep captures the amount of change over
# time, including a notion of how much fluctuation there is (in a way that just
# variance would miss). The periodogram is meant as a measure of periodicity.
ys = []
maxmaxpower = 0
maxmaxperiod = 0
#ordered_labels = ["Buddy"]
for machine in ordered_machines:
    m = []

    for label in ordered_labels:
        ldata = []
        for dt in ordered_dts:
            if label in data[machine][dt]:
                ldata.append(data[machine][dt][label])
            else:
                ldata.append(0)

        mean = np.mean(ldata)
        var = np.var(ldata)
        avgdiff = np.mean(np.diff(ldata))
        avgdiffdiff = np.mean(np.diff(np.diff(ldata)))
        avgdiffdiffdiff = np.mean(np.diff(np.diff(np.diff(ldata))))
        avgdiffdiffdiffdiff = np.mean(np.diff(np.diff(np.diff(np.diff(ldata)))))
        vardiff = np.mean(np.diff(ldata))
        #print(ldata)
        #print(np.diff(ldata))
        #print(np.diff(np.diff(ldata)))
        #print(avgdiffdiff)
        f, Pxx = signal.periodogram(ldata, fs=336) # 2per hour * 24h * 7 days = 336 samples/week
        maxpower = max(Pxx)
        maxperiod = f[np.where(Pxx == maxpower)][0]

        #if machine == "catbert.cs.wisc.edu" or machine == "zazu.cs.wisc.edu":
        #    print(label)
        #    print(f)
        #    print(Pxx)
        #    print(maxpower)
        #    print(maxperiod)
        #    if label == "Lru":
        #        plt.figure(1, figsize=FIGSIZE)
        #        plt.semilogy(f, Pxx)
        #        plt.plot(ldata)
        #        plt.show()

        #print("ddddd")
        #print(f)
        #print(Pxx)
        #print(maxpower)
        #print(maxperiod)

        m.append(mean)
        #m.append(var)
        m.append(avgdiff)
        #m.append(avgdiffdiff)
        #m.append(avgdiffdiffdiff)
        #m.append(avgdiffdiffdiffdiff)
        #m.append(vardiff)
        m.append(maxpower)
        #m.append(maxperiod)
        maxmaxpower = max(maxmaxpower, maxpower)
        maxmaxperiod = max(maxmaxperiod, maxperiod)
        #m += f
        #m += list(Pxx[:10])
    ys.append(np.array(m))

# The mean, avgdiff, vardiff are all of similar scales and normalized already.
# They need to be normalized together because we want the features to remain
# correlated.
#
# But the maxpower and max period we want to normalize now. Again, we want to
# normalize them all together so they remain correlated.
for m in range(len(ordered_machines)):
    for l in range(len(ordered_labels)):
        ys[m][l * 3 + 2] /= maxmaxpower
        #ys[m][l * 4 + 3] /= maxmaxperiod

#ys = np.array(ys)
#ys = StandardScaler().fit_transform(ys)

#for f in range(len(ys[0])):
#    s, p = stats.shapiro(ys[:, f])
#    mean = np.mean(ys[:, f])
#    var = np.var(ys[:, f])
#    print(f, p, mean, var)

# transpose via python tricks
#ys = [*zip(*ys)]
#print(ys)
print(len(ys))
print(len(ys[0]))

# lump together categories that consistently have less than 0.5% impact
#to_remove = []
#for i, label in enumerate(ordered_labels):
#    freqenough = False
#    for j in range(len(ordered_fnames)):
#        if ys[i][j] >= max_y * 0.005:
#            freqenough = True
#    if not freqenough:
#        to_remove.append(label)
#
#other = [0 for f in ordered_fnames]
#for label_to_remove in to_remove:
#    i = ordered_labels.index(label_to_remove)
#    del ordered_labels[i]
#    for j in range(len(ys[i])):
#        other[j] += ys[i][j]
#    del ys[i]
#
#ordered_labels.append("Other")
#ys.append(other)

################################################################################
# Kmeans
################################################################################

seed(0)

#print("kmeans")

# kmeans
ks = [15]
#ks = range(1, 50+1)
#ks = range(1, len(ys)+1)

distortions = []
#for k in ks:
#    km = KMeans(n_clusters=k, init='random',
#                n_init=10, max_iter=300,
#                tol=1e-04, random_state=0)
#
#    categories = km.fit_predict(ys)
#    distortions.append(km.inertia_)
#
#    centers = km.cluster_centers_
#
#    print(k, km.inertia_)
#    for (i, m), c in zip(enumerate(ordered_machines), categories):
#        print("  ", m, c, np.linalg.norm(centers[c] - ys[i]))
#
#print("OPTICS")
#
#clustering = OPTICS(min_samples=3).fit(ys)
#for (i, m), c, r in zip(enumerate(ordered_machines), clustering.labels_, clustering.reachability_):
#    print("  ", m, c, r)

#print("Agglomerative")
#clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=20).fit(ys)
#for (i, m), c in zip(enumerate(ordered_machines), clustering.labels_):
#    print("  ", m, c)

print("Manual")
pairwise_dist = np.ndarray(shape=(len(ys), len(ys)))
for m1, m2 in itertools.product(range(len(ys)), range(len(ys))):
    pairwise_dist[m1, m2] = np.linalg.norm(ys[m1] - ys[m2])

    # for simplicity later...
    if m1 == m2:
        pairwise_dist[m1, m2] = float('inf')

# sort and replot ordered by which machine is closest to most others
#sumpairwise_dist = []
#for m in range(len(ys)):
#    sumpairwise_dist.append((m, sum(pairwise_dist[m, :])))
#sumpairwise_dist.sort(key=lambda x: x[1])
#
#pairwise_dist = np.ndarray(shape=(len(ys), len(ys)))
#for m1, m2 in itertools.product(range(len(ys)), range(len(ys))):
#    pairwise_dist[m1, m2] = np.linalg.norm(ys[sumpairwise_dist[m1][0]] - ys[sumpairwise_dist[m2][0]])

shortest_dists = [(m1, m2, pairwise_dist[m1, m2]) for m1, m2 in itertools.product(range(len(ys)), range(len(ys))) if m1 > m2]
shortest_dists.sort(key=lambda x: x[2])

#print(pairwise_dist)
for m1, m2, d in shortest_dists[:2]:
    print(ordered_machines[m1], ordered_machines[m2], d)
    print(ys[m1])
    print(ys[m2])
    print(ys[m1] - ys[m2])
    print(np.linalg.norm(ys[m1] - ys[m2]))
for m1, m2, d in shortest_dists[-2:]:
    print(ordered_machines[m1], ordered_machines[m2], d)
    print(ys[m1])
    print(ys[m2])

#im = plt.imshow(pairwise_dist)
#plt.colorbar(im)
#plt.xticks(range(len(ys)), ordered_machines, fontsize=5, rotation=90)
#plt.yticks(range(len(ys)), ordered_machines, fontsize=5)
#plt.show()
#plt.savefig("/tmp/diffs.pdf")

# plot a network where each machine is connected to its nearest neighbor
G = nx.DiGraph()
G.add_nodes_from([n.replace("wisc.edu", "") for n in ordered_machines])
for i, m in enumerate(ordered_machines):
    minn = min(pairwise_dist[i, :])
    mini = np.where(pairwise_dist[i, :] == minn)[0][0]

    s = m.replace("wisc.edu", "")
    t = ordered_machines[mini].replace("wisc.edu", "")

    G.add_edge(s, t, weight=pairwise_dist[i, mini])

cluster_centers = []
cluster_max_dist = []
cluster_v = []
for i, c in enumerate(nx.weakly_connected_components(G)):
    vecs = [ys[ordered_machines.index(m + "wisc.edu")] for m in c]
    center = np.average(vecs, axis=0)

    max_dist = max([np.linalg.norm(a - b) for a, b in itertools.product(vecs, vecs)])

    #for m in c:
    #    print(m + "wisc.edu", i, max_dist)
    
    cluster_centers.append(center)
    cluster_max_dist.append(max_dist)
    cluster_v.append(list(c)[0])

pairwise_centers_dists = []
for c1, c2 in itertools.product(range(len(cluster_centers)), range(len(cluster_centers))):
    if c1 != c2 and c1 > c2:
        pairwise_centers_dists.append((c1, c2, np.linalg.norm(cluster_centers[c1] - cluster_centers[c2])))
    else:
        pairwise_centers_dists.append((c1, c2, float('inf')))
pairwise_centers_dists.sort(key=lambda x: x[2])

print(pairwise_centers_dists[:10])

# connect components that are close together relative to the clusters
for c1, c2, dist in pairwise_centers_dists:
    if dist <= cluster_max_dist[c1] and dist <= cluster_max_dist[c2]:
        G.add_edge(cluster_v[c1], cluster_v[c2])

for i, c in enumerate(nx.weakly_connected_components(G)):
    vecs = [ys[ordered_machines.index(m + "wisc.edu")] for m in c]

    max_dist = max([np.linalg.norm(a - b) for a, b in itertools.product(vecs, vecs)])

    for m in c:
        print(m + "wisc.edu", i, max_dist)

L = nx.spring_layout(G, scale=2)
nx.draw_networkx(G, pos=L, with_labels=True, font_size=5, node_shape="s", node_size=600)
nx.draw_networkx_edge_labels(G, pos=L, font_size=5, rotate=False,)
#plt.show()

exit(0)

################################################################################
# Plot
################################################################################

plt.figure(1, figsize=FIGSIZE)

plt.plot(ks, distortions, marker='o', markersize=1)

plt.xlim(left=0)
plt.ylim(bottom=0)

plt.xlabel("k")
plt.ylabel("Error")

plt.grid(True)

#colors = [hash_to_color(hash(label)) for label in ordered_labels]

#print(ys)

#dts = [datetime.strptime(fname, '%m-%d-%Y-%H-%M-%S.summary') for fname in ordered_fnames]
#xs = [(dt - dts[0]).total_seconds() / (24. * 3600.) for dt in dts]
#
#print(len(xs))
#print(len(ys))
#print(len(ys[0]))
#print(ordered_labels)
#
#plt.stackplot(xs, ys, baseline="zero", labels=ordered_labels, colors=colors, edgecolor="black")
#
#plt.xlabel("Time (days)")
#plt.ylabel("Physical Memory (GB)")
#
#plt.xlim((0, max(xs)))
#plt.ylim((0, max_y))
#
#plt.xticks(rotation=90)
#
#plt.grid(True)
#
#plt.legend(loc="lower left", bbox_to_anchor=(0, 1.05), ncol=2)
#plt.tight_layout()

plt.savefig("%s.%s" % (OUTFNAME, ("pdf" if IS_PDF else "png")), bbox_inches="tight")

if not NOSHOW:
    plt.show()
