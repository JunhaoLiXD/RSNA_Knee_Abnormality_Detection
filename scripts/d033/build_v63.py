"""Build notebooks/v63-submit.ipynb = v61 (all 25 cells, byte-identical except header and configuration) + four appended cells: a
markdown cell, v62's R6 asset cell written to /tmp/v63_r6_setup.py (temp folder 'probe' -> 'probe_r6'), the R6 stage and the final
v61/v62-recipe rank blend.  Design: docs/research/v63-v61-v62-blend-design.md.

    python build_v63.py              # v63: anchor weight 0.5
    python build_v63.py v64 0.0      # v64: the v62 recipe alone (with R224 mirror) + the reader; same cells, header_v64.md
    python build_v63.py v65 0.0 r7   # v65: v64 with the compact slot = 0.65 rank(R6) + 0.35 rank(R7) (v61's [s6f] rule); header_v65.md
    python build_v63.py v66 0.0 s6f  # v66: v64 with the compact slot = 0.65 rank(R6) + 0.35 rank(S6F0); header_v66.md
"""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CELLS = Path(__file__).parent / "v63_cells"
VER = sys.argv[1] if len(sys.argv) > 1 else "v63"
W_ANCHOR = sys.argv[2] if len(sys.argv) > 2 else "0.5"
assert float(W_ANCHOR) in (0.0, 0.5), W_ANCHOR
M2 = sys.argv[3] if len(sys.argv) > 3 else None   # second model of the compact slot (stage_blend_m2.py); None = R6 alone (v63, v64)
assert M2 in (None, 'r7', 's6f'), M2
assert M2 is None or (VER not in ('v63', 'v64') and float(W_ANCHOR) == 0.0), (VER, W_ANCHOR, M2)
M2_NAME = {'r7': "R7 (v61's own compact model, ours_sub.csv)", 's6f': "S6F0 (v61's [s6f] model, ours_s6f_sub.csv)"}.get(M2)
sha = lambda b: hashlib.sha256(b).hexdigest()
src = lambda c: "".join(c["source"])


def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


v61 = json.loads((REPO / "notebooks/v61-submit.ipynb").read_text(encoding="utf-8"))
v62 = json.loads((REPO / "notebooks/v62-submit.ipynb").read_text(encoding="utf-8"))
bc = v61["cells"]
assert len(bc) == 25 and src(bc[0]).startswith("# v61 - ") and src(bc[1]).startswith("# v61 configuration")

# v62's R6 asset cell: identical to v61's R7 asset cell except bundle id, dataset slug and the flip switch
r6_cell = src(v62["cells"][7])
assert r6_cell.startswith("ARM = 'E_lrprior'\nBUNDLE_ID = 'fe055406fad6a12f'")
r7_cell = src(bc[6])
import difflib
diff = [l for l in difflib.unified_diff(r7_cell.splitlines(), r6_cell.splitlines(), lineterm="", n=0)
        if l[:1] in "+-" and not l.startswith(("+++", "---"))]
removed = sorted(l[1:].split(" ")[0] for l in diff if l[0] == "-")
added = sorted(l[1:].split(" ")[0] for l in diff if l[0] == "+")
assert removed == ["BUNDLE_ID", "C_SLUG", "if", "print('ASSETS_READY',"], removed
assert added == ["", "BUNDLE_ID", "C_SLUG", "FLIP_TTA", "if", "print('ASSETS_READY',"], added   # "" = one indented comment line
setup = replace_once(r6_cell, "TMP = TMP / 'probe'\n", "TMP = TMP / 'probe_r6'   # [v63] own temp folder: no file of the R7 stage is touched\n")
# Kaggle limits the kernel source to 1 MB: the 382 kB SOURCES line of the R6 cell is byte-identical to the R7 cell's (cell 6), so the
# R6 setup takes the dict the R7 cell defined (passed in as R7_SOURCES); the cell still checks every written file against SOURCE_SHA.
src_line = [l for l in r6_cell.splitlines() if l.startswith("SOURCES = ")]
assert len(src_line) == 1 and src_line == [l for l in r7_cell.splitlines() if l.startswith("SOURCES = ")]
setup = replace_once(setup, src_line[0] + "\n", "SOURCES = R7_SOURCES   # [v63] the identical dict of the R7 asset cell (size limit); each file is checked against SOURCE_SHA below\n")
setup = setup if setup.endswith("\n") else setup + "\n"
SETUP_SHA = sha(setup.rstrip("\n").encode("utf-8"))   # trailing newlines are not trusted to survive %%writefile

header = (CELLS / ("header.md" if VER == "v63" else f"header_{VER}.md")).read_text(encoding="utf-8").rstrip("\n")
header = replace_once(header, "__BASE_BODY__", src(bc[0]).split("\n", 1)[1].lstrip("\n"))
cfg = src(bc[1])
for old, new in (("# v61 configuration", f"# {VER} configuration"), ("VERSION = 'v61'", f"VERSION = '{VER}'"),
                 ("S6F0 in the ConvNeXt slot'", "S6F0 in the ConvNeXt slot; then R6 + the v62 recipe, rank-blended 0.5/0.5 with v61'" if VER == "v63" else
                  "S6F0 in the ConvNeXt slot (fallback only); then R6 + the v62 recipe alone, the reader at 0.10'" if M2 is None else
                  "S6F0 in the ConvNeXt slot (fallback only); then R6 + 0.35 %s in the compact slot + the v62 recipe alone, the reader at 0.10'" % M2_NAME.split(' ')[0])):
    cfg = replace_once(cfg, old, new)
stage = replace_once((CELLS / "stage_launch.py").read_text(encoding="utf-8"), "__R6_SETUP_SHA256__", SETUP_SHA)
blend = (CELLS / "stage_blend.py").read_text(encoding="utf-8")
blend = replace_once(blend, "V63_W_ANCHOR = 0.5\n", f"V63_W_ANCHOR = {W_ANCHOR}\n" if VER == "v63" else
                     f"V63_W_ANCHOR = {W_ANCHOR}   # [{VER}] the v62 recipe alone (mix = pct(v62 recipe)); the v61 anchor is read and validated but not mixed\n")
if M2 is not None:   # [v65, v66] the compact slot of v62_recipe becomes (1 - A2) rank(R6) + A2 rank(M2); every other line as v64
    m2_src = (CELLS / "stage_blend_m2.py").read_text(encoding="utf-8")
    m2_src = m2_src.replace("__VER__", VER).replace("__M2_NAME__", M2_NAME)
    m2_src = replace_once(m2_src, "V63_M2 = '__M2__'\n", f"V63_M2 = '{M2}'\n")
    assert "__" not in m2_src.replace("__name__", ""), "unfilled placeholder"
    blend = replace_once(blend, "def v63_blend(", m2_src + "def v63_blend(")
    blend = replace_once(blend, "def v62_recipe(raw, raw224, ours, our_fail, labels):\n",
                         f"def v62_recipe(raw, raw224, ours, our_fail, labels, slot=None):   # [{VER}] slot: precomputed compact-slot ranks (n x L)\n")
    blend = replace_once(blend, "        ro = _v63_pct_on(ours[c].values, ~our_fail)\n",
                         f"        ro = _v63_pct_on(ours[c].values, ~our_fail) if slot is None else slot[:, j]   # [{VER}] R6 + M2 ranks, not re-ranked\n")
    blend = replace_once(blend, "    v62r, rec['v62_recipe'] = v62_recipe(raw, raw224, r6, r6_fail, labels)\n",
                         f"    _m2_slot, rec['m2'] = v63_m2(work, test_ids, labels, r6, r6_fail, aligned, rd)   # [{VER}] None: the slot is R6 alone (v64)\n"
                         "    if _m2_slot is None:\n"
                         "        v62r, rec['v62_recipe'] = v62_recipe(raw, raw224, r6, r6_fail, labels)\n"
                         "    else:\n"
                         "        v62r, rec['v62_recipe'] = v62_recipe(raw, raw224, r6, r6_fail & _m2_slot[1], labels, slot=_m2_slot[0])\n")
for t in (stage, blend):
    compile(t, "<cell>", "exec")

mk = lambda ctype, text: ({"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)} if ctype == "markdown" else
                          {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text.splitlines(keepends=True)})
cells = [dict(bc[0], source=header.splitlines(keepends=True)), dict(bc[1], source=cfg.splitlines(keepends=True))] + bc[2:]
cells += [mk("markdown", (CELLS / "stage_md.md").read_text(encoding="utf-8").rstrip("\n")),
          mk("code", "%%writefile /tmp/v63_r6_setup.py\n" + setup),
          mk("code", stage.rstrip("\n")),
          mk("code", blend.rstrip("\n"))]
for i in range(2, 25):
    assert cells[i] == bc[i] and src(cells[i]) == src(bc[i]), i
# what %%writefile writes is the cell body after the magic line
assert src(cells[26]).split("\n", 1)[1] == setup
nb = {**v61, "cells": cells}
assert len(json.dumps(nb, indent=1, ensure_ascii=False).encode("utf-8")) < 950_000, "Kaggle kernel source limit is 1 MB"
out = REPO / f"notebooks/{VER}-submit.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"{VER} built (anchor weight {W_ANCHOR}, compact-slot M2 {M2}): {len(cells)} cells (v61 cells 2-24 identical); R6 setup sha256 {SETUP_SHA}")
print("R6 vs R7 asset-cell diff lines:", len(diff))
