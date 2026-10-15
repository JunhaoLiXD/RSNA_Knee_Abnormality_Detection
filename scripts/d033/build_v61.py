"""Build notebooks/v61-submit.ipynb = v54 + nartaa's public all-data S6 model ("S6F0", nartaa/rsna-knee-s6fall-weights, E_prior_s42_fall.pt) as a
second model in the ConvNeXt ("ours", R7) side of the stage-3 blend at A_S6F = 0.35.  Every v54 cell is byte-identical except the header (cell 0),
the configuration (cell 1) and the stage-3 blend (three hunks); two cells (markdown + code) are inserted after the R224 stage (base cell 11).

    python build_v61.py

Sources of the new cells (read from ./cells):
  stage_cell.py   the S6F0 stage (code); its three byte-for-byte blobs are taken from nartaa's pulled script by this builder
  stage_md.md     its markdown cell
  stage3_block.py / stage3_loop.py   the stage-3 hunks
  header.md       cell 0
"""
import ast
import hashlib
import json
from pathlib import Path

REPO = Path("E:/Project/RSNA_Knee_Abnormality_Detection")
D = Path(__file__).parent
CELLS = D / "cells"
NARTAA = REPO / "external/kernels/nartaa__rsna-knee-s6fall-solo_20261015/rsna-knee-s6fall-solo.py"
DS = REPO / "external/datasets/nartaa__rsna-knee-s6fall-weights_20261015"
BASE = "v54"
AFTER = 11   # base cell after which the S6F stage is inserted (the R224 stage)

def ev(node):
    """value of a constant expression (literals, 20 * 60, dict/list/tuple of those); raises for anything that needs a name"""
    return eval(compile(ast.Expression(node), "<const>", "eval"), {"__builtins__": {}}, {})


sha = lambda b: hashlib.sha256(b).hexdigest()
src = lambda c: "".join(c["source"])

# ---------------------------------------------------------------------------------------------------------------------
# 0. nartaa's script: the three blobs we embed byte for byte, and the pinned hashes of his files
# ---------------------------------------------------------------------------------------------------------------------
nartaa_bytes = NARTAA.read_bytes()
NARTAA_SHA = sha(nartaa_bytes)
assert NARTAA_SHA == "2f2d50d8add7c8d2166577cdc16e511def9fa53620d431e25188be06da0aaa24", NARTAA_SHA
tree = ast.parse(nartaa_bytes.decode("utf-8"))
blobs = {}
consts = {}
for node in tree.body:
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        continue
    tg = node.targets[0]
    if isinstance(tg, ast.Name):
        if tg.id in ("PROBE", "LAUNCHER", "B_PROBE"):
            blobs[tg.id] = node.value.value
        try:
            consts[tg.id] = ev(node.value)
        except Exception:
            pass
    elif isinstance(tg, ast.Tuple) and isinstance(node.value, ast.Tuple):   # e.g. ANATOMY_FILE, ANATOMY_SHA256 = "...", "..."
        for t, v in zip(tg.elts, node.value.elts):
            try:
                consts[t.id] = ev(v)
            except Exception:
                pass
assert sha(blobs["PROBE"].encode()) == "52000924e2478375c4c87edf186c4ccda729115e4bf5b1fb826adf132b4d5f46"
assert sha(blobs["LAUNCHER"].encode()) == "9798c08b9a6a14291462f485048380e2d03806f9a0fd9e8a04bb3826c5b5bcdc"
assert sha(blobs["B_PROBE"].encode()) == "71e37c3afe908bca372b2ad8dd48c2922ba1bd17c66895e169b90e2630980497"
for b in blobs.values():
    assert "'''" not in b

# the dataset files (downloaded into the git-ignored external/datasets) carry the pins
want_ds = {"E_prior_s42_fall.pt": "0c7297d58f061ab4e5d7c55046f51fa3e8934928046f0647a0c7854e98371c12",
           "s6_extras.bin": "ddc428d9f2cda0e1378b6731ca7efbdd0397978204763f2a2f81169979e50c8e",
           "code_manifest.json": "b66c574b5c0c13ccaa49d1219d41a8781431166186ef83e78cab6a9ba6b02d22",
           "E_prior_s42_fall.run_config.json": "36e49cf0c8db97e7f995482933911f018c32fca8c5933b4d64399c128c19c886",
           "E_prior_s42_fall.DONE.json": "acc99ed61393404feaa4f84a2e20ce27ad9f55a257b8e0d0760e83e105a20c6a"}
for fn, h in want_ds.items():
    assert sha((DS / fn).read_bytes()) == h, fn
assert consts["B_MODEL"]["sha256"] == want_ds["E_prior_s42_fall.pt"]

# ---------------------------------------------------------------------------------------------------------------------
# 1. the base notebook
# ---------------------------------------------------------------------------------------------------------------------
base_nb = json.loads((REPO / f"notebooks/{BASE}-submit.ipynb").read_text(encoding="utf-8"))
bc = base_nb["cells"]
assert len(bc) == 23
assert src(bc[0]).startswith(f"# {BASE} - ")
assert src(bc[1]).startswith(f"# {BASE} configuration") and f"VERSION = '{BASE}'" in src(bc[1])
assert src(bc[6]).startswith("ARM = 'E_lrprior'\nBUNDLE_ID = '8c7b666e27dc0e8f'")
assert src(bc[11]).startswith("# Stage 2b [r224]")
assert src(bc[12]).startswith("# Stage 3: per-finding rank blend")

# ---------------------------------------------------------------------------------------------------------------------
# 2. the stage cells
# ---------------------------------------------------------------------------------------------------------------------
STAGE_CODE = (CELLS / "stage_cell.py").read_text(encoding="utf-8")
for ph, key in (("__PROBE__", "PROBE"), ("__LAUNCHER__", "LAUNCHER"), ("__B_PROBE__", "B_PROBE")):
    assert STAGE_CODE.count("= r'''" + ph + "'''") == 1, ph
    STAGE_CODE = STAGE_CODE.replace("= r'''" + ph + "'''", "= r'''" + blobs[key] + "'''")
assert "__" not in "".join(l for l in STAGE_CODE.splitlines() if l.startswith("S6F_") and "r'''" in l)
STAGE_MD = (CELLS / "stage_md.md").read_text(encoding="utf-8").rstrip("\n") + "\n"
compile(STAGE_CODE, "s6f_stage", "exec")
# the embedded blobs equal nartaa's (the cell's own literals, evaluated)
st_tree = ast.parse(STAGE_CODE)
emb = {n.targets[0].id: n.value.value for n in st_tree.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
       and n.targets[0].id in ("S6F_PROBE", "S6F_LAUNCHER", "S6F_B_PROBE")}
assert emb == {"S6F_PROBE": blobs["PROBE"], "S6F_LAUNCHER": blobs["LAUNCHER"], "S6F_B_PROBE": blobs["B_PROBE"]}
# the constants copied from nartaa's script equal his
cst = {}
for n in st_tree.body:
    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
        try:
            cst[n.targets[0].id] = ev(n.value)
        except Exception:
            pass
assert cst["S6F_SOURCE_SHA"] == consts["SOURCE_SHA"] and cst["S6F_CODE_SHA"] == consts["CODE_SHA"], "pinned code hashes differ from nartaa's"
assert cst["S6F_ANATOMY_SHA256"] == consts["ANATOMY_SHA256"] and cst["S6F_ANATOMY_FILE"] == consts["ANATOMY_FILE"]
assert cst["S6F_GEOMETRY"] == consts["B_GEOMETRY"], (cst["S6F_GEOMETRY"], consts["B_GEOMETRY"])
assert cst["S6F_LAB"] == consts["LAB"] and cst["S6F_RECEIPT_SOURCES"] == consts["B_RECEIPT_SOURCES"]
assert cst["S6F_WORKERS"] == consts["B_WORKERS"] and cst["S6F_AMP"] == consts["B_AMP"]
assert cst["S6F_DEADLINE_MARGIN_S"] == consts["B_DEADLINE_MARGIN_S"] and cst["S6F_RETRY_MIN_S"] == consts["B_RETRY_MIN_S"]
assert cst["S6F_EXIT_GRACE_S"] == consts["EXIT_GRACE_S"] and cst["S6F_HEARTBEAT_S"] == consts["HEARTBEAT_S"]
for k in ("file", "sha256", "run_config", "done", "arm", "expect_epochs"):
    assert cst["S6F_MODEL"][k] == consts["B_MODEL"][k], k
assert cst["S6F_MODEL"]["expect_train_studies"] == consts["B_MODEL"]["expect_train"] == 4263   # his check reads expect_train_studies, which his dict lacks
assert cst["S6F_PAYLOAD_MAGIC"] == consts["PAYLOAD_MAGIC"]
assert {**cst["S6F_DATASET_SHA"], cst["S6F_MODEL"]["file"]: cst["S6F_MODEL"]["sha256"]} == want_ds

# ---------------------------------------------------------------------------------------------------------------------
# 3. the stage-3 blend: three hunks, each asserted to match exactly once
# ---------------------------------------------------------------------------------------------------------------------
S3_BLOCK = (CELLS / "stage3_block.py").read_text(encoding="utf-8").rstrip("\n") + "\n"
S3_LOOP = (CELLS / "stage3_loop.py").read_text(encoding="utf-8").rstrip("\n")
compile(S3_BLOCK.replace("pct_on", "pct_on"), "s3_block", "exec")
stage3 = src(bc[12])


def replace_once(text, old, new):
    assert text.count(old) == 1, ("anchor not found exactly once", old[:80], text.count(old))
    return text.replace(old, new)


for nm in ("A_S6F", "s6f_info", "S6F_PRED", "S6F_OK", "s6f_fail", "_d6", "_sc6", "_f6", "_ok6", "_rho6", "_x6f"):
    assert nm not in stage3, nm   # the base stage 3 must not already use these names
H1_OLD = "\n\n\ndef pct(v):\n"
stage3 = replace_once(stage3, H1_OLD, "\n\n" + S3_BLOCK + "\n\ndef pct(v):\n")
H2_OLD = "        rr = np.where(np.isnan(_x224), rr, (1.0 - A224) * rr + A224 * _x224)\n"
stage3 = replace_once(stage3, H2_OLD, H2_OLD.rstrip("\n") + "\n" + S3_LOOP + "\n")
H3_OLD = "'rank_basis': 'each model over its own non-failed rows', 'r224': r224_info}   # [r224] used / failed studies / reason"
stage3 = replace_once(stage3, H3_OLD, "'rank_basis': 'each model over its own non-failed rows', 'r224': r224_info,   # [r224] used / failed studies / reason\n"
                      "         's6f': s6f_info}   # [s6f] used / failed studies / reason / stage record")
compile(stage3, "stage3", "exec")

# ---------------------------------------------------------------------------------------------------------------------
# 4. header and configuration
# ---------------------------------------------------------------------------------------------------------------------
base_header = src(bc[0])
base_title, base_body = base_header.split("\n", 1)
header = (CELLS / "header.md").read_text(encoding="utf-8").rstrip("\n")
header = replace_once(header, "__NARTAA_SHA__", NARTAA_SHA)
header = replace_once(header, "__BASE_BODY__", base_body)
assert "__" not in header.replace("__init__", "")
cfg = src(bc[1])
for old, new in ((f"# {BASE} configuration", "# v61 configuration"), (f"VERSION = '{BASE}'", "VERSION = 'v61'"),
                 ("R224 in the Raptor slot'", "R224 in the Raptor slot, S6F0 in the ConvNeXt slot'")):
    cfg = replace_once(cfg, old, new)

# ---------------------------------------------------------------------------------------------------------------------
# 5. assemble and assert
# ---------------------------------------------------------------------------------------------------------------------
mk = lambda ctype, text: ({"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)} if ctype == "markdown" else
                          {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text.splitlines(keepends=True)})
new_cells, mapping = [], []
for i, c in enumerate(bc):
    c = dict(c)
    if i == 0:
        c["source"] = header.splitlines(keepends=True)
        kind = "changed"
    elif i == 1:
        c["source"] = cfg.splitlines(keepends=True)
        kind = "changed"
    elif i == 12:
        c["source"] = stage3.splitlines(keepends=True)
        kind = "changed"
    else:
        kind = "identical"
    new_cells.append(c)
    mapping.append((kind, i))
    if i == AFTER:
        new_cells.append(mk("markdown", STAGE_MD))
        mapping.append(("inserted", None))
        new_cells.append(mk("code", STAGE_CODE))
        mapping.append(("inserted", None))
assert len(new_cells) == len(bc) + 2
for (kind, i), c in zip(mapping, new_cells):
    if kind == "identical":
        assert c == bc[i] and src(c) == src(bc[i]), i   # whole cell dict, so type, metadata and outputs too
assert [src(c) for (k, i), c in zip(mapping, new_cells) if k == "identical"] == [src(bc[i]) for i in range(23) if i not in (0, 1, 12)]
nb = {**base_nb, "cells": new_cells}
out = REPO / "notebooks/v61-submit.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"v61 built from {BASE}, S6F stage after base cell {AFTER}; {len(new_cells)} cells; nartaa script sha256 {NARTAA_SHA[:16]}")
for j, ((kind, i), c) in enumerate(zip(mapping, new_cells)):
    if kind != "identical":
        what = "" if kind == "inserted" else f" (base cell {i})"
        print(f"  cell {j:2d}: {kind}{what}: {c['cell_type']}, {len(src(c))} chars, first line: {src(c).splitlines()[0][:100]!r}")
