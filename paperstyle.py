
import os
import matplotlib
import matplotlib.pyplot as plt

COLORS=["r", "k", "b", "g", "y", "purple", "cyan"]
MARKERS = ['.', '>', '<', '*', 'v', '^', 'D', 'X', 'P', 'p', 's']
LINE_STYLES=[":","-.","--","-"]

IS_PDF = True

SLIDES_FONT_SIZE = 18

def _figsize():
    if os.environ.get("SMALL_PLOT") is not None:
        return (3, 2.5)
    elif os.environ.get("SLIDE_PLOT") is not None:
        # Side-effect: increase font size, set title
        matplotlib.rcParams.update({'font.size': SLIDES_FONT_SIZE})
        plt.title(os.environ.get("SLIDE_PLOT"))

        return (8, 6)
    else:
        return (5, 3.5)

FIGSIZE=_figsize()
