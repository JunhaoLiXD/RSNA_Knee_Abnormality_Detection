"""Run arm-N folds of v13 or a notebook derived from it (v22) on the local GPU (decision D-016).

The notebook stays the only source of truth: its code cells are executed here with the Kaggle
paths mapped to a local input tree and working directory. Differences to the Kaggle run: one GPU
(one fold per invocation), no GPU quota (the notebook's budget logic sees an 11 h session), and
the data-loader worker count.

Run in the conda env `kaggle-gpu` (environment-gpu.yml):
  python scripts/local_v13.py prepare            # input tree + checks of the v07 cache download
  python scripts/local_v13.py check              # re-infer the Kaggle fold-0 N checkpoint locally
  python scripts/local_v13.py fold 1 --workers 6 # train v13 arm N on fold 1 (watchdog: --stall-min 15)
  python scripts/local_v13.py --version v22 fold 0   # v22 (target T3) arm N on fold 0
  python scripts/local_v13.py --version v24 fold 0 --arm C --mode smoke   # v24 arm C smoke check
  python scripts/local_v13.py --version v24 fold 0 --arm C                # v24 arm C on fold 0

Before anything is trained the training targets are checked: v13's and v24's must equal those of the
Kaggle v13 F0 run; v22's must equal T3 recomputed here independently from the inputs. The peak Windows
commit charge is recorded (L19).
"""
import argparse
import hashlib
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
NOTEBOOKS = {'v13': 'v13-round2-mri.ipynb', 'v22': 'v22-n-gemini-target.ipynb', 'v24': 'v24-coatnet-own.ipynb'}
KAGGLE_F0_TARGETS = ('v13', 'v24')                       # versions trained on v13's round-2 target
VERSION = 'v13'                                          # set from --version in __main__
NB = REPO / 'notebooks' / NOTEBOOKS[VERSION]
INPUT = REPO / 'results' / 'v13' / 'local_input'          # shared by all versions
GEMINI = REPO / 'external' / 'datasets' / 'nartaa__rsna-knee-hpo-assets' / 'labels_v1_gemlow.parquet'   # v22 (CC0)
CACHE_RUN = REPO / 'results' / 'v07' / 'full3'          # lingxd/v07-cache-320 version 3 output
V06 = REPO / 'results' / 'v06' / 'run1' / 'v06'
V11_OOF = {f'v11_{kind}_fold{k}_B_k16.csv': REPO / 'results' / 'v11' / run / 'v11' / f'fold{k}_B' / f'v11_{kind}_fold{k}_B_k16.csv'
           for kind in ('oof', 'gold') for k, run in enumerate(['run1', 'run2', 'run2', 'run5', 'run5'])}
F0 = REPO / 'results' / 'v13' / 'f0_1' / 'v13'
F0_CKPT = REPO / 'models' / 'v13' / 'v13' / 'fold0_N' / 'v13_fold_0_N_best.pt'
V07_SHA256 = {   # lingxd/v07-cache-320 version 2, checked equal to version 3 on 2026-10-05
    '1.2.826.0.1.3680043.8.498.10004873229099053869093324292195817260': 'd640dc921307f8daae11d76d646e53b642177bf618a6398934923a8b2ec46ec1',
    '1.2.826.0.1.3680043.8.498.10004945927472656027199792075652399585': 'a4f06f96159b67751699f4ad4711c37c42b37013d0e05797477947b4e9b9858c',
    '1.2.826.0.1.3680043.8.498.11467955500991327547315970867313333592': 'fb564444de73857027b875571d1e425714422e9f7dd93738d2e14d57ed8a21a8',
}
LABELS = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA',
          'PF OA', 'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def cells():
    nb = json.loads(NB.read_text(encoding='utf-8'))
    return [''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'code']


def env_record():
    import cv2
    import timm
    import torch
    return {'python': platform.python_version(), 'torch': torch.__version__, 'timm': timm.__version__,
            'cv2': cv2.__version__, 'device': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu',
            'git_commit': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True, text=True).stdout.strip(),
            'notebook_sha256': sha256(NB)}


# ------------------------------------------------------------------------------------ prepare
def prepare(_args):
    # 1. The v07 cache download: one file per cached study, sizes as in the manifest, known hashes.
    studies = pd.read_csv(CACHE_RUN / 'v07' / 'v07_cache_studies.csv', dtype={'StudyInstanceUID': str})
    ok = studies[studies.error.fillna('') == '']
    cache = CACHE_RUN / 'v07' / 'cache'
    files = {p.stem: p.stat().st_size for p in cache.glob('*.npz')}
    missing = sorted(set(ok.StudyInstanceUID) - set(files))
    wrong_size = [u for u, b in zip(ok.StudyInstanceUID, ok.file_bytes) if u in files and files[u] != int(b)]
    hashes = {u: sha256(cache / f'{u}.npz') == h for u, h in V07_SHA256.items()}
    print(f'v07 cache: {len(files)} files, {len(ok)} cached studies, missing {len(missing)}, '
          f'size mismatches {len(wrong_size)}, hashes {hashes}')
    assert not missing and not wrong_size and all(hashes.values()), 'v07 cache download incomplete or changed'

    # 2. Input tree with the names of the Kaggle inputs; the cache is linked, not copied.
    if INPUT.exists():
        shutil.rmtree(INPUT)
    (INPUT / 'v06-dicom-audit' / 'v06').mkdir(parents=True)
    for name in ('v06_targets.csv', 'v06_folds.csv'):
        shutil.copy(V06 / name, INPUT / 'v06-dicom-audit' / 'v06' / name)
    (INPUT / 'rsna-knee-v11-oof').mkdir()
    for name, src in V11_OOF.items():
        shutil.copy(src, INPUT / 'rsna-knee-v11-oof' / name)
    (INPUT / 'rsna-knee-hpo-assets').mkdir()
    shutil.copy(GEMINI, INPUT / 'rsna-knee-hpo-assets' / GEMINI.name)
    import _winapi
    _winapi.CreateJunction(str(CACHE_RUN), str(INPUT / 'v07-cache-320'))
    print('input tree:', sorted(str(p.relative_to(INPUT)) for p in INPUT.rglob('*.csv') if 'cache' not in p.parts))


# -------------------------------------------------------------------------------- notebook run
def targets_sha256_lf(path):
    # pandas writes CRLF line endings on Windows; hash with LF endings to compare with Kaggle.
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def kaggle_f0_targets_sha256():
    return json.loads((F0 / 'fold0_N' / 'v13_receipt_fold0_N.json').read_text())['train_targets_sha256']


def t3_independent(nb_targets_path):
    """v22: recompute T3 = 0.5 * soft5 + 0.5 * v11 OOF from the inputs, without the notebook's code,
    and return the maximum absolute difference to the notebook's training targets."""
    t = pd.read_csv(V06 / 'v06_targets.csv', dtype={'StudyInstanceUID': str}).set_index('StudyInstanceUID')
    oof = pd.concat([pd.read_csv(REPO / 'results' / 'v11' / run / 'v11' / f'fold{k}_B' / f'v11_oof_fold{k}_B_k16.csv',
                                 dtype={'StudyInstanceUID': str}).set_index('StudyInstanceUID')
                     for k, run in enumerate(['run1', 'run2', 'run2', 'run5', 'run5'])])
    gem = pd.read_parquet(GEMINI).set_index('StudyInstanceUID')
    ids = oof.index
    n = t.loc[ids, [f'{c}__n_sources' for c in LABELS]].to_numpy(float)
    soft5 = (n * t.loc[ids, LABELS].to_numpy(float) + gem.loc[ids, LABELS].to_numpy(float)) / (n + 1.0)
    want = pd.DataFrame(0.5 * soft5 + 0.5 * oof.loc[ids, LABELS].to_numpy(float), index=ids, columns=LABELS)
    got = pd.read_csv(nb_targets_path, dtype={'StudyInstanceUID': str}).set_index('StudyInstanceUID')
    assert set(got.index) == set(want.index) and not t.loc[got.index, 'is_gold'].astype(bool).any(), 'T3 study sets differ'
    return float(np.abs(got.loc[want.index, LABELS].to_numpy() - want.to_numpy()).max())


def run_cells(work_root, override, stop_after=None):
    """Execute the notebook's code cells with local paths; `override(ns)` runs after the config cell.
    Before anything is trained, the training targets are checked (v13: equal to the Kaggle F0 run;
    v22: equal to T3 recomputed independently)."""
    work_root.mkdir(parents=True, exist_ok=True)
    subs = [('/kaggle/input', INPUT.as_posix()), ('/kaggle/working', work_root.as_posix())]
    ns = {'__name__': '__main__'}
    for i, src in enumerate(cells()):
        for a, b in subs:
            src = src.replace(a, b)
        if src.startswith('%%writefile'):
            first, body = src.split('\n', 1)
            Path(first.split(None, 1)[1].strip()).write_text(body, encoding='utf-8')
        else:
            exec(compile(src, f'{NB.name}[code cell {i}]', 'exec'), ns)
        if src.startswith(f'# {VERSION} configuration'):
            override(ns)
        if 'train_targets' in ns.get('PATHS', {}) and not ns.get('_targets_checked'):
            if VERSION in KAGGLE_F0_TARGETS:
                local, kaggle = targets_sha256_lf(ns['PATHS']['train_targets']), kaggle_f0_targets_sha256()
                assert local == kaggle, f'training targets differ from the Kaggle F0 run: {local} vs {kaggle}'
                print('training targets equal to the Kaggle F0 run (sha256 with LF endings)', flush=True)
            else:
                diff = t3_independent(ns['PATHS']['train_targets'])
                assert diff <= 1e-9, f'training targets differ from the independent T3: max abs diff {diff}'
                print(f'training targets equal to the independent T3 (max abs diff {diff:.2e})', flush=True)
            ns['_targets_checked'] = True
        if stop_after is not None and i >= stop_after:
            break
    return ns


def fold(args):
    k, arm, v = args.fold, args.arm, VERSION
    if v == 'v13' and k == 0:
        raise SystemExit('v13 fold 0 is the Kaggle-trained model (D-016)')
    work_root = REPO / 'results' / v / (f'local_f{k}' if args.mode == 'folds' else f'local_smoke{args.tag}')
    tag = f'fold{k}_{arm}'
    out = work_root / v / tag
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f'{out} is not empty; move it away before a rerun')

    def override(ns):
        ns['MODE'] = args.mode
        ns['FOLD0_ARMS'] = []                # F0 is done; keeps the MRI-CORE weights out of the inputs
        ns['FOLDS_JOBS'] = [(arm, k)]        # one GPU: one job per invocation
        if args.mode == 'smoke':
            assert k == 0 and v == 'v24', 'smoke runs only for v24 arm C on fold 0'
            ns['SMOKE_ARMS'] = [arm]
        for kv in args.arm_set:              # diagnostic overrides of the arm's settings (smoke only)
            assert args.mode == 'smoke', '--arm-set is for smoke diagnostics; change the notebook for real runs'
            key, val = kv.split('=', 1)
            ns['ARMS'][arm][key] = json.loads(val)
            print(f'arm override: {key} = {ns["ARMS"][arm][key]}', flush=True)
        ns['QUOTA_AT_LAUNCH_H'] = 11.0       # no quota locally; hard stop min(10.5, 11 - 0.4) h
        ns['HARD_STOP_S'] = min(10.5, ns['QUOTA_AT_LAUNCH_H'] - 0.4) * 3600
        ns['COMMON']['num_workers'] = args.workers
        print(f'local overrides: FOLDS_JOBS {ns["FOLDS_JOBS"]}, workers {args.workers}', flush=True)

    record = {'started': time.strftime('%Y-%m-%d %H:%M:%S'), 'version': v, 'fold': k, 'arm': arm,
              'workers': args.workers, 'arm_set': args.arm_set, **env_record()}
    state = {'done': False, 'killed': None, 'commit_peak_gb': 0.0}
    threading.Thread(target=watchdog, args=(work_root / v / f'{v}_log_{tag}.txt', args.stall_min * 60, state),
                     daemon=True).start()
    threading.Thread(target=commit_sampler, args=(state,), daemon=True).start()
    try:
        run_cells(work_root, override)
    finally:
        state['done'] = True
    receipt = json.loads((out / f'{v}_receipt_fold{k}_{arm}.json').read_text())
    record['windows_commit_peak_gb'] = round(state['commit_peak_gb'], 2)
    if args.mode == 'smoke':
        record.update(finished=time.strftime('%Y-%m-%d %H:%M:%S'), status=receipt['status'], killed=state['killed'])
        (work_root / v / f'{v}_local_run_smoke_{tag}.json').write_text(json.dumps(record, indent=2))
        keys = ('status', 'checks_passed', 'checks', 'peak_reserved_gb', 'projected_fold_hours', 'train_images_per_s',
                'data_share', 'val_seconds_k16', 'smoke_val_macro_auc')
        print(json.dumps({**{key: receipt.get(key) for key in keys}, 'windows_commit_peak_gb': record['windows_commit_peak_gb']},
                         default=float))
        return
    targets_file = work_root / v / f'{v}_train_targets.csv'
    record.update(finished=time.strftime('%Y-%m-%d %H:%M:%S'), status=receipt['status'], killed=state['killed'],
                  train_targets_sha256_lf=targets_sha256_lf(targets_file))
    if v in KAGGLE_F0_TARGETS:
        record['targets_equal_kaggle_f0'] = record['train_targets_sha256_lf'] == kaggle_f0_targets_sha256()
    else:
        record['targets_max_abs_diff_independent_t3'] = t3_independent(targets_file)
    (work_root / v / f'{v}_local_run_{tag}.json').write_text(json.dumps(record, indent=2))
    print(json.dumps({key: receipt.get(key) for key in ('status', 'best_epoch', 'val_macro_k16', 'gold_macro_k16',
                                                        'gold_ci', 'train_images_per_s', 'total_seconds')}, default=float))
    if receipt['status'] != 'done' or state['killed']:
        raise SystemExit(f'{tag} did not complete (status {receipt["status"]}, killed {state["killed"]}); '
                         f'checkpoints left in {out}')
    dest = REPO / 'models' / v / v / tag
    dest.mkdir(parents=True, exist_ok=True)
    for p in out.glob('*.pt'):
        shutil.move(str(p), dest / p.name)
    check = {k2: record[k2] for k2 in ('targets_equal_kaggle_f0', 'targets_max_abs_diff_independent_t3') if k2 in record}
    print('targets check:', check, '| checkpoints moved to', dest)


def commit_sampler(state):
    """Peak Windows commit charge (total page file minus available) while training runs (L19)."""
    import ctypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong), ('ullTotalPhys', ctypes.c_ulonglong),
                    ('ullAvailPhys', ctypes.c_ulonglong), ('ullTotalPageFile', ctypes.c_ulonglong),
                    ('ullAvailPageFile', ctypes.c_ulonglong), ('ullTotalVirtual', ctypes.c_ulonglong),
                    ('ullAvailVirtual', ctypes.c_ulonglong), ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    while not state['done']:
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            state['commit_peak_gb'] = max(state['commit_peak_gb'], (m.ullTotalPageFile - m.ullAvailPageFile) / 2**30)
            state['commit_limit_gb'] = m.ullTotalPageFile / 2**30
        time.sleep(10)


def watchdog(log_path, stall_s, state):
    """Kill the trainer (a child of this process) and its loader workers if its log stops growing.
    On Windows a failed loader worker can leave the trainer blocked instead of exiting (v13 fold 2,
    2026-10-07: WinError 1450 when the commit limit was reached)."""
    while not state['done']:
        time.sleep(60)
        if state['done'] or not log_path.exists() or time.time() - log_path.stat().st_mtime < stall_s:
            continue
        query = f"(Get-CimInstance Win32_Process -Filter \"ParentProcessId={os.getpid()} and Name='python.exe'\").ProcessId"
        pids = subprocess.run(['powershell', '-NoProfile', '-Command', query], capture_output=True, text=True).stdout.split()
        for pid in pids:
            subprocess.run(['taskkill', '/T', '/F', '/PID', pid], capture_output=True)
        state['killed'] = f'log stalled for {stall_s / 60:.0f} min; killed {pids}'
        print(f'watchdog: {state["killed"]}', flush=True)
        return


# ---------------------------------------------------------------------------------- check
def check(args):
    """Re-infer the Kaggle-trained fold-0 N checkpoint locally (gold and the first fold-0 validation
    studies) and compare with the Kaggle predictions: checks the cache, the paths and the software."""
    import torch
    work_root = REPO / 'results' / 'v13' / 'local_check'
    ns = run_cells(work_root, lambda ns: ns.update(MODE='folds', FOLD0_ARMS=[], FOLDS_JOBS=[]))
    cfg = {**ns['COMMON'], **ns['PATHS'], **ns['arm_cfg']('N'), 'arm': 'N', 'fold': 0, 'num_workers': 0,
           'out_dir': str(work_root / 'v13' / 'check'), 'time_limit_s': 3600, 'mode': 'fold'}
    sys.path.insert(0, str(work_root))
    sys.argv = ['v13_train.py', json.dumps(cfg)]
    tr = importlib.import_module('v13_train')
    ck = torch.load(F0_CKPT, map_location='cpu', weights_only=False)
    assert (ck['cfg']['version'], ck['cfg']['arm'], ck['cfg']['fold']) == ('v13', 'N', 0)
    model = tr.Net(tr.build_backbone(cfg, load_weights=False)[0])
    model.load_state_dict(ck['model'])
    device = torch.device('cuda')
    model.to(device)
    targets = pd.read_csv(cfg['targets'], dtype={'StudyInstanceUID': str}).set_index('StudyInstanceUID')
    out = {'env': env_record()}
    for name, ref_file, n in (('gold', 'v13_gold_fold0_N_k16.csv', None), ('val', 'v13_oof_fold0_N_k16.csv', args.n_val)):
        ref = pd.read_csv(F0 / 'fold0_N' / ref_file, dtype={'StudyInstanceUID': str}).set_index('StudyInstanceUID')[LABELS]
        ids = ref.index.tolist()[:n] if n else ref.index.tolist()
        y = targets.loc[ids, LABELS].to_numpy(np.float32)
        ds = tr.StudyDataset(ids, y, np.ones_like(y), cfg['cache_dir'], cfg['k_infer'], False, cfg['img'], cfg['seed'], cfg['norm'])
        t = time.time()
        uids, z = tr.predict(model, ds, device, cfg['eval_batch_tokens'], True)
        assert uids == ids
        p = tr.sigmoid(z)
        diff = np.abs(p - ref.loc[ids].to_numpy(np.float32))
        rec = {'n': len(ids), 'seconds': round(time.time() - t, 1), 'max_abs_diff': float(diff.max()),
               'mean_abs_diff': float(diff.mean())}
        if name == 'gold':
            yb = targets.loc[ids, [f'{c}__gold' for c in LABELS]].to_numpy(np.float32)
            rec['macro_auc_local'] = tr.macro_auc(yb, p)[0]
            rec['macro_auc_kaggle'] = tr.macro_auc(yb, ref.loc[ids].to_numpy(np.float32))[0]
        out[name] = rec
        print(name, json.dumps(rec), flush=True)
    out['pass'] = all(out[n]['max_abs_diff'] <= args.tolerance for n in ('gold', 'val'))
    (work_root / 'v13_local_check.json').write_text(json.dumps(out, indent=2, default=float))
    print('equivalence check:', 'PASS' if out['pass'] else 'FAIL', f'(tolerance {args.tolerance})')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--version', choices=sorted(NOTEBOOKS), default='v13')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('prepare')
    c = sub.add_parser('check')
    c.add_argument('--n-val', type=int, default=100)
    c.add_argument('--tolerance', type=float, default=0.01)
    f = sub.add_parser('fold')
    f.add_argument('fold', type=int, choices=[0, 1, 2, 3, 4])
    f.add_argument('--arm', default='N', choices=['N', 'C'])
    f.add_argument('--mode', default='folds', choices=['folds', 'smoke'])   # smoke: v24 arm C check (design v21-shortlist 5)
    f.add_argument('--arm-set', action='append', default=[], metavar='KEY=JSON')   # smoke diagnostics only
    f.add_argument('--tag', default='')     # smoke: suffix of the work folder, to keep diagnostic runs apart
    f.add_argument('--workers', type=int, default=6)   # 8 reached the Windows commit limit (fold 2, 2026-10-07)
    f.add_argument('--stall-min', type=float, default=15.0)
    a = ap.parse_args()
    VERSION, NB = a.version, REPO / 'notebooks' / NOTEBOOKS[a.version]
    if a.cmd == 'check' and VERSION != 'v13':
        raise SystemExit('check re-infers the Kaggle v13 fold-0 checkpoint; run it with --version v13')
    {'prepare': prepare, 'check': check, 'fold': fold}[a.cmd](a)
