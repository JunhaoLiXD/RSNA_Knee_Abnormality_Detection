# [s6f] nartaa's all-data S6 ConvNeXt-small (S6F0, public 0.950 alone) as a second model of the ConvNeXt slot: slot rank = (1 - A_S6F) * rank(R7) +
# A_S6F * rank(S6F0), each ranked over the studies it scored (R224's rule); a study S6F0 failed on keeps R7's rank alone, so an unusable S6F0 (stage
# skipped, killed, failed or malformed, more than 3 % of the studies unscored, implausible agreement with R7) leaves this cell exactly as without S6F0.
# A_S6F is fixed before any run (the R224 precedent) and is not tuned.
A_S6F = 0.35
S6F_MAX_FAIL_FRACTION = 0.03   # more unscored studies than this and S6F0 is not used at all
S6F_MIN_SPEARMAN = 0.5         # sanity floor, mean per-finding Spearman of S6F0 against R7 (checked from 50 jointly scored studies on)
s6f, s6f_fail = None, np.zeros(n, dtype=bool)
s6f_info = {'weight': A_S6F, 'stage': dict(globals().get('S6F_STAGE') or {}), 'used': False, 'failed': None, 'reason': None}
if globals().get('S6F_OK', False):
    try:
        import hashlib
        s6f_info['output_sha256'] = {f: hashlib.sha256((WORK / f).read_bytes()).hexdigest() for f in ('ours_s6f_sub.csv', 'ours_s6f_receipt.json')}
        _d6 = pd.read_csv(WORK / 'ours_s6f_sub.csv', dtype={'StudyInstanceUID': str})
        assert sorted(_d6['StudyInstanceUID']) == sorted(test_ids) and set(labels) <= set(_d6.columns), 'S6F rows or columns differ from test.csv'
        _d6 = _d6.set_index('StudyInstanceUID').loc[test_ids, labels]
        assert np.isfinite(_d6.values).all() and ((_d6.values >= 0) & (_d6.values <= 1)).all(), 'S6F probabilities not finite or outside [0, 1]'
        _sc6 = {}   # the failure mask is read from the workers' own files: a study is scored when a worker wrote a complete row inside [0, 1]
        for f in sorted(S6F_PRED.glob('part*/predictions.csv')) + sorted(S6F_PRED.glob('retry/predictions.csv')):
            with open(f, encoding='utf-8') as fh:
                for r in csv.DictReader(fh):
                    try:
                        v = [float(r[L]) for L in labels]
                    except (KeyError, ValueError, TypeError):
                        continue
                    if all(0. <= x <= 1. for x in v):
                        _sc6[r['StudyInstanceUID']] = v
        _f6 = np.array([u not in _sc6 for u in test_ids])   # S6F fills an unscored study with the column mean: never read as a prediction
        _rc6 = json.loads((WORK / 'ours_s6f_receipt.json').read_text())
        s6f_info['receipt'] = {k: _rc6.get(k) for k in ('status', 'rows', 'scored', 'fallback_studies', 'seconds', 'n_gpu')}
        assert int(_rc6.get('rows', -1)) == n and int(_rc6.get('scored', -1)) == int((~_f6).sum()), 'S6F receipt does not match the worker predictions'
        _ix6 = np.flatnonzero(~_f6)
        assert len(_ix6) > 0 and np.abs(_d6.values[_ix6] - np.array([_sc6[test_ids[i]] for i in _ix6])).max() < 1e-5, 'S6F csv differs from the worker predictions'
        if _f6.sum() > S6F_MAX_FAIL_FRACTION * n:
            raise RuntimeError('S6F did not score %d of %d studies (more than %.0f %%)' % (_f6.sum(), n, 100 * S6F_MAX_FAIL_FRACTION))
        _ok6 = ~our_fail & ~_f6   # studies both ConvNeXt models scored
        assert _ok6.any(), 'no study scored by both R7 and S6F'
        if _ok6.sum() >= 50:
            _rho6 = np.array([pd.Series(ours[c].values[_ok6]).corr(pd.Series(_d6[c].values[_ok6]), method='spearman') for c in labels])
            s6f_info['spearman_vs_r7'] = {'mean': round(float(np.nanmean(_rho6)), 4), 'min': round(float(np.nanmin(_rho6)), 4)}
            assert np.isfinite(_rho6).all() and _rho6.mean() >= S6F_MIN_SPEARMAN, 'S6F does not agree with R7: %s' % np.round(_rho6, 3)
        s6f, s6f_fail = _d6, _f6
        s6f_info.update(used=True, failed=int(_f6.sum()))
        print('S6F_USED weight %.2f, S6F unscored %d of %d, scored by both ConvNeXt models %d' % (A_S6F, int(_f6.sum()), n, int(_ok6.sum())), flush=True)
    except Exception as _e:   # missing, truncated or implausible S6F output: the blend is exactly the base's
        print('S6F_UNUSABLE', repr(_e), flush=True)
        s6f, s6f_fail = None, np.zeros(n, dtype=bool)
        s6f_info['reason'] = repr(_e)[:300]
else:
    s6f_info['reason'] = 'S6F stage not ok or not run'
