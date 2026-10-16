"""Audit downloaded v61 commit outputs without executing or changing the notebook.

Usage: python scripts/d033/check_v61_gates.py [results/v61/run1]
This checks the three placeholder studies, not the hidden-test execution receipts.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results/v61/run1"
BASE = ROOT / "results/v54/run1"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


base_nb = read_json(ROOT / "notebooks/v54-submit.ipynb")
nb = read_json(ROOT / "notebooks/v61-submit.ipynb")
assert len(base_nb["cells"]) == 23 and len(nb["cells"]) == 25
inherited = []
for i, cell in enumerate(base_nb["cells"]):
    j = i if i <= 11 else i + 2
    if i in (0, 1, 12):  # Builder's documented header, config and blend changes.
        continue
    assert nb["cells"][j] == cell, f"Inherited cell changed: v54 {i}, v61 {j}"
    assert "".join(nb["cells"][j]["source"]).encode() == "".join(cell["source"]).encode()
    inherited.append(i)

blend = read_json(RUN / "blend_receipt.json")
s6f = blend["s6f"]
stage = s6f["stage"]
receipt = read_json(RUN / "ours_s6f_receipt.json")
reader = read_json(RUN / "v47_receipt.json")["decision"]
assert s6f["used"] is True and s6f["weight"] == 0.35 and s6f["failed"] == 0
assert stage["launched"] is True and stage["killed"] is False
assert stage["error"] is None and stage["skipped"] is None
assert all(x is False for x in stage["timed_out"])
# This stage has no aggregate rc field: successful per-part receipts are the evidence.
assert sum(x["scored"] for x in stage["part_receipts"]) == receipt["scored"] == 3
assert receipt["status"] == "PASS" and receipt["fallback_studies"] == 0
assert receipt["model"] == "E_prior_s42_fall.pt"
assert receipt["model_sha256"] == "0c7297d58f061ab4e5d7c55046f51fa3e8934928046f0647a0c7854e98371c12"
for name, expected in s6f["output_sha256"].items():
    assert sha(RUN / name) == expected, name
assert reader["used_reader"] is True and reader["reader"]["exit_code"] == 0
assert reader["blend_weight"] == 0.1
assert blend["raptor_failed"] == blend["ours_failed"] == 0
assert blend["r224"]["used"] is True and blend["r224"]["failed"] == 0

equal_outputs = ["raptor_sub.csv", "raptor224_sub.csv", "ours_sub.csv"]
for name in equal_outputs:
    assert (RUN / name).read_bytes() == (BASE / name).read_bytes(), name

columns = pd.read_csv(ROOT / "data/sample_submission.csv", nrows=0).columns.tolist()
ids = pd.read_csv(ROOT / "data/test.csv", dtype=str)["StudyInstanceUID"].tolist()


def predictions(name):
    df = pd.read_csv(RUN / name, dtype={"StudyInstanceUID": str})
    assert df.columns.tolist() == columns, name
    assert df["StudyInstanceUID"].tolist() == ids, name
    values = df[columns[1:]]
    assert np.isfinite(values.to_numpy()).all(), name
    assert ((values >= 0) & (values <= 1)).to_numpy().all(), name
    return values


def rank(df):
    return df.rank(method="average", pct=True)


r384 = rank(predictions("raptor_raw.csv"))
r224 = rank(predictions("raptor224_sub.csv"))
r7 = rank(predictions("ours_sub.csv"))
s6 = rank(predictions("ours_s6f_sub.csv"))
expected_base = (0.5 * (0.65 * r384 + 0.35 * r224) + 0.5 * (0.65 * r7 + 0.35 * s6)).astype(np.float32)
actual_base = predictions("v47_base_submission.csv")
base_diff = float(np.max(np.abs(expected_base.to_numpy() - actual_base.to_numpy())))
assert base_diff < 1e-7, base_diff
expected_final = rank(0.9 * rank(actual_base) + 0.1 * rank(predictions("v47_reader/reader.csv")))
final_diff = float(np.max(np.abs(expected_final.to_numpy() - predictions("submission.csv").to_numpy())))
assert final_diff < 1e-7, final_diff

report = {
    "status": "PASS", "scope": "downloaded commit run; 3 placeholder studies only",
    "inherited_cells_equal": inherited, "unchanged_stage_outputs": equal_outputs,
    "s6f_used": True, "s6f_scored": 3, "reader_used": True,
    "base_max_abs_diff": base_diff, "final_max_abs_diff": final_diff,
    "hidden_test_receipts_verified": False,
}
(RUN / "codex_gate_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
