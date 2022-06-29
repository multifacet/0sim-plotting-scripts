#!/usr/bin/env python3

import sys
import subprocess
import re
import numpy as np
from os import path, environ

COUNT = len(sys.argv[1:]) // 7

CACHE = {}

# start background process to compute read-pftrace results and cache them for later...
def prefetch(pftrace_file):
    if pftrace_file in CACHE:
        return

    # Run pftrace to get both the number of faults and the distribution.
    sp = subprocess.Popen([
        "/nobackup/cbmm/mm/read-pftrace/target/release/read-pftrace",
        "--tail", "10", "--combined", "--cli-only", "--exclude",
        "NOT_ANON", "--exclude", "SWAP", "--",
        pftrace_file + "pftrace", pftrace_file + "rejected", "10000"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    CACHE[pftrace_file] = sp

# read the prefetched results or error out, possibly blocking until done.
def pftrace(pftrace_file):
    if pftrace_file not in CACHE:
        prefetch(pftrace_file)

    sp = CACHE[pftrace_file]

    # possibly blocks...
    out, errs = sp.communicate()

    if sp.returncode != 0:
        print(pftrace_file, errs)
        sys.exit(1)

    return out.decode("ascii")

def dump(name, pftrace_file, runtimes_files):
    runtimes = []

    # Get the median runtime.
    for f in runtimes_files:
        full_path = f + "runtime"
        ycsb = False
        if not path.exists(full_path):
            full_path = f + "ycsb"
            ycsb = True

        with open(full_path, "r") as file:
            if ycsb:
                data_raw = file.read()
                ymatches = re.search(r'\[OVERALL\], RunTime\(ms\), (\d+)', data_raw)
                if ymatches is None:
                    print(data_raw, ymatches)
                rt = int(ymatches.group(1))
                runtimes.append(rt)
            else:
                data = int(file.read())
                runtimes.append(data)

    # Run pftrace to get both the number of faults and the distribution.
    output = pftrace(pftrace_file)

    matches = re.match(r'\s*none\((\d+)\)', output)
    pfcount = float(matches.group(1))
    pfrate = pfcount / np.median(runtimes)

    #print(pfcount)
    #print(pfrate)

    output = name + " " + " ".join(output.split()[1:])

    #print(pfrate)
    #print(output)

    return (pfrate, output)

# Cache for read-pftrace results...
for i in range(COUNT):
    prefetch(sys.argv[1 + i*7 + 1])

scales = []
data = []

for i in range(COUNT):
    name = sys.argv[1 + i*7]
    pftrace_file = sys.argv[1 + i*7 + 1]
    runtimes_files = sys.argv[1 + i*7 + 2:1 + i*7 + 2 + 5]

    pfrate, output = dump(name, pftrace_file, runtimes_files)
    scales.append(str(pfrate))
    data += list(output.split())

# Plotting

print(scales)

#OUTFNAME=tails-$WK PDF=1 SMALL_PLOT=1 NOLEGEND=1 FREQ=2600 SCALE="$UF_LINUX_SCALE $UF_CBMM_SCALE $UF_HAWKEYE_SCALE $FR_LINUX_SCALE $FR_CBMM_SCALE $FR_HAWKEYE_SCALE" /p/multifacet/users/markm/plotting/dirty-tail-cdf2.py 10 $(cat $OUT)

env = {}
env.update(environ)
env["FREQ"] = "2600"
env["SCALE"] = " ".join(scales)
env["DISPLAY"] = ":1"

subprocess.run(["/p/multifacet/users/markm/plotting/dirty-tail-cdf2.py", "10"] + data, env=env)
