# [__VER__] second model of the compact slot (v61's [s6f] rule, A2 = 0.35, fixed before any run, not tuned): per finding
#   slot rank = (1 - V63_A2) x rank(R6) + V63_A2 x rank(M2), each ranked over its own non-failed studies; a study M2 failed on
#   keeps rank(R6) alone, a study R6 failed on keeps rank(M2) alone (a study both failed on takes the Raptor half, v62's rule).
# M2 = __M2_NAME__. M2 is not used at all (slot = R6 alone, output exactly v64's) if its output is missing or malformed, more than
# 3 % of the studies are unscored by M2, its mean per-finding Spearman with R6 is below 0.5 (from 50 jointly scored studies on),
# or anything in v63_m2 raises (v63_m2 catches every exception).  The slot ranks enter v62_recipe unchanged (not re-ranked).
from pathlib import Path as _V63Path

V63_M2 = '__M2__'
V63_A2 = 0.35
M2_MAX_FAIL_FRACTION = 0.03
M2_MIN_SPEARMAN = 0.5


def _v63_scored(paths, labels):
    """Studies with a complete row inside [0, 1] in the workers' own predictions files (the controllers fill an unscored study
    with the column mean in the submission csv, so the csv alone cannot tell)."""
    scored = set()
    for f in paths:
        with open(f, encoding='utf-8') as fh:
            for r in _v63_csv.DictReader(fh):
                try:
                    v = [float(r[L]) for L in labels]
                except (KeyError, ValueError, TypeError):
                    continue
                if all(0. <= x <= 1. for x in v):
                    scored.add(r['StudyInstanceUID'])
    return scored


def v63_m2(work, test_ids, labels, r6, r6_fail, aligned, rd):
    """Returns ((slot ranks n x L, M2 failure mask) or None for 'R6 alone', info dict).  Never raises."""
    info = {'model': V63_M2, 'weight': V63_A2, 'used': False, 'failed': None, 'reason': None}
    try:
        n = len(test_ids)
        rc = _v63_json.loads((work / 'blend_receipt.json').read_text())   # v61's stage-3 receipt (cell 14)
        if V63_M2 == 'r7':
            # R7 = v61's own compact model.  `pred` is bound once in the main namespace (v61 cell 8: TMP / 'prediction', the R7
            # controller's --output) and never rebound by a later executed cell (cell 22 only writes a file).
            m2_pred = globals().get('pred')
            assert m2_pred is not None, 'R7 prediction folder (pred) not bound'
            paths = sorted(_V63Path(m2_pred).glob('worker*/predictions.csv'))
            m2 = aligned(rd('ours_sub.csv'), 'ours_sub (R7)')
            expected_failed = rc['ours_failed']
        else:
            # S6F0 = v61's [s6f] model, only if v61's stage 3 used it; failure mask read as v61 cell 14 reads it.
            assert rc['s6f']['used'] is True, 'S6F0 not used by v61 stage 3: %r' % (rc['s6f'].get('reason'),)
            m2_pred = globals().get('S6F_PRED')
            assert m2_pred is not None, 'S6F prediction folder (S6F_PRED) not bound'
            paths = sorted(_V63Path(m2_pred).glob('part*/predictions.csv')) + sorted(_V63Path(m2_pred).glob('retry/predictions.csv'))
            m2 = aligned(rd('ours_s6f_sub.csv'), 'ours_s6f_sub (S6F0)')
            expected_failed = rc['s6f']['failed']
        assert paths, 'no M2 worker predictions file'
        assert ((m2.values >= 0) & (m2.values <= 1)).all(), 'M2 outside [0, 1]'
        scored = _v63_scored(paths, labels)
        m2_fail = _v63_np.array([u not in scored for u in test_ids])
        info['failed'] = int(m2_fail.sum())
        assert int(m2_fail.sum()) == int(expected_failed), 'M2 unscored %d, v61 receipt says %r' % (m2_fail.sum(), expected_failed)
        if m2_fail.sum() > M2_MAX_FAIL_FRACTION * n:
            raise RuntimeError('M2 unscored on %d of %d studies' % (m2_fail.sum(), n))
        ok = ~r6_fail & ~m2_fail   # studies both compact models scored
        assert ok.any(), 'no study scored by both R6 and M2'
        if ok.sum() >= 50:
            rho = _v63_np.array([_v63_pd.Series(r6[c].values[ok]).corr(_v63_pd.Series(m2[c].values[ok]), method='spearman') for c in labels])
            info['spearman_vs_r6'] = {'mean': round(float(_v63_np.nanmean(rho)), 4) if _v63_np.isfinite(rho).any() else None,
                                      'min': round(float(_v63_np.nanmin(rho)), 4) if _v63_np.isfinite(rho).any() else None}
            if not (_v63_np.isfinite(rho).all() and rho.mean() >= M2_MIN_SPEARMAN):
                raise RuntimeError('M2 does not agree with R6: %s' % _v63_np.round(rho, 3).tolist())
        slot = _v63_np.zeros((n, len(labels)))
        for j, c in enumerate(labels):
            a = _v63_pct_on(r6[c].values, ~r6_fail)
            b = _v63_pct_on(m2[c].values, ~m2_fail)
            slot[:, j] = _v63_np.where(r6_fail, b, _v63_np.where(m2_fail, a, (1.0 - V63_A2) * a + V63_A2 * b))
        assert _v63_np.isfinite(slot[~(r6_fail & m2_fail)]).all(), 'non-finite slot rank'
        info['used'] = True
        return (slot, m2_fail), info
    except Exception as _exc:   # any problem: the slot is R6 alone, exactly v64
        info['used'], info['reason'] = False, repr(_exc)[:300]
        return None, info


