# Stage 4 [r6]: run the R6 asset cell of v62 (written above to /tmp/v63_r6_setup.py) in its own namespace, then v62's controller
# call for R6 in its own process group. Every exception or skip leaves R6_OK False; stage 5 then keeps v61's submission.csv.
# Writes only ours_r6_sub.csv, r6_submission_receipt.json and r6_worker*_log.txt to the working folder; no global, file or
# folder of the v61 stages is rebound or overwritten (the asset cell works in <temp>/probe_r6).
import json as _r6_json
import os as _r6_os
import shutil as _r6_shutil
import signal as _r6_signal
import subprocess as _r6_sp
import sys as _r6_sys
import time as _r6_time
from pathlib import Path as _R6Path

R6_CUTOFF_S = 8.65 * 3600   # notebook-elapsed (from V47_T0) hard cut-off of this stage (about 20 min to the 9 h limit); the final cell needs seconds
R6_COOP_MARGIN_S = 10 * 60  # the controller's own (cooperative) deadline is this much before the cut-off
R6_TIME_FACTOR = 1.3        # launch only if the time left >= this x the R7 controller time of this run (same worker, flip-TTA, studies)
R6_MIN_S = 20 * 60          # and at least this
R6_SETUP_FILE = '/tmp/v63_r6_setup.py'
R6_SETUP_SHA256 = '__R6_SETUP_SHA256__'   # v62 cell 7 with the temp folder renamed (asserted in the builder), trailing newlines stripped
R6_OK = False
R6_PRED = None
R6_STAGE = {'launched': False, 'skipped': None, 'killed': False, 'rc': None, 'error': None, 'seconds': None, 'setup_seconds': None,
            'r7_seconds': None, 'seconds_left_at_start': None}
_r6_work = _R6Path('/kaggle/working')
_r6_t0 = _r6_time.time()
_r6_pgid = None
try:
    _r6_left = V47_T0 + R6_CUTOFF_S - _r6_t0
    R6_STAGE['seconds_left_at_start'] = round(_r6_left)
    try:
        R6_STAGE['r7_seconds'] = float(_r6_json.loads((_r6_work / 'submission_receipt.json').read_text())['seconds'])
    except Exception as _exc:
        R6_STAGE['r7_seconds'] = None
        R6_STAGE['r7_seconds_error'] = repr(_exc)[:200]
    if R6_STAGE['r7_seconds'] is None or not (R6_STAGE['r7_seconds'] > 0):
        R6_STAGE['skipped'] = 'R7 controller time unknown'
    elif _r6_left < max(R6_MIN_S, R6_TIME_FACTOR * R6_STAGE['r7_seconds']):
        R6_STAGE['skipped'] = 'not enough time: %.0f s left, need %.0f s' % (_r6_left, max(R6_MIN_S, R6_TIME_FACTOR * R6_STAGE['r7_seconds']))
    else:
        import hashlib as _r6_hashlib
        _r6_src = _R6Path(R6_SETUP_FILE).read_bytes()
        assert _r6_hashlib.sha256(_r6_src.rstrip(b'\n')).hexdigest() == R6_SETUP_SHA256, 'R6 asset cell differs from the built one'
        assert isinstance(SOURCES, dict) and len(SOURCES) == 7, 'R7 asset cell SOURCES missing'   # cell 6's dict, shared (size limit)
        R6_NS = {'__name__': 'v63_r6_setup', 'NB_T0': NB_T0, 'R7_SOURCES': dict(SOURCES)}
        exec(compile(_r6_src.decode('utf-8'), R6_SETUP_FILE, 'exec'), R6_NS)
        assert R6_NS['BUNDLE_ID'] == 'fe055406fad6a12f' and R6_NS['manifest']['bundle_id'] == 'fe055406fad6a12f', 'not the R6 bundle'
        assert '--flip-tta' in R6_NS['WORKER_ARGS'], R6_NS['WORKER_ARGS']
        assert R6_NS['TMP'].name == 'probe_r6', R6_NS['TMP']
        R6_STAGE['setup_seconds'] = round(_r6_time.time() - _r6_t0, 1)
        R6_PRED = R6_NS['TMP'] / 'prediction'
        _r6_cut = V47_T0 + R6_CUTOFF_S
        _r6_env = dict(_r6_os.environ, PYTHONPATH=str(R6_NS['CODE']) + _r6_os.pathsep + _r6_os.environ.get('PYTHONPATH', ''),
                       PYTHONDONTWRITEBYTECODE='1')
        _r6_cmd = [_r6_sys.executable, '-u', str(R6_NS['SRC'] / 'probe_dual.py'), '--data', str(R6_NS['DATA']), '--split', 'test',
                   '--code', str(R6_NS['CODE']), '--bundle', str(R6_NS['BUNDLE']), '--arm', R6_NS['ARM'], '--output', str(R6_PRED),
                   '--amp', 'auto', '--loader-workers', '2', '--deadline', str(_r6_cut - R6_COOP_MARGIN_S),
                   '--worker', R6_NS['WORKER'], '--worker-args', _r6_json.dumps(R6_NS['WORKER_ARGS']),
                   '--max-fallback-fraction', '1.0']   # as v62's launch cell; the 3 % rule is applied in stage 5
        _r6_p = _r6_sp.Popen(_r6_cmd, env=_r6_env, start_new_session=True)
        _r6_pgid = _r6_p.pid
        R6_STAGE['launched'] = True
        try:
            _r6_p.wait(timeout=max(1.0, _r6_cut - _r6_time.time()))
        except _r6_sp.TimeoutExpired:
            R6_STAGE['killed'] = True
        R6_STAGE['rc'] = _r6_p.returncode
        for _log in sorted(R6_PRED.glob('worker*/log.txt')):
            _r6_shutil.copyfile(_log, _r6_work / ('r6_' + _log.parent.name + '_log.txt'))
        if R6_STAGE['rc'] == 0 and not R6_STAGE['killed']:
            _r6_shutil.copyfile(R6_PRED / 'submission.csv', _r6_work / 'ours_r6_sub.csv')
            _r6_rec = _r6_json.loads((R6_PRED / 'submission_receipt.json').read_text())
            _r6_rec['bundle_id'] = R6_NS['BUNDLE_ID']
            _r6_rec['arm'] = R6_NS['ARM']
            (_r6_work / 'r6_submission_receipt.json').write_text(_r6_json.dumps(_r6_rec, indent=1))
            R6_STAGE['receipt_status'] = _r6_rec.get('status')   # recorded only; coverage is checked in stage 5 (as v62/v61 do)
            R6_OK = True
        else:
            R6_STAGE['error'] = 'controller rc %r, killed %r' % (R6_STAGE['rc'], R6_STAGE['killed'])
except Exception as _exc:   # any setup or launch failure: v61's output stays
    R6_OK = False
    R6_STAGE['error'] = repr(_exc)[:400]
finally:
    if _r6_pgid is not None:
        try:
            _r6_os.killpg(_r6_pgid, _r6_signal.SIGKILL)   # leftover workers, on every exit path
        except Exception:
            pass
        try:
            _r6_p.wait(timeout=60)
        except Exception:
            pass
    R6_STAGE['seconds'] = round(_r6_time.time() - _r6_t0, 1)
print('R6_STAGE', 'ok' if R6_OK else 'not ok', _r6_json.dumps(R6_STAGE), flush=True)
