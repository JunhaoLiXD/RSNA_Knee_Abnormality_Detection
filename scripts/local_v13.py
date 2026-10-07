"""Run v13 arm-N folds on the local GPU (decision D-016).

The notebook stays the only source of truth: its code cells are executed here with the Kaggle
paths mapped to a local input tree and working directory. Differences to the Kaggle run: one GPU
(one fold per invocation), no GPU quota (the notebook's budget logic sees an 11 h session), and
the data-loader worker count.

Run in the conda env `kaggle-gpu` (environment-gpu.yml):
  python scripts/local_v13.py prepare            # input tree + checks of the v07 cache download
  python scripts/local_v13.py check              # re-infer the Kaggle fold-0 N checkpoint locally
  python scripts/local_v13.py fold 1 --workers 6 # train arm N on fold 1 (watchdog: --stall-min 15)
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
NB = REPO / 'notebooks' / 'v13-round2-mri.ipynb'
INPUT = REPO / 'results' / 'v13' / 'local_input'
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
    import _winapi
    _winapi.CreateJunction(str(CACHE_RUN), str(INPUT / 'v07-cache-320'))
    print('input tree:', sorted(str(p.relative_to(INPUT)) for p in INPUT.rglob('*.csv') if 'cache' not in p.parts))


# -------------------------------------------------------------------------------- notebook run
def targets_sha256_lf(path):
    # pandas writes CRLF line endings on Windows; hash with LF endings to compare with Kaggle.
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def kaggle_f0_targets_sha256():
    return json.loads((F0 / 'fold0_N' / 'v13_receipt_fold0_N.json').read_text())['train_targets_sha256']


def run_cells(work_root, override, stop_after=None):
    """Execute the notebook's code cells with local paths; `override(ns)` runs after the config cell.
    Before anything is trained, the training targets must equal those of the Kaggle F0 run."""
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
        if src.startswith('# v13 configuration'):
            override(ns)
        if 'train_targets' in ns.get('PATHS', {}) and not ns.get('_targets_checked'):
            local, kaggle = targets_sha256_lf(ns['PATHS']['train_targets']), kaggle_f0_targets_sha256()
            assert local == kaggle, f'training targets differ from the Kaggle F0 run: {local} vs {kaggle}'
            ns['_targets_checked'] = True
            print('training targets equal to the Kaggle F0 run (sha256 with LF endings)', flush=True)
        if stop_after is not None and i >= stop_after:
            break
    return ns


def fold(args):
    k, arm = args.fold, 'N'
    work_root = REPO / 'results' / 'v13' / f'local_f{k}'
    tag = f'fold{k}_{arm}'
    out = work_root / 'v13' / tag
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f'{out} is not empty; move it away before a rerun')

    def override(ns):
        ns['MODE'] = 'folds'
        ns['FOLD0_ARMS'] = []                # F0 is done; keeps the MRI-CORE weights out of the inputs
        ns['FOLDS_JOBS'] = [(arm, k)]        # one GPU: one job per invocation
        ns['QUOTA_AT_LAUNCH_H'] = 11.0       # no quota locally; hard stop min(10.5, 11 - 0.4) h
        ns['HARD_STOP_S'] = min(10.5, ns['QUOTA_AT_LAUNCH_H'] - 0.4) * 3600
        ns['COMMON']['num_workers'] = args.workers
        print(f'local overrides: FOLDS_JOBS {ns["FOLDS_JOBS"]}, workers {args.workers}', flush=True)

    record = {'started': time.strftime('%Y-%m-%d %H:%M:%S'), 'fold': k, 'arm': arm, 'workers': args.workers, **env_record()}
    state = {'done': False, 'killed': None}
    threading.Thread(target=watchdog, args=(work_root / 'v13' / f'v13_log_{tag}.txt', args.stall_min * 60, state),
                     daemon=True).start()
    try:
        run_cells(work_root, override)
    finally:
        state['done'] = True
    receipt = json.loads((out / f'v13_receipt_fold{k}_{arm}.json').read_text())
    record.update(finished=time.strftime('%Y-%m-%d %H:%M:%S'), status=receipt['status'], killed=state['killed'],
                  train_targets_sha256_lf=targets_sha256_lf(work_root / 'v13' / 'v13_train_targets.csv'))
    record['targets_equal_kaggle_f0'] = record['train_targets_sha256_lf'] == kaggle_f0_targets_sha256()
    (work_root / 'v13' / f'v13_local_run_{tag}.json').write_text(json.dumps(record, indent=2))
    print(json.dumps({key: receipt.get(key) for key in ('status', 'best_epoch', 'val_macro_k16', 'gold_macro_k16',
                                                        'gold_ci', 'train_images_per_s', 'total_seconds')}, default=float))
    if receipt['status'] != 'done' or state['killed']:
        raise SystemExit(f'{tag} did not complete (status {receipt["status"]}, killed {state["killed"]}); '
                         f'checkpoints left in {out}')
    dest = REPO / 'models' / 'v13' / 'v13' / tag
    dest.mkdir(parents=True, exist_ok=True)
    for p in out.glob('*.pt'):
        shutil.move(str(p), dest / p.name)
    print('targets equal to the Kaggle F0 run:', record['targets_equal_kaggle_f0'], '| checkpoints moved to', dest)


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
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('prepare')
    c = sub.add_parser('check')
    c.add_argument('--n-val', type=int, default=100)
    c.add_argument('--tolerance', type=float, default=0.01)
    f = sub.add_parser('fold')
    f.add_argument('fold', type=int, choices=[1, 2, 3, 4])
    f.add_argument('--workers', type=int, default=6)   # 8 reached the Windows commit limit (fold 2, 2026-10-07)
    f.add_argument('--stall-min', type=float, default=15.0)
    a = ap.parse_args()
    {'prepare': prepare, 'check': check, 'fold': fold}[a.cmd](a)
