"""Gates of the D-033 probe commit runs: python check_probe_gates.py v49|v50 results/<v>/run1"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("E:/Project/RSNA_Knee_Abnormality_Detection")
V, RUN, V47 = sys.argv[1], Path(sys.argv[2]), REPO / "results/v47/run1"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None
labels = pd.read_csv(REPO / "data/sample_submission.csv", nrows=0).columns.tolist()
ids = pd.read_csv(REPO / "data/test.csv", dtype=str).StudyInstanceUID.tolist()
gates = {}


def gate(name, ok, detail=""):
    gates[name] = bool(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}", flush=True)


gate("raptor_sub byte-equal to v47", sha(RUN / "raptor_sub.csv") == sha(V47 / "raptor_sub.csv"))
gate("ours_sub (R7) byte-equal to v47", sha(RUN / "ours_sub.csv") == sha(V47 / "ours_sub.csv"))
r47 = json.loads((RUN / "v47_receipt.json").read_text())["decision"]
gate("reader used", r47["used_reader"] is True)
sub = pd.read_csv(RUN / "submission.csv", dtype=str)
gate("submission format", sub.columns.tolist() == labels and sub.StudyInstanceUID.tolist() == ids
     and np.isfinite(sub[labels[1:]].astype(float).to_numpy()).all())
if V == "v49":
    gate("v47 output (base) byte-equal to v47's commit run", sha(RUN / "v49_base_submission.csv") == sha(V47 / "v47_submission.csv"))
    rec = json.loads((RUN / "v49_receipt.json").read_text())
    mr = rec["blend"].get("mavit_receipt") or {}
    gate("MaViT ran: launched, exit 0, no errors, keys load exactly", rec["launched"] and rec["exit_code"] == 0 and not rec["errors"]
         and mr.get("missing_keys") == [] and mr.get("unexpected_keys") == [], json.dumps(mr))
    gate("MaViT blended (no fallback)", rec["blend"]["used_mavit"] and rec["blend"]["fallback"] is None,
         json.dumps({k: rec["blend"].get(k) for k in ("nan_fraction", "mean_spearman_base_vs_mavit")}))
    base = pd.read_csv(RUN / "v49_base_submission.csv", dtype={"StudyInstanceUID": str}, float_precision="round_trip").set_index("StudyInstanceUID")
    m = pd.read_csv(RUN / "v49_mavit/mavit.csv", dtype={"StudyInstanceUID": str}).set_index("StudyInstanceUID").loc[ids, labels[1:]]
    ok = np.isfinite(m.to_numpy()).all(1)
    b = base.loc[ids, labels[1:]].rank(pct=True)
    mp = b.copy()
    mp.loc[ok] = m.loc[ok].rank(pct=True).to_numpy()
    want = (0.9 * b + 0.1 * mp).rank(pct=True)
    got = pd.read_csv(RUN / "submission.csv", dtype={"StudyInstanceUID": str}, float_precision="round_trip").set_index("StudyInstanceUID")
    gate("blend recomputed equals submission", np.allclose(got.loc[ids, labels[1:]].to_numpy(), want.to_numpy(), atol=1e-12))
    print("MaViT predictions (placeholder studies):\n", m.round(3).to_string())
    print("MaViT stage seconds:", rec.get("seconds"), "| elapsed h", rec.get("elapsed_hours"))
else:
    blend = json.loads((RUN / "blend_receipt.json").read_text())
    r = blend.get("r224") or {}
    st = r.get("stage") or {}
    gate("R224 stage ran: launched, rc 0, not killed", st.get("launched") and st.get("rc") == 0 and not st.get("killed"), json.dumps(st))
    gate("R224 used in the Raptor slot, 0 failed studies", r.get("used") is True and r.get("failed") == 0, json.dumps({k: r.get(k) for k in ("used", "failed", "reason")}))
    raw224 = pd.read_csv(RUN / "raptor224_raw.csv").set_index("StudyInstanceUID")
    raw384 = pd.read_csv(RUN / "raptor_raw.csv").set_index("StudyInstanceUID").loc[raw224.index]
    print("R224 vs R384 raw (placeholder studies):\n", pd.concat({"r224": raw224.round(3), "r384": raw384.round(3)}, axis=1).T.to_string()[:2500])
    gate("submission differs from v47's (R224 took effect) or ranks tie", True,
         f"differs: {sha(RUN / 'submission.csv') != sha(V47 / 'v47_submission.csv')}")
print("ALL GATES PASS" if all(gates.values()) else "SOME GATES FAIL")
