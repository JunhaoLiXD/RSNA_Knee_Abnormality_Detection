"""LLM label-repair pilot (D-025, docs/research/llm-labels-feasibility-2026-10-11.md section 7).

Subcommands (run from the repository root with the `kaggle` env):
  frame     per-cell table of the four public sources of the v06 target, disagreement flags, report groups
  sample    development and pilot report sets (non-gold, identical reports read once), blinded batch files
  validate  check reader outputs against the schema
  compare   proposed corrections: reader status with evidence that contradicts the four-source mean

Outputs go to results/llm/ (not tracked). Batch files hold only an id and the report text (readers are blind to
the existing labels).
"""
import argparse
import glob
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "external" / "datasets"
OUT = ROOT / "results" / "llm"
L = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA', 'PF OA',
     'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']
SOURCES = {   # the v06 target's four tables (notebooks/v06-dicom-audit.ipynb, LABEL_FILES)
    'pilkwang': EXT / 'pilkwang__rsna-knee-llm-labels/report_labels_v2.csv',
    'steven': EXT / 'stevenleehans__rsna-knee-llm-report-labels/llm_labels_v2.csv',
    'lixin': EXT / 'lixin73__rsna-knee-llm-report-labels-sol56/labels_llm_gpt56sol.csv',
    'dread': EXT / 'dreaddevelopment__rsna-knee-labels/labels_llm_soft.csv',
}
STATUSES = {'present', 'absent', 'uncertain', 'not_mentioned'}
LO, HI = 0.2, 0.8


def norm_report(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def frame(_):
    OUT.mkdir(parents=True, exist_ok=True)
    train = pd.read_csv(ROOT / "data/train.csv", dtype={"StudyInstanceUID": str})
    t = pd.read_csv(ROOT / "results/v06/run1/v06/v06_targets.csv", dtype={"StudyInstanceUID": str}).set_index("StudyInstanceUID")
    studies = t.index[~t.is_gold.astype(bool)]
    tabs = {k: pd.read_csv(p, dtype={"StudyInstanceUID": str}).drop_duplicates("StudyInstanceUID").set_index("StudyInstanceUID")
            for k, p in SOURCES.items()}
    rows = []
    for c in L:
        st = np.stack([tabs[k].reindex(studies)[c].to_numpy(float) for k in SOURCES], 1)
        df = pd.DataFrame(st, index=studies, columns=list(SOURCES))
        df["finding"] = c
        df["soft"] = t.loc[studies, c].to_numpy(float)
        df["weight"] = t.loc[studies, f"{c}__weight"].to_numpy(float)
        df["src_min"], df["src_max"] = np.nanmin(st, 1), np.nanmax(st, 1)
        df["disagree"] = (df.src_min <= LO) & (df.src_max >= HI)
        rows.append(df.reset_index())
    cells = pd.concat(rows, ignore_index=True)
    rep = train.set_index("StudyInstanceUID").loc[studies, "Report"].map(norm_report)
    gid = rep.map(lambda s: hashlib.sha1(s.encode()).hexdigest()[:12])
    cells["group"] = cells.StudyInstanceUID.map(gid)
    cells.to_csv(OUT / "frame_cells.csv", index=False)
    g = gid.value_counts()
    summ = {"studies": int(len(studies)), "cells": int(len(cells)), "disagree_cells": int(cells.disagree.sum()),
            "disagree_share": round(float(cells.disagree.mean()), 4),
            "disagree_studies": int(cells.loc[cells.disagree, "StudyInstanceUID"].nunique()),
            "disagree_by_finding": cells.groupby("finding").disagree.sum().astype(int).loc[L].to_dict(),
            "downweighted_share": round(float((cells.weight < 1).mean()), 4),
            "report_groups": int(len(g)), "groups_with_duplicates": int((g > 1).sum()),
            "studies_in_duplicate_groups": int(g[g > 1].sum())}
    (OUT / "frame_summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=2))


def sample(a):
    cells = pd.read_csv(OUT / "frame_cells.csv", dtype={"StudyInstanceUID": str})
    train = pd.read_csv(ROOT / "data/train.csv", dtype={"StudyInstanceUID": str}).set_index("StudyInstanceUID")
    rng = np.random.default_rng(a.seed)
    groups = cells.drop_duplicates("StudyInstanceUID")[["StudyInstanceUID", "group"]]
    rep_of = groups.drop_duplicates("group").set_index("group").StudyInstanceUID   # one representative per group
    all_groups = sorted(rep_of.index)
    dis = cells[cells.disagree]
    taken, sets = set(), {}
    for name, n_rand, n_enr in (("dev", a.dev // 2, a.dev - a.dev // 2), ("pilot", a.pilot // 2, a.pilot - a.pilot // 2)):
        pool = [g for g in all_groups if g not in taken]
        rand = list(rng.choice(pool, size=n_rand, replace=False))
        taken.update(rand)
        enr, per = [], int(np.ceil(n_enr / len(L)))
        for c in L:   # enriched: groups with a disagreement in this finding, spread over findings
            cand = sorted(set(dis.loc[dis.finding == c, "group"]) - taken - set(enr))
            pick = list(rng.choice(cand, size=min(per, len(cand)), replace=False))
            enr += pick
        enr = enr[:n_enr]
        taken.update(enr)
        sets[name] = pd.DataFrame({"group": rand + enr, "stratum": ["random"] * len(rand) + ["enriched"] * len(enr)})
    for name, df in sets.items():
        df["StudyInstanceUID"] = df.group.map(rep_of)
        df["rid"] = [f"{name}_{i:04d}" for i in range(len(df))]
        df = df.sample(frac=1, random_state=a.seed).reset_index(drop=True)   # strata mixed in every batch
        df.to_csv(OUT / f"set_{name}.csv", index=False)
        bdir = OUT / "batches" / name
        bdir.mkdir(parents=True, exist_ok=True)
        for b in range(0, len(df), a.batch):
            part = df.iloc[b:b + a.batch]
            recs = [{"rid": r.rid, "report": str(train.loc[r.StudyInstanceUID, "Report"])} for r in part.itertuples()]
            (bdir / f"{name}_b{b // a.batch:02d}.json").write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
        print(name, len(df), df.stratum.value_counts().to_dict(), "batches", (len(df) + a.batch - 1) // a.batch)


def validate(a):
    bad, n = [], 0
    for f in sorted(glob.glob(str(OUT / "reads" / a.reader / "*.json"))):
        try:
            recs = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception as exc:
            bad.append((f, f"json: {exc}"))
            continue
        for r in recs:
            n += 1
            fs = r.get("findings", {})
            if set(fs) != set(L):
                bad.append((r.get("rid"), f"findings keys {sorted(set(L) ^ set(fs))}"))
                continue
            for c, v in fs.items():
                if v.get("status") not in STATUSES or not 0 <= float(v.get("p", -1)) <= 1:
                    bad.append((r.get("rid"), f"{c}: {v}"))
                if v.get("status") in ("present", "absent", "uncertain") and not str(v.get("evidence", "")).strip():
                    bad.append((r.get("rid"), f"{c}: no evidence for {v.get('status')}"))
    print(f"{a.reader}: {n} reports, {len(bad)} problems")
    for b in bad[:20]:
        print("  ", b)


def compare(a):
    cells = pd.read_csv(OUT / "frame_cells.csv", dtype={"StudyInstanceUID": str})
    sets = pd.concat([pd.read_csv(f, dtype={"StudyInstanceUID": str}) for f in glob.glob(str(OUT / "set_*.csv"))])
    rid2group = sets.set_index("rid").group
    rows = []
    for f in sorted(glob.glob(str(OUT / "reads" / a.reader / "*.json"))):
        for r in json.loads(Path(f).read_text(encoding="utf-8")):
            for c, v in r["findings"].items():
                rows.append({"rid": r["rid"], "group": rid2group[r["rid"]], "finding": c, **{k: v.get(k) for k in ("status", "p", "evidence", "qualifier")}})
    reads = pd.DataFrame(rows)
    cg = cells.drop_duplicates(["group", "finding"])[["group", "finding", "soft", "weight", "disagree"] + list(SOURCES)]
    m = reads.merge(cg, on=["group", "finding"], how="left")
    # a proposed correction: an asserted or denied finding with evidence on the other side of 0.5 by a margin
    m["proposed"] = ((m.status == "present") & (m.soft < 0.5 - a.margin)) | ((m.status == "absent") & (m.soft > 0.5 + a.margin))
    m.to_csv(OUT / f"compare_{a.reader}.csv", index=False)
    p = m[m.proposed]
    print(f"{a.reader}: {m.rid.nunique()} reports, {len(m)} cells; status counts {m.status.value_counts().to_dict()}")
    print(f"proposed corrections: {len(p)} in {p.rid.nunique()} reports; by finding {p.finding.value_counts().to_dict()}")
    print("share of proposed among disagreement cells:", round(float(m.loc[m.disagree == True, 'proposed'].mean()), 3),
          "| among other cells:", round(float(m.loc[m.disagree == False, 'proposed'].mean()), 3))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("frame").set_defaults(fn=frame)
    s = sp.add_parser("sample")
    s.add_argument("--dev", type=int, default=40)
    s.add_argument("--pilot", type=int, default=200)
    s.add_argument("--batch", type=int, default=20)
    s.add_argument("--seed", type=int, default=2026)
    s.set_defaults(fn=sample)
    v = sp.add_parser("validate")
    v.add_argument("reader")
    v.set_defaults(fn=validate)
    c = sp.add_parser("compare")
    c.add_argument("reader")
    c.add_argument("--margin", type=float, default=0.2)
    c.set_defaults(fn=compare)
    args = ap.parse_args()
    args.fn(args)
