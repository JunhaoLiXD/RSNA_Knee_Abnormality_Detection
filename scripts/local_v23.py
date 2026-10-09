"""Run notebooks/v23-coatnet-adapt.ipynb on the local GPU (decisions D-016, D-020).

The notebook stays the only source of truth: its code cells are executed here with the Kaggle paths
mapped to a local input tree (`results/v23/local_input`) and working directory (`results/v23/local`).
Inputs: v06 targets and folds, the v07 cache (junction), the v11 OOF files, the CC0 Gemini table, the
public CoAtNet checkpoint (hard link) and the v18 gold ranks.

Run in the conda env `kaggle-gpu` (environment-gpu.yml):
  python scripts/local_v23.py prepare
  python scripts/local_v23.py run stage0     # gold-58 through the adapter, compared with v18
  python scripts/local_v23.py run teacher    # untouched checkpoint on all cached studies (about 1 h)
  python scripts/local_v23.py run adapt      # adaptation (design 4.2) and the admission report
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))
import local_v13 as base   # noqa: E402  (shared helpers: sha256, watchdog)

NB = REPO / 'notebooks' / 'v23-coatnet-adapt.ipynb'
INPUT = REPO / 'results' / 'v23' / 'local_input'
WORK_ROOT = REPO / 'results' / 'v23' / 'local'
CKPT = REPO / 'external' / 'datasets' / 'nartaa__rsna-knee-publication-swa-weights-20261007' / \
    'raptor_ft_alldata_t16_blendjev_oai_d96_r384_swa.pt'
V18_GOLD = REPO / 'results' / 'v18' / 'run1' / 'v18_gold_coatnet_ranks.csv'


def prepare(_args):
    if INPUT.exists():
        for p in INPUT.iterdir():   # the cache junction is removed without touching its target
            os.rmdir(p) if p.is_junction() else shutil.rmtree(p)
    (INPUT / 'v06-dicom-audit' / 'v06').mkdir(parents=True)
    for name in ('v06_targets.csv', 'v06_folds.csv'):
        shutil.copy(base.V06 / name, INPUT / 'v06-dicom-audit' / 'v06' / name)
    (INPUT / 'rsna-knee-v11-oof').mkdir()
    for name, src in base.V11_OOF.items():
        shutil.copy(src, INPUT / 'rsna-knee-v11-oof' / name)
    (INPUT / 'rsna-knee-hpo-assets').mkdir()
    shutil.copy(base.GEMINI, INPUT / 'rsna-knee-hpo-assets' / base.GEMINI.name)
    (INPUT / 'rsna-knee-publication-swa-weights-20261007').mkdir()
    os.link(CKPT, INPUT / 'rsna-knee-publication-swa-weights-20261007' / CKPT.name)
    (INPUT / 'v18-gold-diagnostic').mkdir()
    shutil.copy(V18_GOLD, INPUT / 'v18-gold-diagnostic' / V18_GOLD.name)
    import _winapi
    _winapi.CreateJunction(str(base.CACHE_RUN), str(INPUT / 'v07-cache-320'))
    print('input tree:', sorted(str(p.relative_to(INPUT)) for p in INPUT.rglob('*') if p.is_file() and 'cache' not in p.parts))


def run(args):
    work = WORK_ROOT
    work.mkdir(parents=True, exist_ok=True)
    subs = [('/kaggle/input', INPUT.as_posix()), ('/kaggle/working', work.as_posix())]
    cells = [''.join(c['source']) for c in json.loads(NB.read_text(encoding='utf-8'))['cells'] if c['cell_type'] == 'code']
    record = {'started': time.strftime('%Y-%m-%d %H:%M:%S'), 'mode': args.mode, 'workers': args.workers,
              'git_commit': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True, text=True).stdout.strip(),
              'notebook_sha256': base.sha256(NB)}
    state = {'done': False, 'killed': None}
    threading.Thread(target=base.watchdog, args=(work / 'v23' / f'v23_log_{args.mode}.txt', args.stall_min * 60, state),
                     daemon=True).start()
    ns = {'__name__': '__main__'}
    try:
        for i, src in enumerate(cells):
            for a, b in subs:
                src = src.replace(a, b)
            if src.startswith('%%writefile'):
                first, body = src.split('\n', 1)
                Path(first.split(None, 1)[1].strip()).write_text(body, encoding='utf-8')
                continue
            exec(compile(src, f'{NB.name}[code cell {i}]', 'exec'), ns)
            if src.startswith('# v23 configuration'):
                ns['MODE'] = args.mode
                ns['NUM_WORKERS'] = args.workers
                print(f'local overrides: MODE {args.mode}, workers {args.workers}', flush=True)
    finally:
        state['done'] = True
    record.update(finished=time.strftime('%Y-%m-%d %H:%M:%S'), killed=state['killed'])
    (work / 'v23' / f'v23_local_run_{args.mode}.json').write_text(json.dumps(record, indent=2))
    print(json.dumps(record))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('prepare')
    r = sub.add_parser('run')
    r.add_argument('mode', choices=['stage0', 'teacher', 'adapt'])
    r.add_argument('--workers', type=int, default=4)
    r.add_argument('--stall-min', type=float, default=20.0)
    a = ap.parse_args()
    {'prepare': prepare, 'run': run}[a.cmd](a)
