"""Audit the v28 local-view cache (100 mm field) against the v07 cache (140 mm field).

Design `docs/research/v25-local-views-design.md` revision 2, section 4 and review findings 6-7:
1. study coverage and errors;
2. per (study, slot) the v07 facts must match: presence, series, series length, stored count, flips, reversal,
   sort method;
3. per study the stored slot and raw slice index arrays must match (all studies);
4. on a stratified sample: how much of the v07 foreground lies inside the central 100 mm (a clipping proxy),
   the foreground centroid offset in mm, the zero-padding share of the v28 slice, and the normalised
   cross-correlation between the v28 slice and the matching central crop of the v07 slice (orientation and
   centring check), summarised by plane, side, field of view and manufacturer;
5. montages (v07 slice with the 100 mm box | v28 slice) for random and worst cases, for a visual check.

Usage: python scripts/audit_v28_cache.py --v28 results/v28/full1/v28 --v07 results/v07/full3/v07 --out results/v28/audit
(run from the repository root)
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

SLOTS = ['SAG_FS', 'SAG_NFS', 'COR_FS', 'COR_OTHER', 'AX_FS']
FACTS = ['present', 'SeriesInstanceUID', 'n_series_slices', 'n_stored', 'flip_lr', 'flip_ud', 'reverse', 'sort_method']
V07_MM, V28_MM, PX = 140.0, 100.0, 320
BOX = int(round(PX * V28_MM / V07_MM))          # 229 px: the 100 mm field inside a v07 slice


def load(path):
    with np.load(path) as z:
        return z['jpeg'], z['offsets'], z['slot'], z['raw_index']


def decode(jpeg, offsets, k):
    return cv2.imdecode(np.frombuffer(jpeg[offsets[k]:offsets[k + 1]].tobytes(), np.uint8), cv2.IMREAD_GRAYSCALE)


def ncc(a, b):
    a, b = a.astype(np.float64).ravel(), b.astype(np.float64).ravel()
    a, b = a - a.mean(), b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else float('nan')


def slice_metrics(img07, img28):
    _, fg = cv2.threshold(img07, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    c0 = (PX - BOX) // 2
    total = float(fg.sum())
    inside = float(fg[c0:c0 + BOX, c0:c0 + BOX].sum())
    ys, xs = np.nonzero(fg)
    off = float(np.hypot(xs.mean() - PX / 2, ys.mean() - PX / 2) * V07_MM / PX) if len(xs) else float('nan')
    crop = img07[c0:c0 + BOX, c0:c0 + BOX]
    small28 = cv2.resize(img28, (BOX, BOX), interpolation=cv2.INTER_AREA)
    return {'inside_frac': inside / total if total else float('nan'), 'centroid_offset_mm': off,
            'zero_share_v28': float((img28 == 0).mean()), 'ncc': ncc(crop, small28)}


def tile(img07, img28, label):
    a = cv2.cvtColor(img07, cv2.COLOR_GRAY2BGR)
    c0 = (PX - BOX) // 2
    cv2.rectangle(a, (c0, c0), (c0 + BOX, c0 + BOX), (0, 0, 255), 1)
    b = cv2.cvtColor(img28, cv2.COLOR_GRAY2BGR)
    t = np.concatenate([a, np.full((PX, 4, 3), 255, np.uint8), b], 1)
    bar = np.zeros((18, t.shape[1], 3), np.uint8)
    cv2.putText(bar, label[:90], (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    return np.concatenate([bar, t], 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--v28', required=True)
    ap.add_argument('--v07', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--v06', default='results/v06/run1/v06', help='v06 audit outputs (series field of view)')
    ap.add_argument('--sample', type=int, default=800, help='studies in the stratified metric sample')
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    v28, v07, out = Path(a.v28), Path(a.v07), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rep = {}

    s07 = pd.read_csv(v07 / 'v07_cache_studies.csv', dtype={'StudyInstanceUID': str})
    s28 = pd.read_csv(v28 / 'v28_cache_studies.csv', dtype={'StudyInstanceUID': str})
    ok07 = set(s07[s07.error.fillna('') == ''].StudyInstanceUID)
    ok28 = set(s28[s28.error.fillna('') == ''].StudyInstanceUID)
    rep['studies'] = {'v07_ok': len(ok07), 'v28_ok': len(ok28), 'v28_errors': int(len(s28) - len(ok28)),
                      'missing_in_v28': len(ok07 - ok28), 'extra_in_v28': len(ok28 - ok07)}

    i07 = pd.read_csv(v07 / 'v07_cache_index.csv', dtype={'StudyInstanceUID': str, 'SeriesInstanceUID': str})
    i28 = pd.read_csv(v28 / 'v28_cache_index.csv', dtype={'StudyInstanceUID': str, 'SeriesInstanceUID': str})
    m = i07.merge(i28, on=['StudyInstanceUID', 'slot'], how='outer', suffixes=('_07', '_28'), indicator=True)
    rep['index'] = {'rows_07': len(i07), 'rows_28': len(i28), 'unmatched_rows': int((m._merge != 'both').sum())}
    both = m[m._merge == 'both']
    mism = {}
    for c in FACTS:
        x, y = both[f'{c}_07'].astype(str), both[f'{c}_28'].astype(str)
        mism[c] = int((x != y).sum())
    rep['index']['fact_mismatches'] = mism

    bad_arrays = []
    common = sorted(ok07 & ok28)
    for k, uid in enumerate(common):
        _, _, sl7, r7 = load(v07 / 'cache' / f'{uid}.npz')
        _, _, sl8, r8 = load(v28 / 'cache' / f'{uid}.npz')
        if not (np.array_equal(sl7, sl8) and np.array_equal(r7, r8)):
            bad_arrays.append(uid)
    rep['arrays'] = {'studies_checked': len(common), 'mismatched': len(bad_arrays), 'examples': bad_arrays[:10]}

    # stratified sample: studies, one middle slice per present slot
    ser = pd.read_csv(Path(a.v06) / 'v06_series_audit.csv',
                      dtype={'StudyInstanceUID': str, 'SeriesInstanceUID': str},
                      usecols=['SeriesInstanceUID', 'fov_mm', 'pixel_spacing', 'Manufacturer'])
    side = s07.set_index('StudyInstanceUID')['side'] if 'side' in s07 else pd.Series(dtype=str)
    rng = np.random.default_rng(a.seed)
    sample = rng.choice(common, size=min(a.sample, len(common)), replace=False).tolist()
    pres = i07[i07.present.astype(str) == 'True'].merge(ser, on='SeriesInstanceUID', how='left')
    pres = pres[pres.StudyInstanceUID.isin(sample)]
    rows = []
    for uid, g in pres.groupby('StudyInstanceUID'):
        j7, o7, sl7, _ = load(v07 / 'cache' / f'{uid}.npz')
        j8, o8, sl8, _ = load(v28 / 'cache' / f'{uid}.npz')
        for r in g.itertuples(index=False):
            sel = np.flatnonzero(sl7 == SLOTS.index(r.slot))
            if len(sel) == 0:
                continue
            k = int(sel[len(sel) // 2])
            met = slice_metrics(decode(j7, o7, k), decode(j8, o8, k))
            rows.append({'StudyInstanceUID': uid, 'slot': r.slot, 'k': k, 'side': side.get(uid, ''),
                         'fov_mm': r.fov_mm, 'manufacturer': r.Manufacturer, **met})
    df = pd.DataFrame(rows)
    df['fov_bin'] = pd.cut(pd.to_numeric(df.fov_mm, errors='coerce'), [0, 120, 160, 200, 1000],
                           labels=['<120', '120-160', '160-200', '>200'])
    df.to_csv(out / 'v28_audit_slices.csv', index=False)
    q = lambda s: {'n': int(s.notna().sum()), 'median': round(float(s.median()), 4), 'p05': round(float(s.quantile(0.05)), 4),
                   'min': round(float(s.min()), 4)}
    rep['sample'] = {'studies': len(sample), 'slices': len(df), 'inside_frac': q(df.inside_frac), 'ncc': q(df.ncc),
                     'centroid_offset_mm_p95': round(float(df.centroid_offset_mm.quantile(0.95)), 1),
                     'zero_share_v28_p95': round(float(df.zero_share_v28.quantile(0.95)), 4),
                     'share_inside_below_0.8': round(float((df.inside_frac < 0.8).mean()), 4),
                     'share_ncc_below_0.8': round(float((df.ncc < 0.8).mean()), 4)}
    strata = {}
    for col in ('slot', 'side', 'fov_bin', 'manufacturer'):
        g = df.groupby(col, observed=True)
        strata[col] = {str(k): {'n': int(len(v)), 'inside_median': round(float(v.inside_frac.median()), 3),
                                'inside_p05': round(float(v.inside_frac.quantile(0.05)), 3),
                                'ncc_median': round(float(v.ncc.median()), 3), 'ncc_p05': round(float(v.ncc.quantile(0.05)), 3)}
                       for k, v in g}
    rep['strata'] = strata

    # montages: per slot 4 random, the 12 lowest inside fractions, the 8 lowest NCC, the 4 smallest fields of view
    picks = [df[df.slot == s].sample(min(4, (df.slot == s).sum()), random_state=a.seed) for s in SLOTS]
    picks += [df.nsmallest(12, 'inside_frac'), df.nsmallest(8, 'ncc'),
              df.assign(f=pd.to_numeric(df.fov_mm, errors='coerce')).nsmallest(4, 'f').drop(columns='f')]
    sel = pd.concat(picks).drop_duplicates(['StudyInstanceUID', 'slot'])
    tiles = []
    for r in sel.itertuples(index=False):
        j7, o7, _, _ = load(v07 / 'cache' / f'{r.StudyInstanceUID}.npz')
        j8, o8, _, _ = load(v28 / 'cache' / f'{r.StudyInstanceUID}.npz')
        lab = f'{r.StudyInstanceUID[-8:]} {r.slot} {r.side} fov {float(r.fov_mm):.0f} mm in {r.inside_frac:.2f} ncc {r.ncc:.2f}'
        tiles.append(tile(decode(j7, o7, r.k), decode(j8, o8, r.k), lab))
    per_page, cols = 12, 3
    for p in range(0, len(tiles), per_page):
        page = tiles[p:p + per_page]
        while len(page) % cols:
            page.append(np.zeros_like(tiles[0]))
        grid = np.concatenate([np.concatenate(page[i:i + cols], 1) for i in range(0, len(page), cols)], 0)
        cv2.imwrite(str(out / f'v28_audit_montage_{p // per_page + 1:02d}.png'), grid)
    rep['montages'] = {'tiles': len(tiles), 'pages': (len(tiles) + per_page - 1) // per_page}
    (out / 'v28_audit.json').write_text(json.dumps(rep, indent=2, default=str))
    print(json.dumps({k: rep[k] for k in ('studies', 'index', 'arrays', 'sample', 'montages')}, indent=2, default=str))


if __name__ == '__main__':
    main()
