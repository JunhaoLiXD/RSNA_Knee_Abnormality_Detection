"""Build notebooks/v49-submit.ipynb (D-033 probe B): v47 cells unchanged + hengck23's public MaViT-288 as a fourth outer
component: final = rank(0.9 rank(v47) + 0.1 rank(MaViT)); rows MaViT could not score keep v47's rank; any stage failure
keeps v47's submission."""
import hashlib
import json
from pathlib import Path

REPO = Path("E:/Project/RSNA_Knee_Abnormality_Detection")
D = Path(__file__).parent
v47 = json.loads((REPO / "notebooks/v47-submit.ipynb").read_text(encoding="utf-8"))
src = lambda c: "".join(c["source"])
cfg47 = src(v47["cells"][1])
assert cfg47.startswith("# v47 configuration") and cfg47.count("VERSION = 'v47'") == 1
wrapper = (D / "mavit/v49_mavit.py").read_text(encoding="utf-8")
DS = REPO / "external/datasets/hengck23__hengck23-rnsa-knee"
SHA = {n: hashlib.sha256((DS / n).read_bytes()).hexdigest()
       for n in ("00000008.pth", "configure.py", "mavit.py", "model.py", "my_fastread_knee.py")}

header = """# v49 - v47 plus hengck23's public MaViT-288 as a fourth outer component at rank weight 0.10 (D-033 probe B)

Explicit ensemble version (D-017). Decision D-033 (`docs/research/silver-push-2026-10-14.md`): the reader rule that moved
v37 -> v40 (+211 rank-crossing witnesses, L33) and v46 -> v47 (+191, L37) applied to another public model family: hengck23's
MaViT-288 (a MALA linear-attention ViT encoder, six views x eight three-slice windows at 288 px; public 0.935 alone).
`final = rank(0.90 * rank(v47 output) + 0.10 * rank(MaViT))`, uniform over the 12 findings; a study MaViT could not read
keeps v47's rank; any stage failure, timeout or malformed output keeps v47's submission.

## Provenance

- v47 (cells 2-19 unchanged): heliosli's public R7 one-click notebook (Apache 2.0) + goodpjw2008's public reader at 0.10.
- MaViT: notebook https://www.kaggle.com/code/hengck23/mavit-288-baseline-01-1-5sec-study-1gpu (Apache 2.0), dataset
  `hengck23/hengck23-rnsa-knee` (MIT): checkpoint `00000008.pth`, `model.py`, `mavit.py`, `configure.py`,
  `my_fastread_knee.py` (his fast DICOM reader, modified from nartaa's). The encoder follows github.com/qhfan/MALA (ICCV 2025).
- Our wrapper `v49_mavit.py` runs his inference unchanged in substance (same reader settings, model, checkpoint, fp16, no
  TTA). Differences, on the failure paths only: the state-dict load must be exact (his notebook uses strict=False; locally
  all 341 tensors load), and a study that cannot be read gets NaN and is counted (his notebook writes zeros).

## Our changes

1. This cell and a v49 configuration cell (v47's settings, VERSION = 'v49', the MaViT settings).
2. After v47's final cell: the wrapper source (written inside the error handling, SHA-checked), a launch cell (own process
   group, notebook-elapsed deadline, dataset files hash-checked) and a blend cell (row fallback, NaN-fraction gate, the
   non-blended v47 output kept on any failure).

Judged against v47 by rank crossing (>= 20 stable witnesses, none reversed). Requirements: v47's inputs plus
`hengck23/hengck23-rnsa-knee`.
"""

cfg = cfg47.replace("# v47 configuration", "# v49 configuration (v47's settings, then the MaViT stage)", 1)
cfg = cfg.replace("VERSION = 'v47'", "VERSION = 'v49'", 1)
cfg = cfg.rstrip("\n") + f"""

# v49 additions (D-033 probe B)
MAVIT_W = 0.1                    # outer rank weight of MaViT, uniform over the 12 findings (the reader rule)
MAVIT_DEADLINE_S = 8.6 * 3600    # notebook-elapsed: MaViT is finished or killed by this time
MAVIT_MIN_S = 50 * 60            # launch allowance: 1.5 x 33 min (1.5 s per study x 1,300 studies, the author's figure)
MAVIT_MAX_NAN_FRACTION = 0.5     # MaViT is not used if more studies than this have no prediction
MAVIT_SHA = {json.dumps(SHA)}
"""
assert "import json" not in cfg47
cfg = cfg.replace("import time as _v47_time\n", "import json\nimport time as _v47_time\n", 1)

stage_md = """## v49: hengck23's MaViT-288 at outer weight 0.10

v47 has written `/kaggle/working/submission.csv`; it is saved as the base (`v49_base_submission.csv`, hash-checked). The
MaViT wrapper runs in its own process group under the deadline; the blend replaces `submission.csv` atomically only after
every check passes, so any failure leaves v47's output in place."""

sources = ("# v49 source: our wrapper of hengck23's inference, written inside the error handling of the next cell (SHA-checked).\n"
           + "_V49_WRAPPER = " + repr(wrapper) + "\n"
           + "_V49_WRAPPER_SHA = " + repr(hashlib.sha256(wrapper.encode("utf-8")).hexdigest()) + "\n")

launch = """# v49 launch: save the base, find and check hengck23's dataset, run the wrapper in its own process group under the deadline.
import hashlib as _v49_hashlib
import json as _v49_json
import os as _v49_os
import shutil as _v49_shutil
import signal as _v49_signal
import subprocess as _v49_sp
import sys as _v49_sys
import time as _v49_time
import traceback as _v49_tb
from pathlib import Path as _V49Path

_V49_WORK = _V49Path('/kaggle/working')
_V49_BASE = _V49_WORK / 'v49_base_submission.csv'
_V49_DIR = _V49_WORK / 'v49_mavit'
_v49_sha = lambda p: _v49_hashlib.sha256(_V49Path(p).read_bytes()).hexdigest() if _V49Path(p).is_file() else None
_v49 = {'launched': False, 'killed': False, 'exit_code': None, 'errors': []}
try:
    _v49['base_sha256'] = _v49_sha(_V49_WORK / 'submission.csv')
    _tmp = _V49_WORK / 'v49_base_submission.tmp'
    _v49_shutil.copy2(_V49_WORK / 'submission.csv', _tmp)
    assert _v49_sha(_tmp) == _v49['base_sha256'], 'base copy differs'
    _v49_os.replace(_tmp, _V49_BASE)
    _v49['base_saved'] = True
    (_V49_WORK / 'v49_mavit.py').write_bytes(_V49_WRAPPER.encode('utf-8'))
    assert _v49_sha(_V49_WORK / 'v49_mavit.py') == _V49_WRAPPER_SHA, 'wrapper written incorrectly'
    _v49_comp = next(p for p in (_V49Path('/kaggle/input/competitions/rsna-knee-abnormality-detection'),
                                 _V49Path('/kaggle/input/rsna-knee-abnormality-detection'))
                     if (p / 'test.csv').is_file())
    _hits = []
    for _cur, _dirs, _files in _v49_os.walk('/kaggle/input'):
        _dirs[:] = [d for d in _dirs if d not in ('train_series', 'test_series', 'competitions')
                    and 'rsna-knee-abnormality-detection' not in d]
        if '00000008.pth' in _files and 'my_fastread_knee.py' in _files:
            _hits.append(_V49Path(_cur))
    assert len(_hits) == 1, [str(h) for h in _hits]
    _V49_SRC = _hits[0]
    _bad = {n: _v49_sha(_V49_SRC / n) for n, h in MAVIT_SHA.items() if _v49_sha(_V49_SRC / n) != h}
    assert not _bad, f'MaViT dataset files differ: {_bad}'
    _left = MAVIT_DEADLINE_S - (_v47_time.time() - V47_T0)
    _v49['seconds_left'] = round(_left)
    assert _left >= MAVIT_MIN_S, f'only {_left / 60:.0f} min left before the MaViT deadline'
    _V49_DIR.mkdir(exist_ok=True)
    _args = {'src': str(_V49_SRC), 'data_dir': str(_v49_comp), 'out_csv': str(_V49_DIR / 'mavit.csv'),
             'receipt': str(_V49_DIR / 'mavit_receipt.json')}
    _env = {**_v49_os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'CUDA_VISIBLE_DEVICES': '0'}
    _logf = open(_V49_WORK / 'v49_mavit_log.txt', 'w')
    _p = _v49_sp.Popen([_v49_sys.executable, '-u', str(_V49_WORK / 'v49_mavit.py'), _v49_json.dumps(_args)], cwd=str(_V49_DIR),
                       env=_env, stdout=_logf, stderr=_v49_sp.STDOUT, start_new_session=True)
    _v49['launched'] = True
    _t = _v49_time.time()
    try:
        _p.wait(timeout=max(1.0, V47_T0 + MAVIT_DEADLINE_S - _v47_time.time()))
    except _v49_sp.TimeoutExpired:
        _v49['killed'] = True
    finally:
        try:
            _v49_os.killpg(_p.pid, _v49_signal.SIGKILL)   # leftover reader threads or workers, on every exit path
        except Exception:
            pass
        try:
            _p.wait(timeout=60)
        except Exception:
            pass
        _logf.close()
    _v49.update(exit_code=_p.returncode, seconds=round(_v49_time.time() - _t, 1))
except Exception as _exc:
    _v49['errors'].append(repr(_exc)[:300] + ' | ' + _v49_tb.format_exc().splitlines()[-2][:200])
try:
    print(''.join(open(_V49_WORK / 'v49_mavit_log.txt', errors='replace').readlines()[-6:]), flush=True)
except Exception:
    pass
print('V49_STAGE', _v49_json.dumps(_v49, default=str), flush=True)
"""

blend = """# v49 blend: final = rank(0.9 rank(v47) + 0.1 rank(MaViT)) per finding; MaViT ranks over its scored studies only, a study it
# did not score keeps v47's rank; submission.csv is replaced atomically only after every check (otherwise it stays v47's).
import numpy as _v49_np
import pandas as _v49_pd

_v49['blend'] = {'used_mavit': False, 'fallback': None}
try:
    assert not _v49['errors'], 'stage error'
    assert _v49['launched'] and not _v49['killed'] and _v49['exit_code'] == 0, 'MaViT did not finish'
    assert _v49.get('base_saved') and _v49_sha(_V49_WORK / 'submission.csv') == _v49['base_sha256'], 'base changed or not saved'
    _rec = _v49_json.loads((_V49_DIR / 'mavit_receipt.json').read_text())
    _v49['blend']['mavit_receipt'] = {k: _rec.get(k) for k in ('status', 'studies', 'failed_studies', 'studies_without_view',
                                                                'nan_rows', 'failed_by_type', 'seconds', 'missing_keys',
                                                                'unexpected_keys')}
    assert _rec.get('status') == 'done' and not _rec.get('missing_keys') and not _rec.get('unexpected_keys'), 'receipt'
    _labels = _v49_pd.read_csv(_v49_comp / 'sample_submission.csv', nrows=0).columns.tolist()
    _ids = _v49_pd.read_csv(_v49_comp / 'test.csv', dtype={'StudyInstanceUID': str}).StudyInstanceUID.tolist()
    _base_s = _v49_pd.read_csv(_V49_BASE, dtype=str)
    assert _base_s.columns.tolist() == _labels and _base_s.StudyInstanceUID.tolist() == _ids, 'base format'
    _base = _v49_pd.read_csv(_V49_BASE, dtype={'StudyInstanceUID': str}, float_precision='round_trip').set_index('StudyInstanceUID')
    _m = _v49_pd.read_csv(_V49_DIR / 'mavit.csv', dtype={'StudyInstanceUID': str}).set_index('StudyInstanceUID')
    assert _m.columns.tolist() == _labels[1:] and _m.index.is_unique and set(_m.index) == set(_ids), 'MaViT output format'
    _m = _m.loc[_ids, _labels[1:]].astype(float)
    _ok = _v49_np.isfinite(_m.to_numpy()).all(1)
    _nan_frac = 1.0 - float(_ok.mean())
    _v49['blend']['nan_fraction'] = round(_nan_frac, 4)
    assert _nan_frac <= MAVIT_MAX_NAN_FRACTION, f'MaViT scored too few studies ({_nan_frac:.2%} without a prediction)'
    assert len(_ids) < 2 or (_m[_ok].nunique() > 1).all(), 'constant MaViT column'
    _bpct = _base.loc[_ids, _labels[1:]].rank(pct=True)
    _mpct = _bpct.copy()
    _mpct.loc[_ok] = _m.loc[_ok].rank(pct=True).to_numpy()   # MaViT's ranks over its scored studies; the others keep v47's
    _final = ((1.0 - MAVIT_W) * _bpct + MAVIT_W * _mpct).rank(pct=True)
    if _ok.sum() > 2:
        _v49['blend']['mean_spearman_base_vs_mavit'] = float(_v49_np.mean([
            _bpct.loc[_ok, c].corr(_m.loc[_ok, c], method='spearman') for c in _labels[1:]]))
    _sub = _final.reset_index()[_labels]
    assert _sub.StudyInstanceUID.tolist() == _ids and _v49_np.isfinite(_sub[_labels[1:]].to_numpy(float)).all()
    _tmpf = _V49_WORK / 'v49_submission.tmp.csv'
    _sub.to_csv(_tmpf, index=False)
    _v49_os.replace(_tmpf, _V49_WORK / 'submission.csv')
    _v49['blend']['used_mavit'] = True
except Exception as _exc:
    _v49['blend']['fallback'] = repr(_exc)[:300]   # submission.csv is still v47's
    print('V49_FALLBACK', _v49['blend']['fallback'], flush=True)
try:   # diagnostics only
    _v49_shutil.copy2(_V49_WORK / 'submission.csv', _V49_WORK / 'v49_submission.csv')
    _v49.update(submission_sha256=_v49_sha(_V49_WORK / 'submission.csv'),
                elapsed_hours=round((_v47_time.time() - V47_T0) / 3600, 3))
    (_V49_WORK / 'v49_receipt.json').write_text(_v49_json.dumps(_v49, indent=2, default=str))
    print(_v49_json.dumps(_v49['blend'], indent=2, default=str), flush=True)
except Exception as _exc:
    print('v49 receipt failed:', repr(_exc)[:200], flush=True)
"""


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.splitlines(keepends=True)}


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)}


host = [dict(c) for c in v47["cells"][2:]]
cells = [md(header), code(cfg)] + host + [md(stage_md), code(sources), code(launch), code(blend)]
assert [src(c) for c in cells[2:2 + len(host)]] == [src(c) for c in v47["cells"][2:]]
nb = {**v47, "cells": cells}
(REPO / "notebooks/v49-submit.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("v49 cells", len(cells), "| sha", {k: v[:12] for k, v in SHA.items()})
