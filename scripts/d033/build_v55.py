"""Build notebooks/v55-submit.ipynb = BASE (v54 by default, or v53) + heliosli's old S6 ConvNeXt bundle as a second model in the
ConvNeXt slot of stage 3 (weight A_S6 = 0.35, fixed).  Every base cell is byte-identical except the header (cell 0), the
configuration (cell 1) and the stage-3 blend (three hunks); two cells (markdown + code) are inserted.

    python build_v55.py [v54|v53] [--after 11|8]

--after 11 (default): the S6 stage runs after the R224 stage (R224 keeps its place and its own cut-off; S6 gets what is left).
--after 8: the S6 stage runs directly after the R7 run cell.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path("E:/Project/RSNA_Knee_Abnormality_Detection")
args = sys.argv[1:]
AFTER = 11
if "--after" in args:
    AFTER = int(args[args.index("--after") + 1])
    del args[args.index("--after"):args.index("--after") + 2]
BASE = args[0] if args else "v54"
assert BASE in ("v53", "v54") and AFTER in (8, 11), (BASE, AFTER)

src = lambda c: "".join(c["source"])
base_nb = json.loads((REPO / f"notebooks/{BASE}-submit.ipynb").read_text(encoding="utf-8"))
bc = base_nb["cells"]
assert len(bc) == 23

# ---- locate the base cells by content (not only by index)
assert src(bc[0]).startswith(f"# {BASE} - ")
assert src(bc[1]).startswith(f"# {BASE} configuration") and f"VERSION = '{BASE}'" in src(bc[1])
assert src(bc[6]).startswith("ARM = 'E_lrprior'\nBUNDLE_ID = '8c7b666e27dc0e8f'")
assert src(bc[8]).lstrip().startswith("deadline = T0 + DEADLINE_HOURS * 3600")
assert src(bc[11]).startswith("# Stage 2b [r224]")
assert src(bc[12]).startswith("# Stage 3: per-finding rank blend")

# ---------------------------------------------------------------------------------------------------------------------
# 1. the S6 setup function, generated from the base setup cell's own lines (so it cannot drift from what v37 / R7 run)
# ---------------------------------------------------------------------------------------------------------------------
lines = src(bc[6]).split("\n")
i0 = lines.index("BUNDLE = TMP / 'bundle'")
i1 = next(i for i, l in enumerate(lines) if l.startswith("print('ASSETS_READY'"))
body = lines[i0:i1]
SUBS = {
    "BUNDLE = TMP / 'bundle'": "BUNDLE = TMP / 'bundle_s6'",
    "M_SRC = find_mount(C_SLUG, 'manifest.json')": "M_SRC = find_mount(S6_SLUG, 'manifest.json')",
    "assert manifest['bundle_id'] == BUNDLE_ID, (manifest['bundle_id'], BUNDLE_ID)":
        "assert manifest['bundle_id'] == S6_BUNDLE_ID, (manifest['bundle_id'], S6_BUNDLE_ID)",
}
for old, new in SUBS.items():
    assert body.count(old) == 1, old
    body[body.index(old)] = new
joined = "\n".join(body)
assert "C_SLUG" not in joined and not re.search(r"(?<!S6_)BUNDLE_ID", joined), "unsubstituted base name left in the S6 setup"
assert "'''" not in joined and '"""' not in joined and "\\\n" not in joined
assert "ASSETS_READY" not in joined and "flip" in joined   # the flip branch is the manifest's own (S6 has none); see the guard below
setup_fn = (
    "def _s6_prepare():\n"
    "    # Lines 'BUNDLE = ...' to the last worker argument of the R7 setup cell above, copied line for line (same checks, same\n"
    "    # argument construction as v37 used for this bundle); only the bundle folder and the manifest slug / id are the S6 ones.\n"
    "    # Everything is a local of this function, so no global of the R7 setup (manifest, BUNDLE, WORKER_ARGS, M_SRC) is rebound.\n"
    + "\n".join(("    " + l) if l.strip() else l for l in body)
    + "\n"
    "    assert not manifest.get('flip_tta') and '--flip-tta' not in WORKER_ARGS, WORKER_ARGS   # S6 was not trained with the mirror\n"
    "    return manifest, BUNDLE, WORKER, WORKER_ARGS, M_SRC\n"
)
compile(setup_fn, "s6_prepare", "exec")

# ---------------------------------------------------------------------------------------------------------------------
# 2. the S6 stage cells
# ---------------------------------------------------------------------------------------------------------------------
STAGE_MD = """## Stage 2s: heliosli's old S6 ConvNeXt-small (the addition)

S6 (bundle `209a32c8b50a6b1c`, four ConvNeXt-small folds from `heliosli/rsna-knee-compact-v1`) runs through the same embedded
sources and mainline code as the R7 stage above (the S6 and R7 notebooks embed byte-identical sources), with its own bundle
folder (`bundle_s6`), output folder (`prediction_s6`) and output files (`ours_s6_sub.csv`, `ours_s6_receipt.json`). It runs in its own
process group under an absolute cut-off that leaves the outer reader its launch allowance, and never rebinds a name of the R7 setup.
Any failure, timeout, skip or malformed output leaves `S6_OK` False and stage 3 exactly as without this stage.
"""

STAGE_CODE = '''# Stage 2s [s6]: heliosli's old S6 ConvNeXt-small bundle (heliosli/rsna-knee-compact-v1, bundle 209a32c8b50a6b1c, 4 folds) as a second
# model of the ConvNeXt slot. Idea and recipe: rudrpratapsingh's "Four public models, one rank blend" (S6 through R7's embedded code with
# --compile, an S6 deadline, a study S6 missed keeps R7 alone); the weight and the gates are ours (stage 3, [s6] block).
# The stage ends by V47_T0 + READER_DEADLINE_S - READER_MIN_S - S6_MARGIN_S (the cut-off of the R224 stage), is not started with
# less than S6_MIN_S before it, and runs in its own process group that is killed on every exit path. Any failure, timeout, skip or
# malformed output leaves S6_OK False, so stage 3 is exactly as without S6; stage 3 validates the output again before using it.
import os, signal, subprocess, sys, time
S6_OK = False
S6_PRED = None
S6_STAGE = {'launched': False, 'skipped': None, 'rc': None, 'killed': False, 'error': None, 'seconds': None,
            'minutes_left_at_start': None, 'worker_args': None, 'receipt': None, 'compile': None}
S6_BUNDLE_ID = '209a32c8b50a6b1c'
S6_SLUG = 'rsna-knee-compact-v1'   # versioned copy of the S6 files (the author's r6cnxfsss slug is non-versioned: Kaggle refuses it)
S6_MIN_S = 50 * 60                # not started with less than this left before the cut-off
S6_MARGIN_S = 15 * 60             # slack between the cut-off and the reader's launch allowance (as the R224 stage)
S6_COOP_S = 5 * 60                # workers stop taking new studies this long before the cut-off, so the controller can merge
S6_COMPILE = True                 # as in R7's manifest: torch.compile of the encoders (checked against eager inside the worker, eager fallback)
S6_FILES = ('ours_s6_sub.csv', 'ours_s6_receipt.json')


''' + setup_fn + '''

try:
    for _s6_f in S6_FILES:   # no stale file can be mistaken for this run's output
        if (WORK / _s6_f).is_file():
            (WORK / _s6_f).unlink()
    S6_PRED = TMP / 'prediction_s6'
    shutil.rmtree(S6_PRED, ignore_errors=True)
    _s6_end = V47_T0 + READER_DEADLINE_S - READER_MIN_S - S6_MARGIN_S
    _s6_left = _s6_end - time.time()
    S6_STAGE['minutes_left_at_start'] = round(_s6_left / 60)
    if _s6_left < S6_MIN_S:
        S6_STAGE['skipped'] = 'only %.0f min left' % (_s6_left / 60)
        print('S6_SKIPPED', S6_STAGE['skipped'], flush=True)
    else:
        _s6_t0 = time.time()
        _s6_manifest, _s6_bundle, _s6_worker, _s6_args, _s6_msrc = _s6_prepare()
        if S6_COMPILE and '--compile' not in _s6_args:
            _s6_args = _s6_args + ['--compile']
        S6_STAGE['worker_args'] = list(_s6_args)
        print('S6_ASSETS_READY', str(_s6_msrc), 'seconds %.1f' % (time.time() - _s6_t0), flush=True)
        _s6_env = dict(os.environ, PYTHONPATH=str(CODE) + os.pathsep + os.environ.get('PYTHONPATH', ''), PYTHONDONTWRITEBYTECODE='1')
        _s6_p = subprocess.Popen([sys.executable, '-u', str(SRC / 'probe_dual.py'), '--data', str(DATA), '--split', 'test',
                                  '--code', str(CODE), '--bundle', str(_s6_bundle), '--arm', ARM, '--output', str(S6_PRED),
                                  '--amp', 'auto', '--loader-workers', '2', '--deadline', str(_s6_end - S6_COOP_S),
                                  '--worker', _s6_worker, '--worker-args', json.dumps(_s6_args),
                                  '--max-fallback-fraction', '1.0'], env=_s6_env, start_new_session=True)   # own process group
        S6_STAGE['launched'] = True
        try:
            S6_STAGE['rc'] = _s6_p.wait(timeout=max(1.0, _s6_end - time.time()))
        except subprocess.TimeoutExpired:
            S6_STAGE['killed'] = True
        finally:
            try:
                os.killpg(_s6_p.pid, signal.SIGKILL)   # controller, workers and prefetch workers, on every exit path
            except Exception:
                try:
                    _s6_p.kill()   # no process group to signal: at least the controller itself
                except Exception:
                    pass
            try:
                _s6_p.wait(timeout=60)
            except Exception:
                pass
        S6_STAGE['seconds'] = round(time.time() - _s6_t0, 1)
        for _s6_log in sorted(S6_PRED.glob('worker*/log.txt')):
            try:
                shutil.copyfile(_s6_log, WORK / ('s6_' + _s6_log.parent.name + '_log.txt'))
            except Exception:
                pass
        if S6_STAGE['rc'] == 0 and not S6_STAGE['killed'] and (S6_PRED / 'submission.csv').is_file() and (S6_PRED / 'submission_receipt.json').is_file():
            shutil.copyfile(S6_PRED / 'submission.csv', WORK / 'ours_s6_sub.csv')
            shutil.copyfile(S6_PRED / 'submission_receipt.json', WORK / 'ours_s6_receipt.json')
            _s6_rc = json.loads((S6_PRED / 'submission_receipt.json').read_text())
            S6_STAGE['receipt'] = {k: _s6_rc.get(k) for k in ('status', 'rows', 'scored', 'fallback_studies', 'seconds', 'per_study_mean', 'gpus', 'worker_exit_codes')}
            S6_STAGE['compile'] = [{k: (w.get('compile') or {}).get(k) for k in ('requested', 'active', 'fallback')} for w in _s6_rc.get('workers', [])]
            S6_STAGE['workers_timed_out'] = [w.get('timed_out') for w in _s6_rc.get('workers', [])]
            S6_OK = True
        print('S6_STAGE', json.dumps(S6_STAGE, default=str), 'ok=%s' % S6_OK, flush=True)
except Exception as _s6_exc:   # never stop the notebook: stage 3 then blends without S6
    S6_OK = False
    S6_STAGE['error'] = repr(_s6_exc)[:300]
    print('S6_STAGE_ERROR', S6_STAGE['error'], flush=True)
'''
compile(STAGE_CODE, "s6_stage", "exec")

# ---------------------------------------------------------------------------------------------------------------------
# 3. the stage-3 blend: three hunks, each asserted to match exactly once
# ---------------------------------------------------------------------------------------------------------------------
S6_BLOCK = '''# [s6] heliosli's old S6 ConvNeXt-small as a second model of the ConvNeXt slot: slot rank = (1 - A_S6) * rank(R7) + A_S6 * rank(S6), each
# ranked over the studies it scored (R224's rule); a study S6 failed on keeps R7's rank alone, so an unusable S6 (stage skipped, killed,
# failed or malformed, more than 3 % of the studies unscored, implausible agreement with R7) leaves this cell exactly as without S6.
# A_S6 is fixed before any run (the R224 precedent) and is not tuned.
A_S6 = 0.35
S6_MAX_FAIL_FRACTION = 0.03   # more unscored studies than this and S6 is not used at all
S6_MIN_SPEARMAN = 0.5         # sanity floor, mean per-finding Spearman of S6 against R7 (checked from 50 jointly scored studies on)
s6, s6_fail = None, np.zeros(n, dtype=bool)
s6_info = {'weight': A_S6, 'stage': dict(globals().get('S6_STAGE') or {}), 'used': False, 'failed': None, 'reason': None}
if globals().get('S6_OK', False):
    try:
        import hashlib
        s6_info['output_sha256'] = {f: hashlib.sha256((WORK / f).read_bytes()).hexdigest() for f in ('ours_s6_sub.csv', 'ours_s6_receipt.json')}
        _d6 = pd.read_csv(WORK / 'ours_s6_sub.csv', dtype={'StudyInstanceUID': str})
        assert sorted(_d6['StudyInstanceUID']) == sorted(test_ids) and set(labels) <= set(_d6.columns), 'S6 rows or columns differ from test.csv'
        _d6 = _d6.set_index('StudyInstanceUID').loc[test_ids, labels]
        assert np.isfinite(_d6.values).all() and ((_d6.values >= 0) & (_d6.values <= 1)).all(), 'S6 probabilities not finite or outside [0, 1]'
        _sc6 = set()   # the failure mask is the one of the R7 stage: a study is scored when a worker wrote a complete row inside [0, 1]
        for f in S6_PRED.glob('worker*/predictions.csv'):
            with open(f, encoding='utf-8') as fh:
                for r in csv.DictReader(fh):
                    try:
                        v = [float(r[L]) for L in labels]
                    except (KeyError, ValueError, TypeError):
                        continue
                    if all(0. <= x <= 1. for x in v):
                        _sc6.add(r['StudyInstanceUID'])
        _f6 = np.array([u not in _sc6 for u in test_ids])   # S6 fills an unscored study with the column mean: never read as a prediction
        _rc6 = json.loads((WORK / 'ours_s6_receipt.json').read_text())
        s6_info['receipt'] = {k: _rc6.get(k) for k in ('status', 'rows', 'scored', 'fallback_studies')}
        assert int(_rc6.get('rows', -1)) == n and int(_rc6.get('scored', -1)) == int((~_f6).sum()), 'S6 receipt does not match the worker predictions'
        if _f6.sum() > S6_MAX_FAIL_FRACTION * n:
            raise RuntimeError('S6 did not score %d of %d studies (more than %.0f %%)' % (_f6.sum(), n, 100 * S6_MAX_FAIL_FRACTION))
        _ok6 = ~our_fail & ~_f6   # studies both ConvNeXt models scored
        assert _ok6.any(), 'no study scored by both R7 and S6'
        if _ok6.sum() >= 50:
            _rho6 = np.array([pd.Series(ours[c].values[_ok6]).corr(pd.Series(_d6[c].values[_ok6]), method='spearman') for c in labels])
            s6_info['spearman_vs_r7'] = {'mean': round(float(np.nanmean(_rho6)), 4), 'min': round(float(np.nanmin(_rho6)), 4)}
            assert np.isfinite(_rho6).all() and _rho6.mean() >= S6_MIN_SPEARMAN, 'S6 does not agree with R7: %s' % np.round(_rho6, 3)
        s6, s6_fail = _d6, _f6
        s6_info.update(used=True, failed=int(_f6.sum()))
        print('S6_USED weight %.2f, S6 unscored %d of %d, scored by both ConvNeXt models %d' % (A_S6, int(_f6.sum()), n, int(_ok6.sum())), flush=True)
    except Exception as _e:   # missing, truncated or implausible S6 output: the blend is exactly the base's
        print('S6_UNUSABLE', repr(_e), flush=True)
        s6, s6_fail = None, np.zeros(n, dtype=bool)
        s6_info['reason'] = repr(_e)[:300]
else:
    s6_info['reason'] = 'S6 stage not ok or not run'
'''
compile(S6_BLOCK, "s6_block", "exec")

S6_LOOP = '''
    if s6 is not None:   # [s6] ConvNeXt slot = (1 - A_S6) * rank(R7) + A_S6 * rank(S6) over the studies both scored; a study S6 failed on keeps rank(R7)
        _x6 = pct_on(s6[c].values, ~our_fail & ~s6_fail)
        ro = np.where(np.isnan(_x6), ro, (1.0 - A_S6) * ro + A_S6 * _x6)'''

stage3 = src(bc[12])


def replace_once(text, old, new):
    assert text.count(old) == 1, ("anchor not found exactly once", old[:80], text.count(old))
    return text.replace(old, new)


# hunk 1: the S6 block, between the failure checks and the rank helpers
H1_OLD = "\n\n\ndef pct(v):\n"
stage3 = replace_once(stage3, H1_OLD, "\n\n" + S6_BLOCK + "\n\ndef pct(v):\n")
# hunk 2: inside the per-finding loop, directly after the R224 mix
H2_OLD = "        rr = np.where(np.isnan(_x224), rr, (1.0 - A224) * rr + A224 * _x224)\n"
stage3 = replace_once(stage3, H2_OLD, H2_OLD.rstrip("\n") + S6_LOOP + "\n")
# hunk 3: the S6 record in blend_receipt.json
H3_OLD = "'rank_basis': 'each model over its own non-failed rows', 'r224': r224_info}   # [r224] used / failed studies / reason"
stage3 = replace_once(stage3, H3_OLD, "'rank_basis': 'each model over its own non-failed rows', 'r224': r224_info,   # [r224] used / failed studies / reason\n         's6': s6_info}   # [s6] used / failed studies / reason / stage record")
# the pre-existing S6 name check: stage 3 must not already use these names
for nm in ("A_S6", "s6_info", "S6_PRED"):
    assert nm not in src(bc[12]), nm
compile(stage3, "stage3", "exec")

# ---------------------------------------------------------------------------------------------------------------------
# 4. header and configuration
# ---------------------------------------------------------------------------------------------------------------------
base_header = src(bc[0])
base_title, base_body = base_header.split("\n", 1)
header = f"""# v55 - {BASE} + heliosli's old S6 in the ConvNeXt slot at 0.35 (D-033)

Explicit ensemble version (D-017), decision D-033 (`docs/research/silver-push-2026-10-14.md`). The base is {BASE}, unchanged
except for the cells listed under "Our changes": nartaa's 384-px CoAtNet with its 224-px sibling (R224) in the Raptor slot,
heliosli's R7 ConvNeXt-small (with its own flip-TTA) in the ConvNeXt slot, the outer goodpjw2008 reader. The addition is a second
ConvNeXt model in the ConvNeXt slot: heliosli's older S6 bundle.

## Provenance of the addition

- Model: heliosli's compact ConvNeXt-small S6, bundle `209a32c8b50a6b1c` (four folds, side classifier, state spec), read from the
  versioned dataset `heliosli/rsna-knee-compact-v1` (the same files as the author's `rsna-knee-compact-r6cnxfsss`, which Kaggle
  refuses as non-versioned; every file is checked against the manifest's SHA-256 at run time). Code: the embedded sources and the
  setup lines of heliosli's R7 notebook (Apache 2.0), which are byte-identical to the S6 notebook's (v37 reproduced that notebook:
  https://www.kaggle.com/code/heliosli/blend-mine-in-private-lb-luck-to-all-upvoters, Apache 2.0). The S6 worker arguments are built
  by the same setup lines from the S6 manifest, as in v37; no flip-TTA (the S6 manifest has none).
- Idea: rudrpratapsingh's public notebook "RSNA Knee | Four public models, one rank blend"
  (https://www.kaggle.com/code/rudrpratapsingh/rsna-knee-four-public-models-one-rank-blend; unscored when pulled on 2026-10-14):
  R7 and S6 together in the ConvNeXt slot, S6 run through R7's embedded code with `--compile`, an S6 deadline, a study S6 missed
  keeps R7 alone. We reuse the idea and those three design points, not that notebook's cells.

## Our changes (against {BASE})

1. This cell and the configuration cell (`VERSION = 'v55'`).
2. New cells "Stage 2s [s6]" (markdown + code): the S6 setup as a function of the R7 setup's own lines (local names only: no global of
   the R7 setup is rebound, `submission_receipt.json` is not touched), S6 through `probe_dual.py` into its own folder with `--compile`,
   an absolute cut-off at `READER_DEADLINE_S - READER_MIN_S - 15 min` (the R224 cut-off; the reader keeps its launch allowance), no
   start with less than 50 min left, a cooperative deadline 5 min earlier, its own process group killed on every exit path.
3. Stage-3 blend, three hunks: an `[s6]` validation block, one mix in the per-finding loop
   (ConvNeXt slot rank = 0.65 x rank(R7) + 0.35 x rank(S6) over the studies both scored; a study S6 failed on keeps rank(R7)), and
   an `s6` record in `blend_receipt.json`. S6 is not used (stage 3 equals {BASE}'s) when the stage did not finish, its output is
   malformed, more than 3 % of the studies are unscored by S6, or its mean per-finding Spearman with R7 is below 0.5 (from 50
   jointly scored studies on).
4. Every other cell is byte-identical to {BASE} (asserted in the builder).

Weight 0.35 is fixed before any run (the R224 precedent), not tuned. Extra input to attach: `heliosli/rsna-knee-compact-v1`.

---

Base notebook header ({BASE}):
{base_body}"""
cfg = src(bc[1])
for old, new in ((f"# {BASE} configuration", "# v55 configuration"), (f"VERSION = '{BASE}'", "VERSION = 'v55'"),
                 ("R224 in the Raptor slot'", "R224 in the Raptor slot, S6 in the ConvNeXt slot'")):
    cfg = replace_once(cfg, old, new)

# ---------------------------------------------------------------------------------------------------------------------
# 5. assemble and assert
# ---------------------------------------------------------------------------------------------------------------------
mk = lambda ctype, text: ({"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)} if ctype == "markdown" else
                          {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text.splitlines(keepends=True)})
new_cells, mapping = [], []   # mapping: (new index, 'base i' | 'changed i' | 'inserted')
for i, c in enumerate(bc):
    c = dict(c)
    if i == 0:
        c["source"] = header.splitlines(keepends=True)
        kind = "changed"
    elif i == 1:
        c["source"] = cfg.splitlines(keepends=True)
        kind = "changed"
    elif i == 12:
        c["source"] = stage3.splitlines(keepends=True)
        kind = "changed"
    else:
        kind = "identical"
    new_cells.append(c)
    mapping.append((kind, i))
    if i == AFTER:
        new_cells.append(mk("markdown", STAGE_MD))
        mapping.append(("inserted", None))
        new_cells.append(mk("code", STAGE_CODE))
        mapping.append(("inserted", None))
assert len(new_cells) == len(bc) + 2
for (kind, i), c in zip(mapping, new_cells):
    if kind == "identical":
        assert c == bc[i] and src(c) == src(bc[i]), i   # whole cell dict, so type, metadata and outputs too
assert [src(c) for (k, i), c in zip(mapping, new_cells) if k == "identical"] == [src(bc[i]) for i in range(23) if i not in (0, 1, 12)]
nb = {**base_nb, "cells": new_cells}
out = REPO / "notebooks/v55-submit.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"v55 built from {BASE}, S6 stage after base cell {AFTER}; {len(new_cells)} cells")
for j, ((kind, i), c) in enumerate(zip(mapping, new_cells)):
    if kind != "identical":
        what = "" if kind == "inserted" else f" (base cell {i})"
        print(f"  cell {j:2d}: {kind}{what}: {c['cell_type']}, {len(src(c))} chars, first line: {src(c).splitlines()[0][:100]!r}")
