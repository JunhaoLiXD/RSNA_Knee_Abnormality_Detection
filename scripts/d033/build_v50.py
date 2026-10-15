"""Build notebooks/v50-submit.ipynb = notebooks/v47-submit.ipynb + exactly the R224 addition.

Inputs (read only):
  notebooks/v47-submit.ipynb                                                  base
  external/kernels/varshithakolupuri__rsna-knee-one-unused-checkpoint-lifts-the-0-956_20261013/*.ipynb   R224 recipe
  external/kernels/heliosli__0-957-latest-dataset-score-in-one-click_20261013/*.ipynb                    R7 base of that recipe
Output:
  notebooks/v50-submit.ipynb

Every v47 cell that is not listed as changed is asserted byte-identical (cell JSON). The file format
(indent 1, CRLF, ensure_ascii False) is the one v47 uses; the script asserts that v47 round-trips with it.
"""
import copy
import difflib
import json
import pathlib

ROOT = pathlib.Path('E:/Project/RSNA_Knee_Abnormality_Detection')
V47 = ROOT / 'notebooks' / 'v47-submit.ipynb'
OUT = ROOT / 'notebooks' / 'v50-submit.ipynb'
VARSH = next((ROOT / 'external/kernels/varshithakolupuri__rsna-knee-one-unused-checkpoint-lifts-the-0-956_20261013').glob('*.ipynb'))
HELIOS = next((ROOT / 'external/kernels/heliosli__0-957-latest-dataset-score-in-one-click_20261013').glob('*.ipynb'))

R224_SHA = '3394fdd7e668286956e85af2554bef0386df5cd79d1c1af223b095c828b815d6'
R224_FILE = 'raptor_ft_alldata_t16_blendjev_oai_d96_c08_r224_swa.pt'


def dump(nb):
    return (json.dumps(nb, indent=1, ensure_ascii=False) + '\n').replace('\n', '\r\n').encode('utf-8')


def src(cell):
    s = cell['source']
    return s if isinstance(s, str) else ''.join(s)


def canon(cell):
    return json.dumps(cell, sort_keys=True, ensure_ascii=False)


def rep(text, old, new, count=1):
    assert text.count(old) == count, (text.count(old), old[:80])
    return text.replace(old, new)


def lines(text):
    return text.splitlines(keepends=True)


def code_cell(text):
    return {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': lines(text)}


def md_cell(text):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': lines(text)}


# ----------------------------------------------------------------------------------------------------------------------
# load
raw47 = V47.read_bytes()
v47 = json.loads(raw47.decode('utf-8'))
assert dump(v47) == raw47, 'v47 does not round-trip with the writer used here'
varsh = json.loads(VARSH.read_text(encoding='utf-8'))
helios = json.loads(HELIOS.read_text(encoding='utf-8'))
c47 = v47['cells']
cv = varsh['cells']
ch = helios['cells']
assert len(c47) == 19 and len(cv) == 13 and len(ch) == 7

# ----------------------------------------------------------------------------------------------------------------------
# 1. what varshitha's recipe changes relative to the R7 notebook it is built on (checked, not assumed)
#    helios cell -> varsh cell: 2->3 (raptor writefile), 3->4 (stage 1), 4->6 (R7 compute), 5->7 (R7 launch), 6->12 (stage 3)
for hi, vi in ((2, 3), (3, 4), (4, 6), (5, 7)):
    assert src(ch[hi]) == src(cv[vi]), ('helios', hi, 'varsh', vi)
# v47's author cells (v47 2, 4..8) are helios 0, 2..6
for hi, xi in ((0, 2), (2, 4), (3, 5), (4, 6), (5, 7), (6, 8)):
    assert src(ch[hi]) == src(c47[xi]), ('helios', hi, 'v47', xi)
# the credits cell of v47 differs from helios' only by the repaired separator character (v46 provenance); varsh adds a paragraph
assert src(ch[1]).replace(chr(0x8def), chr(0xb7)) == src(c47[3])
# the stage-3 cell: varsh = helios + two hunks (the A224 block and the rank-mix lines), nothing else
V_BLOCK = src(cv[12])
H_BLOCK = src(ch[6])
v_hunk1 = V_BLOCK[V_BLOCK.index("A224 = 0.35"):V_BLOCK.index("n = len(test_ids)\n")]
v_hunk2 = ("    if r224 is not None:   # [s5] mix the 224 model into the Raptor slot, over Raptor's non-failed rows\n"
           "        rr = (1.0 - A224) * rr + A224 * pct_on(r224[c].values, ~rap_fail)\n")
assert rep(rep(V_BLOCK, v_hunk1, ''), v_hunk2, '') == H_BLOCK, 'varshitha stage 3 differs from helios by more than the two R224 hunks'
# the added cells of varshitha: 8 (md), 9 (raptor224 writefile), 10 (stage 2b launch), 11 (md)
assert [cv[i]['cell_type'] for i in (8, 9, 10, 11)] == ['markdown', 'code', 'code', 'markdown']
assert src(cv[9]).startswith('%%writefile /tmp/raptor224_run.py\n')
# position: after the R7 launch cell (varsh 7) and before the stage 3 cell (varsh 12); in v47 that is between cells 7 and 8
assert src(cv[7]) == src(c47[7]) and V_BLOCK.startswith('# Stage 3') and src(c47[8]).startswith('# Stage 3')

# ----------------------------------------------------------------------------------------------------------------------
# 2. the R224 scoring source = varshitha's cell 9 + two additions (raw dump for the failure mask, load-time sha256 assertion)
r224_src = src(cv[9])
assert R224_FILE in r224_src and R224_SHA in r224_src
assert "/kaggle/input/rsna-knee-publication-swa-weights-20261007') / _weight_name" in r224_src          # candidate 1: v47's dataset
assert "/kaggle/input/datasets/nartaa/rsna-knee-publication-swa-weights-20261007') / _weight_name" in r224_src   # candidate 2
assert '\r' not in r224_src

# (a) load-time sha256 assertion, the same lines the 384 script has (the header only checks the first candidate path)
r224_src = rep(
    r224_src,
    "def load_model(pt_path, arch_default, res_default, device, ngpu=1):\n"
    "    ck = torch.load(pt_path, map_location=\"cpu\", weights_only=False)\n",
    "def load_model(pt_path, arch_default, res_default, device, ngpu=1):\n"
    "    import hashlib   # [r224] bind the loaded bytes to the pinned hash, as the 384 script does\n"
    "    with open(pt_path, \"rb\") as stream:\n"
    "        observed_sha = hashlib.file_digest(stream, \"sha256\").hexdigest()\n"
    f"    assert observed_sha == '{R224_SHA}', \"Bound checkpoint bytes differ\"\n"
    "    print(f\"[weights] sha256 {observed_sha}\", flush=True)\n"
    "    ck = torch.load(pt_path, map_location=\"cpu\", weights_only=False)\n")
# (b) raw probability dump, the same lines the 384 script has: a study the model failed on stays 0.5 in every column
r224_src = rep(
    r224_src,
    "    print(f\"[gpu] done: {done_n[0]}/{N} studies on {len(devs)} device(s) | {time.time()-t0:.0f}s\", flush=True)\n"
    "    for d in devs:\n",
    "    print(f\"[gpu] done: {done_n[0]}/{N} studies on {len(devs)} device(s) | {time.time()-t0:.0f}s\", flush=True)\n"
    "    _raw = pd.DataFrame(arm_probs[0].astype(np.float32), columns=LAB)   # [r224] raw probabilities; a failed study stays 0.5 in every column\n"
    "    _raw.insert(0, \"StudyInstanceUID\", test_ids)\n"
    "    _raw.to_csv(\"/kaggle/working/raptor224_raw.csv\", index=False)\n"
    "    for d in devs:\n")
assert r224_src.count('raptor224_raw.csv') == 1 and r224_src.count('observed_sha') == 3
# (c) Codex review 2026-10-14: a study whose preprocessing failed arrives as a zero volume with an empty mask; the scoring
# source would still run the model on it, so the prediction escaped the 0.5 failure sentinel. Skip it instead.
_OLD_C = ("            sid, vol, mask = item; i = pos[sid]\n"
          "            try:\n"
          "                for a, (model, res) in enumerate(models[d]):\n")
_NEW_C = ("            sid, vol, mask = item; i = pos[sid]\n"
          "            try:\n"
          "                if not np.asarray(mask).any():   # [r224] preprocessing failed: keep the 0.5 sentinel, no inference on zeros\n"
          "                    raise RuntimeError('no readable slice')\n"
          "                for a, (model, res) in enumerate(models[d]):\n")
r224_src = rep(r224_src, _OLD_C, _NEW_C)

# ----------------------------------------------------------------------------------------------------------------------
# 3. stage 2b launch cell (own process group, absolute clock that keeps the outer reader launchable, never raises)
launch_src = '''# Stage 2b [r224]: nartaa's 224-pixel, 0.8-crop CoAtNet (public, 0.945 alone; second checkpoint of the Raptor weights dataset).
# Runs only if the absolute clock leaves the outer reader its launch allowance afterwards. Any failure, timeout or skip leaves
# R224_OK False and therefore stage 3 exactly as in v47; stage 3 validates the two output files again before using them.
import os, signal, subprocess, sys, time
R224_OK = False
R224_STAGE = {'launched': False, 'skipped': None, 'rc': None, 'killed': False, 'error': None, 'seconds': None}
R224_MIN_S = 20 * 60           # not started with less than this left before the cut-off below
R224_MAX_S = 2.5 * 3600        # hard cap of the stage
R224_MARGIN_S = 15 * 60        # slack kept between the cut-off and the reader's launch allowance
R224_FILES = ('raptor224_sub.csv', 'raptor224_raw.csv')
try:
    for _r224_f in R224_FILES:   # no stale file can be mistaken for this run's output
        if os.path.isfile('/kaggle/working/' + _r224_f):
            os.remove('/kaggle/working/' + _r224_f)
    # the stage must end early enough that the outer reader (cell "Launch the reader") still gets READER_MIN_S before its deadline
    _r224_end = V47_T0 + READER_DEADLINE_S - READER_MIN_S - R224_MARGIN_S
    _r224_left = _r224_end - time.time()
    if _r224_left < R224_MIN_S:
        R224_STAGE['skipped'] = 'only %.0f min left' % (_r224_left / 60)
        print('R224_SKIPPED', R224_STAGE['skipped'], flush=True)
    else:
        _r224_t0 = time.time()
        _r224_p = subprocess.Popen([sys.executable, '-u', '/tmp/raptor224_run.py'], start_new_session=True)   # own process group
        R224_STAGE['launched'] = True
        try:
            R224_STAGE['rc'] = _r224_p.wait(timeout=min(_r224_left, R224_MAX_S))
        except subprocess.TimeoutExpired:
            R224_STAGE['killed'] = True
        finally:
            try:
                os.killpg(_r224_p.pid, signal.SIGKILL)   # leftover prefetch workers, on every exit path
            except Exception:
                try:
                    _r224_p.kill()   # no process group to signal: at least the scoring process itself
                except Exception:
                    pass
            try:
                _r224_p.wait(timeout=60)
            except Exception:
                pass
        R224_STAGE['seconds'] = round(time.time() - _r224_t0, 1)
        R224_OK = (R224_STAGE['rc'] == 0 and not R224_STAGE['killed']
                   and all(os.path.isfile('/kaggle/working/' + _r224_f) for _r224_f in R224_FILES))
        print('R224_STAGE', R224_STAGE, 'ok=%s' % R224_OK, flush=True)
except Exception as _r224_exc:   # never stop the notebook: stage 3 then blends without R224
    R224_OK = False
    R224_STAGE['error'] = repr(_r224_exc)[:300]
    print('R224_STAGE_ERROR', R224_STAGE['error'], flush=True)
'''

# ----------------------------------------------------------------------------------------------------------------------
# 4. stage 3 blend cell = v47's cell 8 + the R224 block (own failure mask) + the mix lines + a receipt key
blend47 = src(c47[8])
BLOCK_A = '''A224 = 0.35   # [r224] share of the Raptor slot given to the 224-crop model (public recipe); fixed before any run
R224_MIN_SPEARMAN = 0.5   # [r224] sanity floor, mean per-finding Spearman of R224 against the 384 model (checked from 50 studies on)
r224, r224_fail = None, np.zeros(len(test_ids), dtype=bool)
r224_info = {'weight': A224, 'stage': dict(globals().get('R224_STAGE') or {}), 'used': False, 'failed': None, 'reason': None}
if globals().get('R224_OK', False):
    try:
        import hashlib
        r224_info['output_sha256'] = {f: hashlib.sha256((WORK / f).read_bytes()).hexdigest() for f in ('raptor224_sub.csv', 'raptor224_raw.csv')}
        _s224 = pd.read_csv(WORK / 'raptor224_sub.csv', dtype={'StudyInstanceUID': str})
        _w224 = pd.read_csv(WORK / 'raptor224_raw.csv', dtype={'StudyInstanceUID': str})
        for _df, _nm in ((_s224, 'raptor224_sub'), (_w224, 'raptor224_raw')):
            assert sorted(_df['StudyInstanceUID']) == sorted(test_ids) and set(labels) <= set(_df.columns), _nm + ': rows or columns differ from test.csv'
        _s224 = _s224.set_index('StudyInstanceUID').loc[test_ids, labels]
        _w224 = _w224.set_index('StudyInstanceUID').loc[test_ids, labels]
        assert np.isfinite(_s224.values).all() and np.isfinite(_w224.values).all(), 'non-finite R224 output'
        assert ((_w224.values >= 0) & (_w224.values <= 1)).all(), 'R224 raw probabilities outside [0, 1]'
        _f224 = (_w224.values == 0.5).all(axis=1)          # R224 leaves a study it failed on at 0.5 in every column of its raw dump
        if _f224.sum() > 0.03 * len(test_ids):
            raise RuntimeError('R224 failed on %d of %d studies' % (_f224.sum(), len(test_ids)))
        _ok224 = ~_f224 & ~(raw.values == 0.5).all(axis=1)   # studies both Raptor models scored
        assert _ok224.any(), 'no study scored by both Raptor models'
        if _ok224.sum() >= 3:   # the rank file must be the rank of the raw dump, as for the 384 model
            _rho = np.array([pd.Series(_w224[c].values[~_f224]).corr(pd.Series(_s224[c].values[~_f224]), method='spearman') for c in labels])
            assert np.isfinite(_rho).all() and _rho.min() >= 0.99, 'R224 raw dump does not match its own submission ranks: %s' % np.round(_rho, 4)
        if _ok224.sum() >= 50:
            _rho = np.array([pd.Series(_w224[c].values[_ok224]).corr(pd.Series(raw[c].values[_ok224]), method='spearman') for c in labels])
            r224_info['spearman_vs_r384'] = {'mean': round(float(np.nanmean(_rho)), 4), 'min': round(float(np.nanmin(_rho)), 4)}
            assert np.isfinite(_rho).all() and _rho.mean() >= R224_MIN_SPEARMAN, 'R224 does not agree with the 384 model: %s' % np.round(_rho, 3)
        r224, r224_fail = _s224, _f224
        r224_info.update(used=True, failed=int(_f224.sum()))
    except Exception as _e:   # missing, truncated or implausible R224 output: the blend is exactly v47's
        print('R224_UNUSABLE', repr(_e), flush=True)
        r224, r224_fail = None, np.zeros(len(test_ids), dtype=bool)
        r224_info['reason'] = repr(_e)[:300]
else:
    r224_info['reason'] = 'R224 stage not ok or not run'
'''
BLOCK_A_ANCHOR = "rsub = rsub.set_index('StudyInstanceUID').loc[test_ids, labels]\nn = len(test_ids)\n"
blend50 = rep(blend47, BLOCK_A_ANCHOR,
              "rsub = rsub.set_index('StudyInstanceUID').loc[test_ids, labels]\n" + BLOCK_A + "n = len(test_ids)\n")
MIX_ANCHOR = ("    rr, ro = pct_on(raw[c].values, ~rap_fail), pct_on(ours[c].values, ~our_fail)   # [v3] each over its own non-failed rows\n"
              "    wr = W_RAPTOR_C.get(c, W_RAPTOR)\n")
blend50 = rep(blend50, MIX_ANCHOR,
              "    rr, ro = pct_on(raw[c].values, ~rap_fail), pct_on(ours[c].values, ~our_fail)   # [v3] each over its own non-failed rows\n"
              "    if r224 is not None:   # [r224] 0.65 x rank(384) + 0.35 x rank(224) over the studies both models scored; a study R224 failed on keeps rank(384)\n"
              "        _x224 = pct_on(r224[c].values, ~rap_fail & ~r224_fail)\n"
              "        rr = np.where(np.isnan(_x224), rr, (1.0 - A224) * rr + A224 * _x224)\n"
              "    wr = W_RAPTOR_C.get(c, W_RAPTOR)\n")
blend50 = rep(blend50, "         'rank_basis': 'each model over its own non-failed rows'}\n",
              "         'rank_basis': 'each model over its own non-failed rows', 'r224': r224_info}   # [r224] used / failed studies / reason\n")

# ----------------------------------------------------------------------------------------------------------------------
# 5. configuration cell: title, VERSION and the log line only
cfg47 = src(c47[1])
cfg50 = rep(cfg47, '# v47 configuration\n', '# v50 configuration\n')
cfg50 = rep(cfg50, "VERSION = 'v47'\n", "VERSION = 'v50'\n")
cfg50 = rep(cfg50, "reader deadline {READER_DEADLINE_S / 3600:.1f} h', flush=True)",
            "reader deadline {READER_DEADLINE_S / 3600:.1f} h, R224 in the Raptor slot', flush=True)")

# ----------------------------------------------------------------------------------------------------------------------
# 6. markdown cells
header = '''# v50 - v47 plus nartaa's 224-px CoAtNet in the Raptor slot (D-033 probe C)

Explicit ensemble version (D-017). Decision D-033, probe C: v47's Raptor slot (nartaa's 384-px CoAtNet, 320-px input with mirror
TTA) becomes `0.65 * rank(R384) + 0.35 * rank(R224)` per finding, where R224 is the second checkpoint of the same weights dataset
(224 px from a 0.8 centre crop, one view, public 0.945 alone). Everything after the Raptor slot is v47: heliosli's R7 stage, the
per-finding rank blend (Raptor 0.5, R7 0.5, so R224 carries 0.175 of it) and the outer goodpjw2008 reader at 0.10. No weight is
fitted on any label or on the public board. Judged against v47 by rank crossing (D-022, D-033); adopted only if it wins.

Failure policy: R224 runs in its own process group under an absolute clock that leaves the outer reader its launch allowance. A
failed, killed, skipped or unusable R224 run (files missing or malformed, non-finite values, more than 3 % failed studies,
implausible agreement with the 384 model) leaves stage 3, and therefore the submission, exactly as in v47. R224 has its own
per-study failure mask (raw dump `raptor224_raw.csv`, 0.5 in every column marks a failed study): a study R224 failed on keeps the
384 rank in the Raptor slot.

## Provenance

- R224 recipe: https://www.kaggle.com/code/varshithakolupuri/rsna-knee-one-unused-checkpoint-lifts-the-0-956 (pulled 2026-10-13;
  kernel version and licence are not recorded in the pulled copy). It adds nartaa's 224-px inference script (stated there to be
  from https://www.kaggle.com/code/nartaa/rsna-knee-0945-efficient-224crop; not compared by us) and a blend change to heliosli's R7
  notebook. Our copy of both differs from it as listed below.
- R224 weights: `raptor_ft_alldata_t16_blendjev_oai_d96_c08_r224_swa.pt` (sha256 `3394fdd7e668286956e85af2554bef0386df5cd79d1c1af223b095c828b815d6`)
  from `nartaa/rsna-knee-publication-swa-weights-20261007`, the dataset v47 already attaches (its checkpoint-manifest.json lists
  the file as the 0.945 "efficiency" model). Same OAI-trained family as the 384 model (D-019).
- Anchor: as `notebooks/v47-submit.ipynb` (v46 = heliosli/0-957-latest-dataset-score-in-one-click version 1, Apache 2.0: nartaa's
  OAI CoAtNet-384 + heliosli's R7 ConvNeXt-small bundle `8c7b666e27dc0e8f`; plus the public goodpjw2008 reader of
  `goodpjw2008/rsna-knee-2-5d-convnext-reader`, Apache 2.0, at outer weight 0.10, D-032); its cells are unchanged except as below.

## Our changes

Relative to v47 (everything else is byte-identical):
1. This header; the configuration cell (title, `VERSION = 'v50'`, one log line).
2. Three cells before stage 3: a markdown header, the R224 scoring source (`/tmp/raptor224_run.py`), and the stage 2b launch.
3. The stage 3 blend cell: the R224 block, the rank-mix lines and one receipt key.

Relative to varshitha's notebook: (a) R224 writes a raw probability dump (`raptor224_raw.csv`, the same lines the 384 script has),
which gives R224 its own per-study failure mask (the original reuses the 384 mask and cannot see an R224 failure); (b) the R224
script asserts the pinned sha256 again when it loads the checkpoint (the original checks only the file its header finds, while the
loader searches /kaggle/input by itself);
(c) the stage runs in its own process group under an absolute clock tied to the reader's deadline (the original uses a 9-hour
clock from the Raptor start); (d) the R224 output is validated again in stage 3 (format, finite values, failed-study fraction,
rank file against raw dump, agreement with the 384 model); (e) the ranks of R224 are taken over the studies both models scored.

Requirements: GPU T4 x2, internet off; the same three datasets as v46 plus `goodpjw2008/rsna-knee-2-5d-convnext-reader`
(no new dataset).
'''
stage2b_md = '''## Stage 2b: nartaa's 224-pixel CoAtNet (the addition)

`/tmp/raptor224_run.py` is the 224-px, 0.8-centre-crop scoring script of varshitha's notebook with the second checkpoint of the
Raptor weights dataset (sha256 asserted twice: file header and checkpoint load). It writes `raptor224_sub.csv` (rank file) and
`raptor224_raw.csv` (raw probabilities, the failure mask); the blend cell writes `submission.csv`. The launch cell never raises.
'''

# ----------------------------------------------------------------------------------------------------------------------
# 7. assemble
new = []
new.append(md_cell(header))                                    # 0  (replaces v47 header)
c1 = copy.deepcopy(c47[1]); c1['source'] = lines(cfg50)
new.append(c1)                                                 # 1  config (changed)
for i in range(2, 8):                                          # 2..7 v47 cells 2..7 unchanged
    new.append(copy.deepcopy(c47[i]))
new.append(md_cell(stage2b_md))                                # 8  new
new.append(code_cell(r224_src))                                # 9  new
new.append(code_cell(launch_src))                              # 10 new
c8 = copy.deepcopy(c47[8]); c8['source'] = lines(blend50)
new.append(c8)                                                 # 11 blend (changed)
for i in range(9, 19):                                         # 12..21 v47 cells 9..18 unchanged
    new.append(copy.deepcopy(c47[i]))
assert len(new) == 22

nb = copy.deepcopy(v47)
nb['cells'] = new

# untouched cells: byte-identical to v47
untouched = {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
untouched.update({12 + k: 9 + k for k in range(10)})
for ni, oi in untouched.items():
    assert canon(new[ni]) == canon(c47[oi]), (ni, oi)
    assert dump({'x': new[ni]}) == dump({'x': c47[oi]})
# changed cells: only the intended differences
assert src(new[1]) != src(c47[1]) and src(new[11]) != src(c47[8])
for key in nb:
    if key != 'cells':
        assert nb[key] == v47[key]
for c in new:
    if c['cell_type'] == 'code':
        assert c['outputs'] == [] and c['execution_count'] is None
    for k in ('id',):
        assert k not in c

OUT.write_bytes(dump(nb))

# ----------------------------------------------------------------------------------------------------------------------
# 8. re-read and re-verify, then summarise
chk = json.loads(OUT.read_bytes().decode('utf-8'))
assert dump(chk) == OUT.read_bytes()
for ni, oi in untouched.items():
    assert canon(chk['cells'][ni]) == canon(c47[oi])
print('wrote', OUT, len(chk['cells']), 'cells;', len(untouched), 'v47 cells verified byte-identical')
print('summary of changed or new cells (index in v50 | origin | what):')
print('  0  | v47 cell 0 replaced | v50 header (title, purpose, failure policy, provenance, changes)')
print('  1  | v47 cell 1 changed  | title line, VERSION, one log line')
print('  8  | new                 | stage 2b markdown')
print('  9  | new                 | %%writefile /tmp/raptor224_run.py (varshitha cell 9 + raw dump + load-time sha256)')
print('  10 | new                 | stage 2b launch (own process group, absolute clock, never raises)')
print('  11 | v47 cell 8 changed  | R224 block (+validation, own failure mask), rank mix, receipt key')
for name, a, b in (('cfg (cell 1)', cfg47, cfg50), ('blend (cell 11)', blend47, blend50)):
    d = [l for l in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm='', n=0) if l[:1] in '+-' and l[:3] not in ('+++', '---')]
    print('  %s: +%d / -%d lines' % (name, sum(l[0] == '+' for l in d), sum(l[0] == '-' for l in d)))
print('r224 script vs varshitha cell 9: +%d lines' % (len(r224_src.splitlines()) - len(src(cv[9]).splitlines())))
