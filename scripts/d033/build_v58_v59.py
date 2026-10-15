"""Build v58 (v57 + the goodpjw2008 reader at outer weight 0.10, v47's reader cells unchanged) and v59 (v57 + R7 flip-TTA via
the 0.9573 notebook's own FLIP_TTA switch). Every other cell byte-identical to v57."""
import json
from pathlib import Path

REPO = Path("E:/Project/RSNA_Knee_Abnormality_Detection")
load = lambda v: json.loads((REPO / f"notebooks/{v}-submit.ipynb").read_text(encoding="utf-8"))
src = lambda c: "".join(c["source"])
code = lambda s: {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.splitlines(keepends=True)}
md = lambda s: {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)}
v57, v47 = load("v57"), load("v47")
assert src(v57["cells"][0]).startswith("# v57") and "FLIP_TTA = False" in src(v57["cells"][7])
assert src(v57["cells"][-1]).startswith("# Stage 3"), src(v57["cells"][-1])[:60]


def save(ver, cells):
    nb = {**v57, "cells": cells}
    (REPO / f"notebooks/{ver}-submit.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(ver, "cells", len(cells))


# ---- v59: R7 flip-TTA through the author's own switch
cells = [dict(c) for c in v57["cells"]]
s7 = src(cells[7])
old = "FLIP_TTA = False   # [d957] package F: no flip TTA"
assert s7.count(old) == 1 and "if manifest.get('flip_tta') or FLIP_TTA:" in s7
cells[7] = {**cells[7], "source": s7.replace(old, "FLIP_TTA = True   # [v59] R7's own flip-TTA on (the author's switch; v48 tested it on v47: +6 witnesses)").splitlines(keepends=True)}
h = src(cells[0]).replace("# v57 - v56 (public 0.9573 notebook) + mirror TTA on the CoAtNet-224 stage:",
                          "# v59 - v57 + R7 flip-TTA (D-033 probe on the 0.957 base): v56 + mirror TTA on the CoAtNet-224 stage + R7 flip-TTA;", 1)
assert h.startswith("# v59")
h += """
## v59 change (against v57)

The setup cell's own switch `FLIP_TTA = True`: R7 also scores the anatomically mirrored windows (the mirror R7 was trained
with, `mirror` 0.5), outputs re-indexed medial <-> lateral, MCL from the plain pass. Everything else equals v57.
"""
cells[0] = {**cells[0], "source": h.splitlines(keepends=True)}
for i, (a, b) in enumerate(zip(cells, v57["cells"])):
    if i not in (0, 7):
        assert src(a) == src(b)
save("v59", cells)

# ---- v58: the reader as an outer component (v47's cells 10-18 unchanged) + a configuration cell at the notebook start
cfg47 = src(v47["cells"][1])
cfg = """# v58 configuration: the settings v47's reader cells read (the reader's deadline counts from the notebook start)
import time as _v47_time

VERSION = 'v58'
V47_T0 = _v47_time.time()
""" + cfg47[cfg47.index("BLEND_W = 0.1"):cfg47.index("AUTHOR_V3_SHA")].rstrip("\n") + """
print(f'{VERSION}: v57 + goodpjw2008 reader at outer w {BLEND_W}, reader deadline {READER_DEADLINE_S / 3600:.1f} h', flush=True)
"""
for k in ("BLEND_W", "READER_CKPTS", "READER_DEADLINE_S", "READER_MIN_S", "MAX_EMPTY_FRACTION"):
    assert k in cfg, k
reader = [dict(c) for c in v47["cells"][10:19]]
assert src(reader[0]).startswith("## The public goodpjw2008 reader") and src(reader[-1]).startswith("# Blend with fallbacks")
assert not any("VERSION" in src(c) or "AUTHOR_V3_SHA" in src(c) for c in reader)
cells = [dict(c) for c in v57["cells"]]
h = src(cells[0]).replace("# v57 - v56 (public 0.9573 notebook) + mirror TTA on the CoAtNet-224 stage:",
                          "# v58 - v57 + the goodpjw2008 reader at outer weight 0.10 (D-033 probe on the 0.957 base): v56 + mirror TTA on R224 + reader;", 1)
assert h.startswith("# v58")
h += """
## v58 change (against v57)

A configuration cell at the notebook start and, after the stage-3 blend, v47's reader cells unchanged (base saved, the public
goodpjw2008 2.5D ConvNeXt reader's source written, run in its own process group under a deadline, then
`final = rank(0.9 rank(base) + 0.1 rank(reader))`; any reader failure keeps the base). v47 gained 191 witnesses from it on R7
alone (L37); v53 (with flip-TTA) displayed below the 0.957 recipe, so its effect on this base is the question.
"""
cells[0] = {**cells[0], "source": h.splitlines(keepends=True)}
cells = cells[:1] + [code(cfg)] + cells[1:] + reader
save("v58", cells)
