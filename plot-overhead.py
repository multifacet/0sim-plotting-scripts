
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import itertools

from paperstyle import MARKERS, FIGSIZE, COLORS, IS_PDF

ncores = np.arange(1,6+1)

runtime_wk_old = [
        17638.78
  ,      7814.02
  ,      6336.68
  ,      5994.44
  ,      7106.50
  ,      5936.40
        ]
runtime_wk_old = [x / 3600 for x in runtime_wk_old]

runtime_server = [
12962.40
,11059.22
,11929.60
,11739.92
,12600.15
,11919.46
        ]
runtime_server = [x / 3600 for x in runtime_server]

overhead_wk_old = [
0.9356539089
,0.9248288497
,0.9484905401
,0.9480834729
,0.9677775965
,0.9604357145
]
overhead_wk_old = [1/(1 - x) for x in overhead_wk_old]

overhead_server = [
0.9134877229 ,
0.9346357321 ,
0.9544847567 ,
0.9626717876 ,
0.9680069934 ,
0.9789826599 ,
        ]
overhead_server = [1/(1-x) for x in overhead_server]

colors = itertools.cycle(COLORS)
wk_old_color = colors.next()
neutral_color = colors.next()
server_color = colors.next()

fig, ax1 = plt.subplots(figsize=FIGSIZE)

ax1.set_xlabel('Number of simulated cores')
plt.grid()

width = 0.35

ax1.set_ylabel('Simulation Duration (hours)')
ax1.bar(ncores - width/2, runtime_wk_old, width, alpha=0.5, color = wk_old_color)
ax1.bar(ncores + width/2, runtime_server, width, alpha=0.5, color = server_color)
ax1.tick_params(axis='y')
ax1.set_ylim((0, 5))

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

ax2.set_ylabel('Slowdown vs Native (x)')
ax2.plot(ncores, overhead_wk_old, color = wk_old_color, linestyle = '--')
ax2.plot(ncores, overhead_server, color = server_color, linestyle = '--')
ax2.tick_params(axis='y')
ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax1.get_yticks())))

custom_lgd = [
        Line2D([0], [0], color = wk_old_color, lw=4),
        Line2D([0], [0], color = server_color, lw=4),
        Patch(facecolor = neutral_color),
        Line2D([0], [0], color = neutral_color, linestyle = "--")
        ]
lgd_text = [
        "wk-old",
        "server",
        "Duration",
        "Slowdown"
        ]

ax1.legend(custom_lgd, lgd_text, loc = 'upper center', ncol = 2)

plt.savefig("/tmp/figure.%s" % ("pdf" if IS_PDF else "png"), bbox_inches="tight")

plt.show()
