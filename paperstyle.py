
import os

COLORS=["r", "k", "b", "g"]
MARKERS = ['.', '>', '<', '*', 'v', '^', 'D', 'X', 'P', 'p', 's']
LINE_STYLES=[":","-.","--","-"]

IS_PDF = True

FIGSIZE=(3, 2.5) if os.environ.get("SMALL_PLOT") is not None else (5, 3.5)
