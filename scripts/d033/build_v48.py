"""Build notebooks/v48-submit.ipynb (D-033 probe A): v47 with R7's own flip-TTA switched on; every other cell unchanged."""
import json
from pathlib import Path

REPO = Path("E:/Project/RSNA_Knee_Abnormality_Detection")
v47 = json.loads((REPO / "notebooks/v47-submit.ipynb").read_text(encoding="utf-8"))
src = lambda c: "".join(c["source"])
cfg47 = src(v47["cells"][1])
assert cfg47.startswith("# v47 configuration") and cfg47.count("VERSION = 'v47'") == 1
assert src(v47["cells"][6]).startswith("ARM = 'E_lrprior'") and "WORKER_ARGS = [" in src(v47["cells"][6])
assert "probe_dual.py" in src(v47["cells"][7])

header = """# v48 - v47 with R7's own flip-TTA (D-033 probe A)

Explicit version of v47 (D-017: a changed public anchor setting is a new version). Decision D-033
(`docs/research/silver-push-2026-10-14.md`): R7's worker scores every window twice, plain and anatomically mirrored, and
averages the two passes in logit space per fold model. The mirror is the one R7 was trained with (`run_config` `"mirror": 0.5`,
`compact_train` v9.4): coronal and axial windows flipped on the patient's left-right axis, sagittal windows reversed along the
slice axis with `rel_pos` negated, the coronal bilateral views exchanged; the mirrored outputs are re-indexed (Medial <->
Lateral Meniscus, Medial <-> Lateral OA) and MCL comes from the plain pass. The fold models carry the extent heads the TTA
needs (`extent: true`). The bundle ships with `flip_tta: false`; nothing else changes (weights, stackers, blends, the reader).

## Provenance

- v47 (cells 2-19 unchanged): heliosli's public R7 one-click notebook (Apache 2.0) + goodpjw2008's public reader at 0.10.
- The flip-TTA code path is heliosli's own (`compact_infer.py` v4c `--flip-tta`, embedded in the R7 notebook's sources).

## Our changes

1. This cell and a v48 configuration cell (v47's settings, VERSION = 'v48').
2. One cell after the R7 setup cell appends `--flip-tta` to the R7 worker's arguments (with assertions).

Judged against v47 by rank crossing (>= 20 stable witnesses, none reversed). Requirements as v47.
"""

cfg = cfg47.replace("# v47 configuration", "# v48 configuration (v47's settings; probe A of D-033: R7 flip-TTA)", 1)
cfg = cfg.replace("VERSION = 'v47'", "VERSION = 'v48'", 1)

flip = """# v48 (D-033 probe A): R7's own flip-TTA. The fold models were trained with this anatomical mirror (run_config "mirror": 0.5)
# and carry the extent heads it needs; the worker re-indexes the mirrored outputs (medial <-> lateral meniscus and OA), averages
# the two passes in logit space and keeps MCL from the plain pass. Only the worker's arguments change.
assert manifest.get('flip_tta') is False and manifest['backbone'] != 'ofl_l', (manifest.get('flip_tta'), manifest['backbone'])
assert '--flip-tta' not in WORKER_ARGS, WORKER_ARGS
WORKER_ARGS += ['--flip-tta']
print('V48_FLIP_TTA', WORKER_ARGS[-1], flush=True)
"""


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.splitlines(keepends=True)}


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)}


cells = [md(header), code(cfg)] + [dict(c) for c in v47["cells"][2:7]] + [code(flip)] + [dict(c) for c in v47["cells"][7:]]
assert [src(c) for c in cells[2:7]] == [src(c) for c in v47["cells"][2:7]]
assert [src(c) for c in cells[8:]] == [src(c) for c in v47["cells"][7:]]
nb = {**v47, "cells": cells}
(REPO / "notebooks/v48-submit.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("v48 cells", len(cells))
