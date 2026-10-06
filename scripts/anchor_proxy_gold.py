"""Proxy of the v05 public-stack anchor on the 58 gold studies, from public member predictions.

The anchor (v05) cannot be scored on training data, but several of its members published
predictions: out-of-fold predictions on all training studies (pilkwang DINOv2 x20, antoinegg1
RadImageNet heads) and held-out gold predictions (mattiaangeli CoAtNet packages, selected on
gold, so optimistic). This script rank-blends them into three fixed proxy variants (pre-registered in
design v13 revision 3; a diagnostic, never a veto) and reports what a candidate leg adds to it on gold.

Usage:
    python scripts/anchor_proxy_gold.py --leg name=path_or_glob [--leg ...] [--weights 0.1,0.2,0.3,0.45]

A leg is one CSV with StudyInstanceUID and the 12 label columns, or a glob of per-fold CSVs
(rank-averaged). Inputs live in external/datasets/ (not tracked; see docs/research/
anchor-components-2026-10-06.md for sources). Calibration (2026-10-06): the proxy reproduces
v09 (v08 leg at w 0.45: -0.010 on gold vs -0.011 on the public LB); one point only.
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / 'external' / 'datasets'
LABELS = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA',
          'PF OA', 'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']
# Pre-registered proxy variants (rank space; design v13 revision 3). The proxy is a diagnostic,
# reported for all variants; no variant has a veto over a submission.
PROXY_VARIANTS = {
    'coat_heavy': {'dino': 0.5, 'rad': 0.5, 'coat_rg': 1.0, 'coat_g96': 1.5, 'coat_d4': 1.5},
    'equal5': {'dino': 1.0, 'rad': 1.0, 'coat_rg': 1.0, 'coat_g96': 1.0, 'coat_d4': 1.0},
    'coat_only': {'coat_rg': 1.0, 'coat_g96': 1.0, 'coat_d4': 1.0},
}
MEMBER_FILES = {
    'dino': ('npz_oof', 'pilkwang__rsna-knee-weights/oof.npz'),
    'rad': ('csv', 'antoinegg1__rsna-knee-e9-radimagenet-heads-v15/v52_oof.csv'),
    'coat_rg': ('npz_gold', 'mattiaangeli__rsna-knee-coat-resgated-ep10-top3/gold58_top3_predictions.npz'),
    'coat_g96': ('npz_gold', 'mattiaangeli__rsna-knee-coatnet-global96-top3/coatnet_global96_gold58_reference.npz'),
    'coat_d4': ('npz_gold', 'mattiaangeli__rsna-knee-coatnet-d4-depthzone-swa3-b2/d4_gold58_reference.npz'),
}


def rank(a):
    return pd.DataFrame(a).rank(pct=True).to_numpy()


def macro(y, p):
    return float(np.nanmean([roc_auc_score(y[:, j], p[:, j]) for j in range(len(LABELS))
                             if 0 < y[:, j].sum() < len(y)]))


def load_gold():
    t = pd.read_csv(ROOT / 'results/v06/run1/v06/v06_targets.csv', dtype={'StudyInstanceUID': str})
    t = t.set_index('StudyInstanceUID')
    gold = t.index[t.is_gold.astype(bool)].tolist()
    return gold, t.loc[gold, [f'{c}__gold' for c in LABELS]].to_numpy(float)


def load_member(kind, rel, gold):
    path = EXT / rel
    if kind == 'npz_oof':
        z = np.load(path)
        df = pd.DataFrame(z['pred'], index=[str(s) for s in z['ids']], columns=[str(c) for c in z['targets']])
    elif kind == 'csv':
        df = pd.read_csv(path, dtype={'StudyInstanceUID': str}).set_index('StudyInstanceUID')
    else:
        z = np.load(path)
        df = pd.DataFrame(z['probability_mean'], index=[str(s) for s in z['study_uids']], columns=LABELS)
    return df.loc[gold, LABELS].to_numpy(float)


def load_leg(spec, gold):
    files = sorted(glob.glob(str(ROOT / spec))) or [spec]
    parts = [pd.read_csv(f, dtype={'StudyInstanceUID': str}).set_index('StudyInstanceUID').loc[gold, LABELS]
             .to_numpy(float) for f in files]
    return rank(sum(rank(p) for p in parts)), len(files)


def proxies(gold):
    members = {k: load_member(kind, rel, gold) for k, (kind, rel) in MEMBER_FILES.items()}
    return {v: rank(sum(w * rank(members[k]) for k, w in wts.items())) for v, wts in PROXY_VARIANTS.items()}, members


def paired(y, a, b, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(n):
        s = rng.integers(0, len(y), len(y))
        d.append(macro(y[s], b[s]) - macro(y[s], a[s]))
    d = np.asarray(d)
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)), float((d <= 0).mean())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--leg', action='append', default=[], help='name=path_or_glob')
    ap.add_argument('--weights', default='0.1,0.2,0.3,0.45')
    args = ap.parse_args()
    gold, y = load_gold()
    anchors, members = proxies(gold)
    print('members on gold: ' + ', '.join(f'{k} {macro(y, v):.3f}' for k, v in members.items()))
    print('proxy anchors on gold: ' + ', '.join(f'{v} {macro(y, a):.4f}' for v, a in anchors.items()))
    for spec in args.leg:
        name, path = spec.split('=', 1)
        leg, n = load_leg(path, gold)
        print(f'{name} ({n} file(s)): alone {macro(y, leg):.4f}')
        for variant, anchor in anchors.items():
            for w in (float(x) for x in args.weights.split(',')):
                blend = rank((1 - w) * anchor + w * leg)
                lo, hi, p0 = paired(y, anchor, blend)
                print(f'  {variant:10s} w={w:.2f}: gain {macro(y, blend) - macro(y, anchor):+.4f} '
                      f'(95% CI {lo:+.4f} to {hi:+.4f}, P(gain <= 0) {p0:.3f})')


if __name__ == '__main__':
    main()
