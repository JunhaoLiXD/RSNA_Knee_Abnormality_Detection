"""Audit a commit run of a copied public notebook against the author's run output.

    python -I scripts/d033/audit_copy.py <our run dir> <author output dir>

Prints SHA-256 equality for every CSV the author's run wrote (submission.csv must match; raw probability dumps may differ by GPU
float noise, so their rank files are what matters), the maximum absolute difference for differing CSVs, receipt statuses and
failure counts, and the submission's column order against data/sample_submission.csv. Exit code 1 if submission.csv differs
beyond 1e-6 or the format is wrong.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def main():
    ours, author = Path(sys.argv[1]), Path(sys.argv[2])
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    ok = True
    for f in sorted(author.glob("*.csv")):
        g = ours / f.name
        if not g.is_file():
            print(f"MISSING {f.name}")
            ok &= f.name != "submission.csv"
            continue
        if sha(f) == sha(g):
            print(f"MATCH   {f.name}")
            continue
        try:
            a = pd.read_csv(f).set_index("StudyInstanceUID")
            b = pd.read_csv(g).set_index("StudyInstanceUID").loc[a.index, a.columns]
            d = float(np.abs(a.values.astype(float) - b.values.astype(float)).max())
            same_rank = all((a[c].rank() == b[c].rank()).all() for c in a.columns)
        except Exception as exc:
            d, same_rank = float("nan"), False
            print(f"DIFF    {f.name} (unreadable: {exc!r})")
        print(f"DIFF    {f.name} max {d:.3g} ranks {'equal' if same_rank else 'DIFFER'}")
        if f.name == "submission.csv" and not (d <= 1e-6):
            ok = False
    for f in sorted(ours.glob("*receipt*.json")):
        try:
            r = json.loads(f.read_text())
            info = {k: v for k, v in r.items() if "fail" in k or k in ("status", "bundle_id")}
            print(f"RECEIPT {f.name}: {info}")
        except Exception as exc:
            print(f"RECEIPT {f.name}: unreadable {exc!r}")
    sub = pd.read_csv(ours / "submission.csv")
    cols = list(pd.read_csv(REPO / "data/sample_submission.csv", nrows=0).columns)
    fmt = list(sub.columns) == cols and int(sub.isna().sum().sum()) == 0
    print("FORMAT", "ok" if fmt else "WRONG", list(sub.columns) == cols, int(sub.isna().sum().sum()))
    ok &= fmt
    print("AUDIT", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
