"""Gates of the v48 commit run (R7 flip-TTA): python check_v48_gates.py results/v48/run1"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("E:/Project/RSNA_Knee_Abnormality_Detection")
RUN, V47 = Path(sys.argv[1]), REPO / "results/v47/run1"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
gates = {}


def gate(name, ok, detail=""):
    gates[name] = bool(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}", flush=True)


log = (RUN / "v48-submit.log").read_text(encoding="utf-8", errors="replace")
wlogs = "".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted(RUN.glob("worker*_log.txt")))
gate("G1 Raptor stage unchanged (raptor_sub, raptor_raw ranks)", sha(RUN / "raptor_sub.csv") == sha(V47 / "raptor_sub.csv"))
gate("G2 flip-TTA active (notebook marker and worker FLIP_TTA_READY)", "V48_FLIP_TTA --flip-tta" in log and "FLIP_TTA_READY" in wlogs)
r = json.loads((RUN / "submission_receipt.json").read_text())
gate("G3 R7 stage done, all studies scored, no fallback", r.get("status") in ("done", "ok") and r.get("fallback_studies") in (0, [], None)
     and r.get("scored") == r.get("rows"), json.dumps({k: r.get(k) for k in ("status", "rows", "scored", "fallback_studies", "seconds")}))
r47 = json.loads((V47 / "submission_receipt.json").read_text())
gate("G4 R7 output changed vs v47 (TTA took effect)", sha(RUN / "ours_sub.csv") != sha(V47 / "ours_sub.csv"))
o48 = pd.read_csv(RUN / "ours_sub.csv").set_index("StudyInstanceUID")
o47 = pd.read_csv(V47 / "ours_sub.csv").set_index("StudyInstanceUID").loc[o48.index, o48.columns]
print("max |ours_sub v48 - v47| per column:", (o48 - o47).abs().max().round(4).to_dict())
mcl_same = np.allclose(o48["MCL"], o47["MCL"], atol=0) if "MCL" in o48 else None
print("MCL column identical to v47 (expected only if the MCL stacker/plain pass leaves ranks unchanged):", mcl_same)
gate("G5 reader and final blend ran, submission format", (RUN / "v47_receipt.json").is_file()
     and json.loads((RUN / "v47_receipt.json").read_text())["decision"]["used_reader"] is True)
sub = pd.read_csv(RUN / "submission.csv", dtype=str)
labels = pd.read_csv(REPO / "data/sample_submission.csv", nrows=0).columns.tolist()
ids = pd.read_csv(REPO / "data/test.csv", dtype=str).StudyInstanceUID.tolist()
gate("G6 submission columns, ids, finite", sub.columns.tolist() == labels and sub.StudyInstanceUID.tolist() == ids
     and np.isfinite(sub[labels[1:]].astype(float).to_numpy()).all())
print("R7 stage seconds v48 vs v47:", r.get("seconds"), r47.get("seconds"), "| per study", r.get("per_study_mean"), r47.get("per_study_mean"))
print("ALL GATES PASS" if all(gates.values()) else "SOME GATES FAIL", json.dumps(gates))
