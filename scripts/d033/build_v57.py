"""Build notebooks/v54-submit.ipynb = v53 + nartaa's anatomical mirror TTA on the R224 stage (varshithakolupuri "One Free Flip"
[s9] hunks, verbatim); every other cell byte-identical to v53."""
import difflib
import glob
import json
from pathlib import Path

REPO = Path("E:/Project/RSNA_Knee_Abnormality_Detection")
v56 = json.loads((REPO / "notebooks/v56-submit.ipynb").read_text(encoding="utf-8"))
src = lambda c: "".join(c["source"])
K = REPO / "external/kernels"
flip_nb = glob.glob(str(K / "varshithakolupuri__rsna-0-956-one-free-flip-68-ranks-up_20261014/*.ipynb"))[0]
old_nb = glob.glob(str(K / "varshithakolupuri__rsna-knee-one-unused-checkpoint-lifts-the-0-956_20261013/*.ipynb"))[0]
r224_cell = lambda nb: next(src(c) for c in json.load(open(nb, encoding="utf-8"))["cells"] if src(c).startswith("%%writefile /tmp/raptor224_run.py"))
vs_old, vs_new = r224_cell(old_nb), r224_cell(flip_nb)

k = next(i for i, c in enumerate(v56["cells"]) if src(c).startswith("%%writefile /tmp/raptor224_run.py"))
ours = src(v56["cells"][k])


def rep(t, old, new):
    assert t.count(old) == 1 and vs_old.count(old) == 1 and vs_new.count(new) == 1, (old[:70], t.count(old))
    return t.replace(old, new)


# hunk 1: the mirror helpers before the window LUT
H1_OLD = "_WLUT = {}\ndef gpu_windows(vol, mask, k, res, dev, norm=NORM):\n"
i0 = vs_new.index("# [s9] anatomical L/R mirror TTA")
i1 = vs_new.index("_WLUT = {}\ndef gpu_windows(vol, mask, k, res, dev, norm=NORM, mirror=False):\n")
H1_NEW = vs_new[i0:i1] + "_WLUT = {}\ndef gpu_windows(vol, mask, k, res, dev, norm=NORM, mirror=False):\n"
ours = rep(ours, H1_OLD, H1_NEW)
# hunk 2: the mirror inside gpu_windows
H2_OLD = "    tri = torch.from_numpy(np.ascontiguousarray(vol[np.stack([cs - 1, cs, cs + 1], 1)])).to(dev)   # (k,3,IMG,IMG) uint8\n"
H2_NEW = H2_OLD + "    if mirror:   # [s9]\n        tri = _mirror_tri(tri, cs, D)\n"
ours = rep(ours, H2_OLD, H2_NEW)
# hunk 3: average the plain and the mirrored pass
H3_OLD = "                    else:\n                        arm_probs[a][i] = infer_probs(model, xw, d)\n"
j0 = vs_new.index("                    else:   # [s9]")
j1 = vs_new.index("                        del xm\n", j0) + len("                        del xm\n")
H3_NEW = vs_new[j0:j1]
ours = rep(ours, H3_OLD, H3_NEW)
# the result must differ from varshitha's flip cell only by our own earlier additions (sha pin, raw dump, empty-mask skip)
d_ours = [l for l in difflib.unified_diff(src(v56["cells"][k]).splitlines(), ours.splitlines(), lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
d_vs = [l for l in difflib.unified_diff(vs_old.splitlines(), vs_new.splitlines(), lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
assert d_ours == d_vs, "our mirror hunks differ from varshitha's"

cells = [dict(c) for c in v56["cells"]]
cells[k] = {**cells[k], "source": ours.splitlines(keepends=True)}
header = src(cells[0]).replace("# v56 - Public 0.9573 notebook reproduced:", "# v57 - v56 (public 0.9573 notebook) + mirror TTA on the CoAtNet-224 stage:", 1)
assert header.startswith("# v57")
header += """

## v57 change (against v56, D-033)

The CoAtNet-224 stage averages the plain and the anatomically mirrored windows (probabilities, 0.5 each), as the CoAtNet-384
stage does: the three `[s9]` hunks of varshithakolupuri's public notebook "RSNA 0.956: One Free Flip, 68 Ranks Up"
(https://www.kaggle.com/code/varshithakolupuri/rsna-0-956-one-free-flip-68-ranks-up, Apache 2.0), copied verbatim (asserted
equal to that notebook's diff in the builder); the mirror code is nartaa's (0949 Anatomical Mirror). Everything else equals v56.
"""
cells[0] = {**cells[0], "source": header.splitlines(keepends=True)}
for i, (a, b) in enumerate(zip(cells, v56["cells"])):
    if i not in (0, k):
        assert src(a) == src(b)
nb = {**v56, "cells": cells}
(REPO / "notebooks/v57-submit.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("v57 built; R224 cell", k, "| diff lines", len(d_ours))
