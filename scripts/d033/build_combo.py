"""Build a D-033 combination notebook from the probe notebooks: python build_combo.py <version> <components>
components: any of flip (v48's cell), r224 (v50's cells), mavit (v49's cells), e.g. `build_combo.py v51 flip,r224,mavit`.
Base cells are v47's (or v50's when r224 is included); every inherited cell is asserted byte-identical to its source."""
import json
import sys
from pathlib import Path

REPO = Path("E:/Project/RSNA_Knee_Abnormality_Detection")
VER, COMPS = sys.argv[1], sys.argv[2].split(",")
assert set(COMPS) <= {"flip", "r224", "mavit"} and len(COMPS) >= 2
load = lambda v: json.loads((REPO / f"notebooks/{v}-submit.ipynb").read_text(encoding="utf-8"))
src = lambda c: "".join(c["source"])
v47, v48, v49, v50 = load("v47"), load("v48"), load("v49"), load("v50")
base = v50 if "r224" in COMPS else v47
cells = [dict(c) for c in base["cells"]]

# configuration: the base's settings + MaViT's additions; VERSION renamed
cfg = src(base["cells"][1])
first = cfg.splitlines()[0]
cfg = cfg.replace(first, f"# {VER} configuration (D-033 combination: {', '.join(COMPS)})", 1)
old_ver = "v50" if "r224" in COMPS else "v47"
assert cfg.count(f"VERSION = '{old_ver}'") == 1
cfg = cfg.replace(f"VERSION = '{old_ver}'", f"VERSION = '{VER}'", 1)
if "mavit" in COMPS:
    c49 = src(v49["cells"][1])
    add = c49[c49.index("# v49 additions"):]
    # Codex review 2026-10-14 point 5: in a combination MaViT is used only with near-full coverage (the probe v49 kept 0.5)
    assert add.count("MAVIT_MAX_NAN_FRACTION = 0.5") == 1
    add = add.replace("MAVIT_MAX_NAN_FRACTION = 0.5     # MaViT is not used if more studies than this have no prediction",
                      "MAVIT_MAX_NAN_FRACTION = 0.1     # combination: MaViT is not used if more than 10% of the studies have no prediction")
    assert "MAVIT_MAX_NAN_FRACTION = 0.1" in add
    cfg = cfg.rstrip("\n") + "\n\n" + add
    if "import json\n" not in cfg:
        cfg = cfg.replace("import time as _v47_time\n", "import json\nimport time as _v47_time\n", 1)
cells[1] = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": cfg.splitlines(keepends=True)}

# flip: v48's cell right after the R7 setup cell
if "flip" in COMPS:
    flip_cell = next(c for c in v48["cells"] if src(c).startswith("# v48 (D-033 probe A)"))
    k = next(i for i, c in enumerate(cells) if src(c).startswith("ARM = 'E_lrprior'"))
    assert "probe_dual.py" in src(cells[k + 1])
    cells.insert(k + 1, dict(flip_cell))

# mavit: v49's markdown + three code cells after the last cell
if "mavit" in COMPS:
    tail = v49["cells"][-4:]
    assert src(tail[0]).startswith("## v49") and src(tail[1]).startswith("# v49 source") and src(tail[3]).startswith("# v49 blend")
    cells += [dict(c) for c in tail]

names = {"flip": "R7 flip-TTA (v48)", "r224": "nartaa's 224-px CoAtNet at 0.35 of the Raptor slot (v50)",
         "mavit": "hengck23's MaViT-288 at outer rank weight 0.10 (v49)"}
header = f"""# {VER} - D-033 combination: v47 + {' + '.join(names[c] for c in COMPS)}

Explicit ensemble version (D-017), decision D-033 (`docs/research/silver-push-2026-10-14.md`). Each component is exactly the
cell(s) of its probe notebook, unchanged, with that probe's own fallbacks (any failure leaves the stage before it in place):
""" + "\n".join(f"- {names[c]}" for c in COMPS) + """

The base and every inherited cell are asserted byte-identical to their source notebooks in the builder. Judged against the
incumbent by rank crossing (>= 20 stable witnesses, none reversed). Provenance and licences: see v47, v48, v49 and v50.
"""
cells[0] = {"cell_type": "markdown", "metadata": {}, "source": header.strip("\n").splitlines(keepends=True)}
nb = {**base, "cells": cells}
out = REPO / f"notebooks/{VER}-submit.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(VER, "cells", len(cells), "components", COMPS)
