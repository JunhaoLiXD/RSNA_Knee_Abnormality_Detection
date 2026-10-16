# Stage 5 [v63]: per finding, ranks over all test studies, weights fixed before any run and not tuned:
#   mix   = pct(0.5 x pct(v61 anchor) + 0.5 x pct(v62 recipe))       v61 anchor = v61's stage-3 output before the reader (v47_base_submission.csv)
#   final = pct((1 - BLEND_W) x pct(mix) + BLEND_W x pct(reader))   the reader at v61's 0.10 under v61's own use/fallback decision (cell 24);
#                                                                   without the reader, final = mix
# so the reader keeps its tested 0.10 (L33, L34, L37) instead of being halved by the 0.5/0.5 mix.
# v62 recipe = v62's stage-3 formula, unchanged (Raptor half = 0.65 rank(R384) + 0.35 rank(R224), each over its own non-failed studies;
# per-finding Raptor weight W62_RAPTOR_C, else 0.5; ours = R6; a study one side failed on takes the other side's rank), here with this
# notebook's R224 (anatomical mirror), used only if v61's stage 3 used it (blend_receipt.json); otherwise the Raptor half is R384 alone.
# R6 is not used, and submission.csv stays v61's byte for byte, if the stage was skipped or failed, its output is malformed, more than 3 % of
# the studies are unscored by R6, its mean per-finding Spearman with R7 is below 0.5 (from 50 jointly scored studies on), or anything raises.
import csv as _v63_csv
import hashlib as _v63_hashlib
import json as _v63_json
import time as _v63_time
import numpy as _v63_np
import pandas as _v63_pd

V63_W_ANCHOR = 0.5
W62_RAPTOR, W62_A224 = 0.5, 0.35
W62_RAPTOR_C = {'Medial OA': 0.5, 'Lateral OA': 0.2, 'PF OA': 0.6, 'Synovitis': 0.8, "Baker's": 0.35}   # v62 stage 3, verbatim
R6_MAX_FAIL_FRACTION = 0.03
R6_MIN_SPEARMAN = 0.5


def _v63_pct(v):
    return _v63_pd.Series(_v63_np.asarray(v, dtype=_v63_np.float64)).rank(method='average', pct=True).values


def _v63_pct_on(v, ok):
    r = _v63_np.full(len(v), _v63_np.nan)
    if ok.any():
        r[ok] = _v63_pct(_v63_np.asarray(v, dtype=_v63_np.float64)[ok])
    return r


def v62_recipe(raw, raw224, ours, our_fail, labels):
    """v62's stage-3 per-finding blend (its cell 9, lines 35-80) on aligned DataFrames; raw224 None = R224 unavailable."""
    n = len(raw)
    r384_fail = (raw.values == 0.5).all(axis=1)
    r224_fail = _v63_np.ones(n, dtype=bool) if raw224 is None else (raw224.values == 0.5).all(axis=1)
    rap_fail = r384_fail & r224_fail
    out = _v63_np.zeros((n, len(labels)))
    for j, c in enumerate(labels):
        r384 = _v63_pct_on(raw[c].values, ~r384_fail)
        r224 = _v63_np.full(n, _v63_np.nan) if raw224 is None else _v63_pct_on(raw224[c].values, ~r224_fail)
        rr = _v63_np.where(r384_fail, r224, _v63_np.where(r224_fail, r384, (1.0 - W62_A224) * r384 + W62_A224 * r224))
        ro = _v63_pct_on(ours[c].values, ~our_fail)
        wr = W62_RAPTOR_C.get(c, W62_RAPTOR)
        b = wr * rr + (1.0 - wr) * ro
        b[rap_fail] = ro[rap_fail]
        b[our_fail] = rr[our_fail]
        b[rap_fail & our_fail] = 0.5
        out[:, j] = b
    return out, {'raptor384_failed': int(r384_fail.sum()), 'raptor224_failed': int(r224_fail.sum()), 'ours_failed': int(our_fail.sum()),
                 'both_failed': int((rap_fail & our_fail).sum())}


def v63_blend(work, comp, r6_ok, r6_pred, reader, reader_w):
    """Returns (DataFrame to write or None for 'keep v61', receipt dict). reader: aligned reader DataFrame if v61 used it, else None.
    Reads only; writes nothing."""
    cols = list(_v63_pd.read_csv(comp / 'sample_submission.csv', nrows=0).columns)
    labels = cols[1:]
    test_ids = _v63_pd.read_csv(comp / 'test.csv', dtype={'StudyInstanceUID': str})['StudyInstanceUID'].tolist()
    n = len(test_ids)
    rec = {'w_anchor': V63_W_ANCHOR, 'w62_raptor_c': W62_RAPTOR_C, 'a224': W62_A224, 'rows': n, 'used_r6': False, 'reason': None,
           'reader_used': reader is not None, 'reader_w': reader_w}
    if not r6_ok:
        rec['reason'] = 'R6 stage not ok'
        return None, rec
    rd = lambda f: _v63_pd.read_csv(work / f, dtype={'StudyInstanceUID': str})
    def aligned(df, nm):
        assert df['StudyInstanceUID'].is_unique and sorted(df['StudyInstanceUID']) == sorted(test_ids), nm + ': rows differ from test.csv'
        assert set(labels) <= set(df.columns), nm + ': columns differ'
        df = df.set_index('StudyInstanceUID').loc[test_ids, labels].astype(float)
        assert _v63_np.isfinite(df.values).all(), nm + ': non-finite values'
        return df
    anchor = aligned(rd('v47_base_submission.csv'), 'v61 anchor')
    raw = aligned(rd('raptor_raw.csv'), 'raptor_raw')
    r6 = aligned(rd('ours_r6_sub.csv'), 'ours_r6_sub')
    assert ((r6.values >= 0) & (r6.values <= 1)).all(), 'R6 outside [0, 1]'
    raw224 = None
    try:
        if _v63_json.loads((work / 'blend_receipt.json').read_text())['r224']['used'] is True:   # v61's stage 3 used R224
            raw224 = aligned(rd('raptor224_raw.csv'), 'raptor224_raw')
    except Exception as _exc:
        raw224, rec['r224_error'] = None, repr(_exc)[:200]
    rec['r224_used'] = raw224 is not None
    scored = set()   # the R6 controller fills a failed study with the column mean: read what was scored (v62's rule)
    for f in r6_pred.glob('worker*/predictions.csv'):
        with open(f, encoding='utf-8') as fh:
            for r in _v63_csv.DictReader(fh):
                try:
                    v = [float(r[L]) for L in labels]
                except (KeyError, ValueError, TypeError):
                    continue
                if all(0. <= x <= 1. for x in v):
                    scored.add(r['StudyInstanceUID'])
    r6_fail = _v63_np.array([u not in scored for u in test_ids])
    rec['r6_failed'] = int(r6_fail.sum())
    if r6_fail.sum() > R6_MAX_FAIL_FRACTION * n:
        rec['reason'] = 'R6 unscored on %d of %d studies' % (r6_fail.sum(), n)
        return None, rec
    r7 = aligned(rd('ours_sub.csv'), 'ours_sub (R7)')
    ok = ~r6_fail
    if ok.sum() >= 50:
        rho = _v63_np.array([_v63_pd.Series(r6[c].values[ok]).corr(_v63_pd.Series(r7[c].values[ok]), method='spearman') for c in labels])
        rec['spearman_r6_vs_r7'] = {'mean': round(float(_v63_np.nanmean(rho)), 4) if _v63_np.isfinite(rho).any() else None,
                                    'min': round(float(_v63_np.nanmin(rho)), 4) if _v63_np.isfinite(rho).any() else None}
        if not (_v63_np.isfinite(rho).all() and rho.mean() >= R6_MIN_SPEARMAN):
            rec['reason'] = 'R6 does not agree with R7: %s' % _v63_np.round(rho, 3).tolist()
            return None, rec
    v62r, rec['v62_recipe'] = v62_recipe(raw, raw224, r6, r6_fail, labels)
    out = _v63_np.zeros((n, len(labels)))
    for j, c in enumerate(labels):
        mix = _v63_pct(V63_W_ANCHOR * _v63_pct(anchor[c].values) + (1.0 - V63_W_ANCHOR) * _v63_pct(v62r[:, j]))
        out[:, j] = mix if reader is None else _v63_pct((1.0 - reader_w) * mix + reader_w * _v63_pct(reader[c].values))
    if n >= 3:
        rec['spearman_anchor_vs_v62_recipe'] = {c: round(float(_v63_pd.Series(anchor[c].values).corr(_v63_pd.Series(v62r[:, j]), method='spearman')), 4)
                                                for j, c in enumerate(labels)}
    sub = _v63_pd.DataFrame(out.astype(_v63_np.float32), columns=labels)
    sub.insert(0, 'StudyInstanceUID', test_ids)
    sub = sub[cols]
    assert sub['StudyInstanceUID'].tolist() == test_ids and _v63_np.isfinite(sub[labels].values).all()
    assert ((sub[labels].values >= 0) & (sub[labels].values <= 1)).all()
    rec['used_r6'] = True
    return sub, rec


if __name__ != 'v63_local_test':
    _v63_sub_path = _V47_WORK / 'submission.csv'
    _v63_v61_bytes = _v63_sub_path.read_bytes()            # v61's complete output (cell 24); restored on every failure
    V63_RECEIPT = {'used_r6': False, 'reason': None}
    try:
        (_V47_WORK / 'v61_submission.csv').write_bytes(_v63_v61_bytes)
        _v63_reader = _reader_out if _use_reader else None   # v61's own reader decision and aligned output (cell 24)
        _v63_sub, V63_RECEIPT = v63_blend(_V47_WORK, _v47_comp, R6_OK, R6_PRED, _v63_reader, BLEND_W)
        if _v63_sub is not None:
            _v63_sub.to_csv(_v63_sub_path, index=False)
    except Exception as _exc:
        V63_RECEIPT = {'used_r6': False, 'reason': 'blend error: ' + repr(_exc)[:400]}
    try:
        if not V63_RECEIPT.get('used_r6'):
            _v63_sub_path.write_bytes(_v63_v61_bytes)
            print('V63_FALLBACK_TO_V61', V63_RECEIPT.get('reason'), flush=True)
        V63_RECEIPT['r6_stage'] = R6_STAGE
        V63_RECEIPT['v61_submission_sha256'] = _v63_hashlib.sha256(_v63_v61_bytes).hexdigest()
        V63_RECEIPT['submission_sha256'] = _v63_hashlib.sha256(_v63_sub_path.read_bytes()).hexdigest()
        V63_RECEIPT['elapsed_hours'] = round((_v63_time.time() - V47_T0) / 3600, 3)
        (_V47_WORK / 'v63_receipt.json').write_text(_v63_json.dumps(V63_RECEIPT, indent=1, default=str))
        print('NOTEBOOK_COMPLETE v63', _v63_json.dumps(V63_RECEIPT, default=str), flush=True)
    except Exception as _exc:   # bookkeeping only: never fail the submission here
        print('V63_RECEIPT_ERROR', repr(_exc)[:300], flush=True)
