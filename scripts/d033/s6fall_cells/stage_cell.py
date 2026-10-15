# Stage 2f [s6f]: nartaa's all-data S6 ConvNeXt-small ("S6F0": nartaa/rsna-knee-s6fall-weights, E_prior_s42_fall.pt, public 0.950 alone) as a second
# model of the ConvNeXt slot. This is component B of nartaa's public notebook nartaa/rsna-knee-s6fall-solo (Apache 2.0) run as its own guarded stage:
# heliosli's OLDER compact_infer.py (sha256 34f433fe..., not R7's) through nartaa's launcher, --arm E_prior, --amp fp16, size 320 / crop 288, v4 views
# placed by the SKM-TEA anatomy V-Net, evaluation stride 1, one checkpoint, one process per GPU (his launcher text, probes, arguments, receipt checks and
# one retry of failed studies are reproduced; his code bundle s6_extras.bin and every file of heliosli's code dataset are checked against pinned sha256).
# Weights licence: CC BY-NC 4.0 (nartaa).
# The stage ends by V47_T0 + READER_DEADLINE_S - READER_MIN_S - S6F_MARGIN_S (the cut-off of the R224 stage), is not started with less than S6F_MIN_S
# before it, and every process it starts runs in its own process group that is killed on every exit path. Any failure, timeout, skip, deadline hit or
# malformed output leaves S6F_OK False, so stage 3 is exactly as without S6F0; stage 3 validates the output again before using it. The stage
# writes only ours_s6f_sub.csv, ours_s6f_receipt.json and s6f_*_log.txt to the working folder and works in TMP / 's6f': no file, folder or global of
# the R7 stage (submission_receipt.json, ours_sub.csv, bundle, manifest, WORKER_ARGS, ...) is touched or rebound.
import hashlib, json, os, shutil, signal, subprocess, sys, tarfile, time, types
from pathlib import Path
import numpy as np
import pandas as pd

S6F_OK = False
S6F_PRED = None
S6F_STAGE = {'launched': False, 'skipped': None, 'killed': False, 'error': None, 'seconds': None, 'minutes_left_at_start': None,
             'n_gpu': None, 'parts': None, 'retry': None, 'failed': None, 'timed_out': None, 'env': None, 'probe': None,
             'part_receipts': None, 'progress': None}
S6F_SLUG = 'rsna-knee-s6fall-weights'                       # nartaa: CC BY-NC 4.0 weights + code manifest + code extras (Apache 2.0)
S6F_CODE_SLUG = 'rsna-orthofoundation-fold0-epoch7-20261004'   # heliosli: SKM-TEA anatomy V-Net + data pipeline (the dataset the R7 stage also reads)
S6F_INPUT = Path('/kaggle/input')
S6F_ROOT = TMP / 's6f'            # own subfolder of the R7 stage's temp folder
S6F_MIN_S = 50 * 60               # not started with less than this left before the cut-off
S6F_MARGIN_S = 15 * 60            # slack between the cut-off and the reader's launch allowance (as the R224 stage)
S6F_DEADLINE_MARGIN_S = 20 * 60   # compact_infer --deadline = start + max(budget - this, 0.8 budget) (nartaa: B_DEADLINE_MARGIN_S, above the 900 s item timeout)
S6F_RETRY_MIN_S = 10 * 60         # the one retry of failed studies runs only with at least this much of the budget left (nartaa: B_RETRY_MIN_S)
S6F_EXIT_GRACE_S = 120            # outputs complete but no exit within this: the group is killed and the run accepted (nartaa: EXIT_GRACE_S)
S6F_HEARTBEAT_S = 300
S6F_WORKERS = 2                   # DataLoader workers per GPU process (nartaa: B_WORKERS)
S6F_AMP = 'fp16'                  # the one deliberate argument difference of nartaa's run to the laptop (the T4 has no bf16)
S6F_FILES = ('ours_s6f_sub.csv', 'ours_s6f_receipt.json')
S6F_LAB = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA', 'PF OA',
           'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']
S6F_MODEL = {'file': 'E_prior_s42_fall.pt', 'sha256': '0c7297d58f061ab4e5d7c55046f51fa3e8934928046f0647a0c7854e98371c12',
             'run_config': 'E_prior_s42_fall.run_config.json', 'done': 'E_prior_s42_fall.DONE.json', 'arm': 'E_prior',
             'expect_epochs': 16, 'expect_train_studies': 4263}   # (nartaa's B_MODEL key is expect_train, which his check never reads)
S6F_DATASET_SHA = {   # nartaa/rsna-knee-s6fall-weights, files read by this stage (the checkpoint itself is pinned in S6F_MODEL)
    's6_extras.bin': 'ddc428d9f2cda0e1378b6731ca7efbdd0397978204763f2a2f81169979e50c8e',
    'code_manifest.json': 'b66c574b5c0c13ccaa49d1219d41a8781431166186ef83e78cab6a9ba6b02d22',
    'E_prior_s42_fall.run_config.json': '36e49cf0c8db97e7f995482933911f018c32fca8c5933b4d64399c128c19c886',
    'E_prior_s42_fall.DONE.json': 'acc99ed61393404feaa4f84a2e20ce27ad9f55a257b8e0d0760e83e105a20c6a'}
S6F_ANATOMY_FILE = 'anatomy.pt'
S6F_ANATOMY_SHA256 = '5904dd16eb9a4fd7a1caf90ac977f8fe2ef364908598c23c209db3fe7fd1563e'
S6F_PAYLOAD_MAGIC = b'K1PAYLOAD1\n'
S6F_SOURCE_SHA = {   # heliosli's compact_* scripts as in nartaa's scored run (compact_infer.py 34f433fe... is the older one, not R7's 8401812c...)
    'px_cache.py': 'b13e38a7ad3bd496f8027e02209653e224b0926db4f0853eeb0d076a2d6e2632',
    'compact_train.py': '14767c7a8f0daa986477511fe9a83aefe032a208ae978fabf15a5f896992ac80',
    'compact_infer.py': '34f433fe72b732543813165c3397ec80cef01b0d49b25b7b22668714f0b0ef4a',
    'probe_infer.py': 'a6cc31448019c84be5868d0a2ff1d99719b23b0f86110efc03efff3ce6bd6980',
    'knee_anchor_bank_v2.py': 'e564807a129dfcd3c984348917436ee6083066a4d685340587ebd1d3ea14f309',
    'side_common.py': 'bbcc5d027834e6a6fd48c4a8cf228e25661b7522c792587c840fe4d7cd5c0566'}
S6F_RECEIPT_SOURCES = ('px_cache.py', 'compact_train.py', 'compact_infer.py', 'probe_infer.py', 'knee_anchor_bank_v2.py')
S6F_CODE_SHA = {
    'native_cache.py': 'c53ce8985406b3b918d9e821d43518479e89d9f946daebd817f378e3949718b9',
    'native_data.py': 'f59afe205c8e193369fa3ccd22edcce8df3b293205fc48ddb1dd45169ee43b36',
    'input_provenance.py': 'b3a22500c7f976f6ee040239ada5cacecf2326861cb49af1c7d8cfdeeb55fcda',
    'intensity_mapping.py': '19be2d8cbd6f8971c1288d7512a8cca41d143470c2ba6e9b9096fde035fa9d41',
    'coronal_views.py': '841f216d2682ae2c0f8afd82fc902b9fa74924d7145b952069dea8b0bbd03c40',
    'exact_duplicates.py': '51b38db21ce9c5fe2b6278a835983414756b61ac6af81aba380b44b41b075897',
    'dicom_geometry.py': '12aa501f9704aef15b7a3bbd560951acb6d95b89b7de0141d6cf89fc3f051ab1',
    'common.py': '8283fa1f8e7ef8cfacbba52df1715636be3c9ad688e39912814e7d5bcf57105f'}
S6F_GEOMETRY = {'backbone': 'convnext_small', 'size': 320, 'crop': 288, 'views': 'v4', 'slices': 3, 'phys_mm': 3.5,
                'eval_stride': 1, 'chunk': 192, 'item_timeout': 900}

# nartaa's environment probe, launcher and component-B stack probe, byte for byte (nartaa/rsna-knee-s6fall-solo: PROBE, LAUNCHER, B_PROBE)
S6F_PROBE = r'''__PROBE__'''
S6F_LAUNCHER = r'''__LAUNCHER__'''
S6F_B_PROBE = r'''__B_PROBE__'''


class _S6FTimeout(RuntimeError):
    pass


def _s6f_sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def _s6f_tail(path, n=3000):
    try:
        return Path(path).read_text(errors='replace')[-n:]
    except Exception as e:
        return '(no log: %r)' % e


def _s6f_kill(p):
    try:
        os.killpg(p.pid, signal.SIGKILL)   # the process leads its own group (start_new_session): workers and prefetch workers included
    except Exception:
        try:
            p.kill()   # no process group to signal: at least the process itself
        except Exception:
            pass


def _s6f_gpu_snapshot():
    try:
        r = subprocess.run(['nvidia-smi', '--query-gpu=index,memory.used,memory.total,utilization.gpu', '--format=csv,noheader'],
                           capture_output=True, text=True, timeout=20)
        return [l.strip() for l in r.stdout.splitlines() if l.strip()] or [r.stderr.strip()[:200]]
    except Exception as e:
        return ['nvidia-smi failed: %r' % e]


def _s6f_mount(slug, marker):
    cands = [S6F_INPUT / slug, S6F_INPUT / 'competitions' / slug]
    cands += list(S6F_INPUT.glob('datasets/*/' + slug)) + list(S6F_INPUT.glob('datasets/*/' + slug + '/*'))
    cands += list(S6F_INPUT.glob('*/' + slug)) + list(S6F_INPUT.glob(slug + '/*'))
    found = []
    for p in cands:
        if (p / marker).is_file() and p.resolve() not in [f.resolve() for f in found]:
            found.append(p)
    if len(found) != 1:
        raise RuntimeError('cannot resolve %s (marker %s): %s' % (slug, marker, found))
    return found[0]


def _s6f_safe_rel(name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise RuntimeError('unsafe payload member %r' % name)
    return p


def _s6f_extract(path, target, members):
    # the code payload = magic + an uncompressed tar; exact member set, sizes and sha256 (nartaa: extract_payload)
    if target.exists():
        shutil.rmtree(target)
    with open(path, 'rb') as f:
        if f.read(len(S6F_PAYLOAD_MAGIC)) != S6F_PAYLOAD_MAGIC:
            raise RuntimeError('payload magic mismatch')
        with tarfile.open(fileobj=f, mode='r:') as tar:
            ms = tar.getmembers()
            if {m.name for m in ms} != set(members) or len(ms) != len(members):
                raise RuntimeError('payload member set differs from the manifest')
            for m in ms:
                _s6f_safe_rel(m.name)
                if not m.isfile() or m.size != members[m.name]['bytes']:
                    raise RuntimeError('payload member %s: not a regular file or size differs' % m.name)
            for m in ms:
                dst = target / _s6f_safe_rel(m.name)
                dst.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(m) as src, open(dst, 'xb') as out:
                    shutil.copyfileobj(src, out, 1 << 20)
    for name, rec in members.items():
        if _s6f_sha(target / name) != rec['sha256']:
            raise RuntimeError('payload member %s sha differs' % name)


def _s6f_prepare():
    # nartaa: prepare_inputs. Returns a namespace with the resolved folders, the code tree, the launcher and the test ids.
    I = types.SimpleNamespace()
    I.ds = _s6f_mount(S6F_SLUG, 'checkpoint-manifest.json')
    I.helios = _s6f_mount(S6F_CODE_SLUG, S6F_ANATOMY_FILE)
    for name, want in S6F_DATASET_SHA.items():
        if _s6f_sha(I.ds / name) != want:
            raise RuntimeError('%s differs from the pinned sha256' % name)
    man = json.loads((I.ds / 'code_manifest.json').read_text())
    if _s6f_sha(I.ds / S6F_MODEL['file']) != S6F_MODEL['sha256']:
        raise RuntimeError('model sha differs from the pinned sha256')
    if _s6f_sha(I.helios / S6F_ANATOMY_FILE) != S6F_ANATOMY_SHA256:
        raise RuntimeError('anatomy.pt differs from the S6F0 anchor checkpoint')
    cfg = json.loads((I.ds / S6F_MODEL['run_config']).read_text())
    want = {'size': S6F_GEOMETRY['size'], 'crop': S6F_GEOMETRY['crop'], 'views': S6F_GEOMETRY['views'], 'slices': S6F_GEOMETRY['slices'],
            'phys_mm': S6F_GEOMETRY['phys_mm'], 'backbone': S6F_GEOMETRY['backbone'], 'spatial_attn': True, 'arms': S6F_MODEL['arm']}
    bad = {k: (cfg.get(k), v) for k, v in want.items() if cfg.get(k) != v}
    if bad:
        raise RuntimeError('run_config differs from the inference arguments (trained, inferred): %s' % bad)
    done = json.loads((I.ds / S6F_MODEL['done']).read_text())
    if done.get('model_sha256') != S6F_MODEL['sha256'] or os.path.basename(done.get('model', '')) != S6F_MODEL['file']:
        raise RuntimeError('DONE marker does not record this model')
    for k in ('epochs', 'train_studies'):
        if done.get(k) != S6F_MODEL['expect_' + k]:
            raise RuntimeError('DONE marker %s=%s, expected %s' % (k, done.get(k), S6F_MODEL['expect_' + k]))
    # code = the scored run's exact file set: the extras from nartaa's dataset, everything else from heliosli's; every file is checked
    # against the scored sha256 / size, so the tree is byte-identical to the one that scored 0.950
    I.code_root = S6F_ROOT / 'src'
    extras = {n: man['members'][n] for n in man['from_this_dataset']}
    _s6f_extract(I.ds / 's6_extras.bin', I.code_root, extras)
    for n, rec in man['members'].items():
        if n in extras:
            continue
        src, dst = I.helios / _s6f_safe_rel(n), I.code_root / _s6f_safe_rel(n)
        if not src.is_file() or src.stat().st_size != rec['bytes']:
            raise RuntimeError('heliosli file %s missing or size differs' % n)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        if _s6f_sha(dst) != rec['sha256']:
            raise RuntimeError('heliosli file %s sha differs' % n)
    I.src = I.code_root / 'heliosli'
    I.code = I.code_root / 'cloud_code'
    for n, want_sha in S6F_SOURCE_SHA.items():
        if _s6f_sha(I.src / n) != want_sha:
            raise RuntimeError('heliosli/%s differs from the pinned sha256' % n)
    for n, want_sha in S6F_CODE_SHA.items():
        if _s6f_sha(I.code / 'training' / n) != want_sha:
            raise RuntimeError('cloud_code/training/%s differs from the pinned sha256' % n)
    I.models = S6F_ROOT / 'models'   # the models folder holds exactly this one file
    if I.models.exists():
        shutil.rmtree(I.models)
    I.models.mkdir(parents=True)
    try:
        os.symlink(I.ds / S6F_MODEL['file'], I.models / S6F_MODEL['file'])
    except OSError:
        shutil.copyfile(I.ds / S6F_MODEL['file'], I.models / S6F_MODEL['file'])
    I.anatomy = I.helios / S6F_ANATOMY_FILE
    I.launcher = S6F_ROOT / 'launch' / 'k1_b_infer.py'
    I.launcher.parent.mkdir(parents=True, exist_ok=True)
    I.launcher.write_text(S6F_LAUNCHER.replace('__SRC__', repr(str(I.src))).replace('__CODE__', repr(str(I.code))))
    test = pd.read_csv(DATA / 'test.csv', dtype={'StudyInstanceUID': str})
    I.test_ids = test['StudyInstanceUID'].astype(str).tolist()
    if not I.test_ids or len(I.test_ids) != len(set(I.test_ids)):
        raise RuntimeError('test.csv empty or has duplicate study ids')
    ss = DATA / 'sample_submission.csv'
    cols = list(pd.read_csv(ss, nrows=1).columns) if ss.is_file() else ['StudyInstanceUID'] + S6F_LAB
    if cols[0] != 'StudyInstanceUID' or sorted(cols[1:]) != sorted(S6F_LAB):
        raise RuntimeError('submission columns differ from the 12 findings: %s' % cols)
    sc = pd.read_csv(DATA / 'test_series.csv', dtype=str, usecols=['StudyInstanceUID'])
    I.cost = sc['StudyInstanceUID'].value_counts().to_dict()
    I.manifest_sha256 = _s6f_sha(I.ds / 'code_manifest.json')
    print('S6F_INPUTS_OK %d test studies | weights %s | code %s | %d payload files | model %s...' % (
        len(I.test_ids), I.ds, I.helios, len(man['members']), S6F_MODEL['sha256'][:16]), flush=True)
    return I


def _s6f_probe_env():
    r = subprocess.run([sys.executable, '-c', S6F_PROBE], capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    line = [l for l in r.stdout.splitlines() if l.startswith('K1_ENV ')]
    if r.returncode != 0 or not line:
        raise RuntimeError('environment probe failed rc %d: %s %s' % (r.returncode, r.stdout[-1500:], r.stderr[-1500:]))
    return json.loads(line[0][len('K1_ENV '):])


def _s6f_probe_b(I):
    # nartaa: probe_b_stack. The launcher (stubs, distutils guard), compact_infer import, the vendored MONAI V-Net with anatomy.pt (+ one
    # forward pass) and compact_train.Net with the checkpoint (strict). CPU only, so a broken stack is seen before any GPU time is spent.
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1')
    env.pop('K1_DISTUTILS_SHIM', None)
    g = S6F_GEOMETRY
    r = subprocess.run([sys.executable, '-c', S6F_B_PROBE, str(I.launcher), str(I.anatomy), str(I.models / S6F_MODEL['file']),
                        g['backbone'], str(g['crop']), str(g['slices'])],
                       capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL, env=env, cwd=str(S6F_ROOT))
    line = [l for l in r.stdout.splitlines() if l.startswith('K1_BPROBE ')]
    if r.returncode != 0 or not line:
        raise RuntimeError('component-B stack probe failed rc %d: %s %s' % (r.returncode, r.stdout[-1500:], r.stderr[-2500:]))
    return json.loads(line[0][len('K1_BPROBE '):])


def _s6f_cmd(I, assignment, out_dir, tmp_dir, deadline):
    g = S6F_GEOMETRY   # nartaa: b_cmd
    return [sys.executable, '-u', str(I.launcher), '--data', str(DATA), '--split', 'test', '--code', str(I.code),
            '--models', str(I.models), '--arm', S6F_MODEL['arm'], '--backbone', g['backbone'], '--size', str(g['size']),
            '--crop', str(g['crop']), '--views', g['views'], '--slices', str(g['slices']), '--phys-mm', str(g['phys_mm']),
            '--eval-stride', str(g['eval_stride']), '--anchor-weights', str(I.anatomy), '--amp', S6F_AMP, '--chunk', str(g['chunk']),
            '--workers', str(S6F_WORKERS), '--item-timeout', str(g['item_timeout']), '--assignment', str(assignment),
            '--output', str(out_dir), '--tmp', str(tmp_dir), '--dump-logits', str(Path(out_dir) / 'logits.json'),
            '--deadline', '%.0f' % deadline]


def _s6f_split(ids, cost, n):
    order = sorted(ids, key=lambda u: (-cost.get(u, 0), u))   # nartaa: split_parts (largest studies first, dealt round-robin, then interleaved)
    parts = [order[i::n] for i in range(n)]
    return [p[::2] + p[1::2] for p in parts if p]


def _s6f_env(gi):
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gi), OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
               MALLOC_ARENA_MAX='2', PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1')
    env.pop('K1_PX_DUMP', None)
    return env


def _s6f_done(pdir):
    return (pdir / 'receipt.json').is_file() and (pdir / 'logits.json').is_file() and 'WORKER_DONE' in _s6f_tail(pdir / 'log.txt', 3000)


def _s6f_progress(logp, n=4000):
    out = []
    for l in _s6f_tail(logp, n).splitlines():
        if l.startswith('{') and '"done"' in l:
            try:
                out.append(json.loads(l))
            except Exception:
                pass
    return out


def _s6f_run_group(specs, timeout_s, what, live):
    # nartaa: run_group. Every spec {name, cmd, env, cwd, log, done_when} runs in its own session; polled until all exit, one fails or
    # timeout_s passes; a failure or the timeout kills every group (DataLoader children included). done_when(): the child's outputs are
    # complete; if it then has not exited within S6F_EXIT_GRACE_S (an interpreter-exit hang) its group is killed and the run counts as a success.
    procs, t_start, last_hb, last_check = [], time.time(), time.time(), 0.0
    try:
        for s in specs:
            fh = open(s['log'], 'w')
            p = subprocess.Popen(s['cmd'], env=s['env'], cwd=s.get('cwd'), stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                 start_new_session=True)   # own process group
            live.append(p)
            procs.append({'s': s, 'p': p, 'fh': fh, 't1': time.time(), 'done_at': None})
            print('S6F [%s] started %s pid %d' % (what, s['name'], p.pid), flush=True)
        done = {}
        while len(done) < len(procs):
            now_ = time.time()
            check = now_ - last_check >= 5
            if check:
                last_check = now_
            for r in procs:
                s, p = r['s'], r['p']
                if s['name'] in done:
                    continue
                rc, note = p.poll(), ''
                if rc is None and check and s.get('done_when') is not None:
                    try:
                        complete = bool(s['done_when']())
                    except Exception:
                        complete = False
                    if complete and r['done_at'] is None:
                        r['done_at'] = now_
                    if r['done_at'] is not None and now_ - r['done_at'] > S6F_EXIT_GRACE_S and p.poll() is None:
                        _s6f_kill(p)
                        rc, note = 0, 'outputs complete, no exit after %ds: group killed, accepted' % S6F_EXIT_GRACE_S
                        print('S6F [%s] %s: %s' % (what, s['name'], note), flush=True)
                if rc is not None:
                    done[s['name']] = (rc, round(time.time() - r['t1'], 1), note)
                    r['fh'].close()
                    _s6f_kill(p)
                    print('S6F [%s] %s exited rc %d after %.0fs' % (what, s['name'], rc, time.time() - r['t1']), flush=True)
                    if rc != 0:
                        for r2 in procs:
                            if r2['s']['name'] not in done:
                                _s6f_kill(r2['p'])
                        raise RuntimeError('%s: %s exited %d; log tail:\n%s' % (what, s['name'], rc, _s6f_tail(s['log'])))
            if len(done) == len(procs):
                break
            if time.time() - t_start > timeout_s:
                for r in procs:
                    if r['s']['name'] not in done:
                        _s6f_kill(r['p'])
                raise _S6FTimeout('%s: timeout after %ds; still running %s' % (what, timeout_s, [r['s']['name'] for r in procs if r['s']['name'] not in done]))
            if time.time() - last_hb >= S6F_HEARTBEAT_S:
                last_hb = time.time()
                for r in procs:
                    if r['s']['name'] in done:
                        continue
                    prog = _s6f_progress(r['s']['log'])[-1:]
                    print('S6F [heartbeat] %s %s | %.0fs | gpu %s | %s' % (what, r['s']['name'], time.time() - r['t1'], _s6f_gpu_snapshot(),
                                                                       json.dumps(prog[0])[:300] if prog else '(no progress line yet)'), flush=True)
            time.sleep(2)
        return [(r['s']['name'],) + done[r['s']['name']] for r in procs]
    finally:
        for r in procs:
            if r['p'].poll() is None:
                _s6f_kill(r['p'])
            try:
                r['fh'].close()
            except Exception:
                pass


def _s6f_collect(pdir, part):
    # nartaa: collect_part. Receipt, source and anchor checks; the logits (mean over the models = the one checkpoint) against predictions.csv.
    rec = json.loads((pdir / 'receipt.json').read_text())
    if rec.get('status') != 'PASS' or rec.get('studies') != len(part):
        raise RuntimeError('%s: receipt status %s, studies %s (expected %d)' % (pdir.name, rec.get('status'), rec.get('studies'), len(part)))
    if rec.get('amp') != S6F_AMP or rec.get('models') != [S6F_MODEL['file']] or rec.get('spatial_models') != 1:
        raise RuntimeError('%s: receipt amp %s models %s spatial %s' % (pdir.name, rec.get('amp'), rec.get('models'), rec.get('spatial_models')))
    if rec.get('anchor_weights_sha256') != S6F_ANATOMY_SHA256:
        raise RuntimeError('%s: anchor weights sha differs' % pdir.name)
    if not isinstance(rec.get('timed_out'), bool):
        raise RuntimeError('%s: the receipt does not state timed_out (%r)' % (pdir.name, rec.get('timed_out')))
    shas = rec.get('sha256')
    if not isinstance(shas, dict) or not set(S6F_RECEIPT_SOURCES) <= set(shas):
        raise RuntimeError('%s: the receipt source shas are incomplete: %s' % (pdir.name, sorted(shas) if isinstance(shas, dict) else shas))
    for n, s in shas.items():
        if S6F_SOURCE_SHA.get(n) != s:
            raise RuntimeError('%s: source %s sha differs in the receipt' % (pdir.name, n))
    n_anchor = sum(int(v) for v in (rec.get('anchor_methods') or {}).values())
    if n_anchor != rec.get('scored'):   # every scored study must have had its SKM-TEA anchor record
        raise RuntimeError('%s: %s scored studies but %d anchor records %s' % (pdir.name, rec.get('scored'), n_anchor, rec.get('anchor_methods')))
    logits = json.loads((pdir / 'logits.json').read_text())
    pc = pd.read_csv(pdir / 'predictions.csv', dtype={'StudyInstanceUID': str})
    if list(pc.columns) != ['StudyInstanceUID'] + S6F_LAB:
        raise RuntimeError('%s: predictions.csv columns %s' % (pdir.name, list(pc.columns)))
    pc = pc.set_index('StudyInstanceUID')
    z = {}
    for u in part:
        if u not in logits:
            continue
        a = np.asarray(logits[u], np.float64)
        if a.shape != (1, len(S6F_LAB)) or not np.isfinite(a).all():
            raise RuntimeError('%s: logits for %s have shape %s or are non-finite' % (pdir.name, u, a.shape))
        if u not in pc.index:
            raise RuntimeError('%s: %s has logits but no predictions.csv row' % (pdir.name, u))
        zm = a.mean(0)
        p = 1.0 / (1.0 + np.exp(-zm))
        d = float(np.abs(p - pc.loc[u, S6F_LAB].to_numpy(np.float64)).max())
        if d >= 1e-5:
            raise RuntimeError('%s: predictions.csv disagrees with the logits for %s (%.2e)' % (pdir.name, u, d))
        z[u] = zm
    extra = set(logits) - set(part)
    if extra:
        raise RuntimeError('%s: logits for studies outside the assignment: %s' % (pdir.name, sorted(extra)[:3]))
    fallback = dict(rec.get('fallback') or {})
    for u in [u for u in part if u not in z]:
        fallback.setdefault(u, 'no logits')
    return z, fallback, rec


def _s6f_run(I, n_gpu, end):
    # nartaa: run_b. One process per GPU, one retry of the failed studies. The deadline (first pass or retry) is a failure of the stage: a
    # receipt whose timed_out is not False, or any fallback reason naming the deadline. Returns (z, failed, info).
    def deadline_named(fb):
        return [u for u, v in fb.items() if 'deadline' in str(v).lower()]
    out = S6F_ROOT / 'out'
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    ids = I.test_ids
    parts = _s6f_split(ids, I.cost, n_gpu)
    t_start = time.time()
    budget = end - t_start
    deadline = t_start + max(budget - S6F_DEADLINE_MARGIN_S, budget * 0.8)
    specs, pdirs = [], []
    for gi, part in enumerate(parts):
        pdir = out / ('part%d' % gi)
        pdir.mkdir()
        (pdir / 'ids.json').write_text(json.dumps(part))
        specs.append({'name': 'part%d' % gi, 'cmd': _s6f_cmd(I, pdir / 'ids.json', pdir, S6F_ROOT / ('tmp%d' % gi), deadline),
                      'env': _s6f_env(gi), 'cwd': str(S6F_ROOT), 'log': pdir / 'log.txt', 'done_when': (lambda d=pdir: _s6f_done(d))})
        pdirs.append(pdir)
    S6F_STAGE['parts'] = [len(p) for p in parts]
    S6F_STAGE['launched'] = True
    print('S6F %d studies over %d GPU process(es) %s, budget %ds, compact_infer deadline +%ds' % (
        len(ids), len(parts), [len(p) for p in parts], budget, deadline - t_start), flush=True)
    live = []
    try:
        runs = _s6f_run_group(specs, budget, 'S6F', live)
        z, fallback, receipts = {}, {}, []
        for pdir, part in zip(pdirs, parts):
            zz, fb, rec = _s6f_collect(pdir, part)
            z.update(zz)
            fallback.update(fb)
            receipts.append({k: rec.get(k) for k in ('studies', 'scored', 'seconds', 'amp', 'gpu', 'torch', 'timm', 'stats', 'timed_out', 'anchor_methods')})
            receipts[-1]['progress'] = _s6f_progress(pdir / 'log.txt', 200000)[-1:]
        S6F_STAGE['part_receipts'] = receipts
        S6F_STAGE['timed_out'] = [rc.get('timed_out') for rc in receipts]
        timed = [i for i, rc in enumerate(receipts) if rc.get('timed_out') is not False]
        if timed or deadline_named(fallback):
            raise _S6FTimeout('compact_infer reached its deadline (timed_out not False in part(s) %s); %d studies have no prediction: %s' % (
                timed, len(fallback), dict(list(fallback.items())[:5])))
        retry = None
        if fallback:
            left = end - time.time()
            print('S6F %d fallback studies %s; %.0fs of budget left' % (len(fallback), dict(list(fallback.items())[:5]), left), flush=True)
            if left >= S6F_RETRY_MIN_S:
                rdir = out / 'retry'
                rdir.mkdir()
                rids = sorted(fallback)
                (rdir / 'ids.json').write_text(json.dumps(rids))
                rdeadline = time.time() + max(left - S6F_DEADLINE_MARGIN_S, left * 0.8)
                rruns = _s6f_run_group([{'name': 'retry', 'cmd': _s6f_cmd(I, rdir / 'ids.json', rdir, S6F_ROOT / 'tmp_retry', rdeadline),
                                         'env': _s6f_env(0), 'cwd': str(S6F_ROOT), 'log': rdir / 'log.txt',
                                         'done_when': lambda: _s6f_done(rdir)}], left, 'S6F', live)
                zz, fb2, rec2 = _s6f_collect(rdir, rids)
                if rec2.get('timed_out') is not False or deadline_named(fb2):
                    raise _S6FTimeout('compact_infer reached its deadline in the retry (timed_out %r); %d of %d retried studies have no prediction' % (
                        rec2.get('timed_out'), len(fb2), len(rids)))
                z.update(zz)
                retry = {'ids': len(rids), 'recovered': len(zz), 'still_failing': len(fb2), 'seconds': rec2.get('seconds'), 'runs': rruns}
                fallback = fb2
            else:
                retry = {'ids': len(fallback), 'skipped': 'only %.0f s left' % left}
        S6F_STAGE['retry'] = retry
        missing = [u for u in ids if u not in z]
        failed = {u: str(fallback.get(u, 'no logits'))[:200] for u in missing}
        return z, failed, {'runs': runs, 'parts': [len(p) for p in parts], 'retry': retry, 'seconds': round(time.time() - t_start, 1)}
    finally:
        for p in live:
            if p.poll() is None:
                _s6f_kill(p)   # controller-less here: every worker group is killed on every exit path
            try:
                p.wait(timeout=60)
            except Exception:
                pass


def _s6f_stage(end):
    t0 = time.time()
    S6F_ROOT.mkdir(parents=True, exist_ok=True)
    env = _s6f_probe_env()
    S6F_STAGE['env'] = {k: env.get(k) for k in ('python', 'torch', 'cuda', 'n_gpu', 'gpus', 'capability', 'timm', 'pydicom', 'numpy', 'pandas', 'cv2', 'scipy')}
    print('S6F_ENV', json.dumps(env), flush=True)
    if not env.get('cuda_available') or env.get('n_gpu', 0) < 1:
        raise RuntimeError('CUDA is not available')
    S6F_STAGE['n_gpu'] = n_gpu = max(1, int(env.get('n_gpu', 1)))
    I = _s6f_prepare()
    print('S6F_ASSETS_READY seconds %.1f' % (time.time() - t0), flush=True)
    S6F_STAGE['probe'] = _s6f_probe_b(I)
    print('S6F_BPROBE', json.dumps(S6F_STAGE['probe']), flush=True)
    z, failed, info = _s6f_run(I, n_gpu, end)
    ids = I.test_ids
    nan12 = np.full(len(S6F_LAB), np.nan)
    Z = np.stack([z.get(u, nan12) for u in ids])
    P = 1.0 / (1.0 + np.exp(-Z))
    ok = np.array([u in z for u in ids])
    if not ok.any() or not np.isfinite(P[ok]).all():
        raise RuntimeError('no study scored, or non-finite probabilities')
    P[~ok] = P[ok].mean(axis=0)   # a failed study is filled with the column mean (heliosli's controller does the same): never read as a prediction
    sub = pd.DataFrame({'StudyInstanceUID': ids})
    for j, l in enumerate(S6F_LAB):
        sub[l] = P[:, j]
    sub.to_csv(WORK / 'ours_s6f_sub.csv', index=False, float_format='%.17g')
    receipt = {'status': 'PASS', 'rows': len(ids), 'scored': int(ok.sum()), 'fallback_studies': len(failed), 'fallback_reasons': dict(list(failed.items())[:50]),
               'model': S6F_MODEL['file'], 'model_sha256': S6F_MODEL['sha256'], 'amp': S6F_AMP, 'n_gpu': n_gpu, 'parts': info['parts'],
               'retry': info['retry'], 'seconds': info['seconds'], 'code_manifest_sha256': I.manifest_sha256,
               'env': S6F_STAGE['env'], 'part_receipts': S6F_STAGE['part_receipts']}
    (WORK / 'ours_s6f_receipt.json').write_text(json.dumps(receipt, indent=1, default=str))
    S6F_STAGE['failed'] = len(failed)
    return receipt


# ---- driver: never stops the notebook; any exception leaves S6F_OK False
try:
    for _s6f_f in S6F_FILES:   # no stale file can be mistaken for this run's output
        if (WORK / _s6f_f).is_file():
            (WORK / _s6f_f).unlink()
    for _s6f_l in WORK.glob('s6f_*_log.txt'):
        _s6f_l.unlink()
    shutil.rmtree(S6F_ROOT, ignore_errors=True)
    S6F_PRED = S6F_ROOT / 'out'
    _s6f_end = V47_T0 + READER_DEADLINE_S - READER_MIN_S - S6F_MARGIN_S
    _s6f_left = _s6f_end - time.time()
    S6F_STAGE['minutes_left_at_start'] = round(_s6f_left / 60)
    if _s6f_left < S6F_MIN_S:
        S6F_STAGE['skipped'] = 'only %.0f min left' % (_s6f_left / 60)
        print('S6F_SKIPPED', S6F_STAGE['skipped'], flush=True)
    else:
        _s6f_t0 = time.time()
        try:
            _s6f_stage(_s6f_end)
            S6F_OK = True
        except _S6FTimeout as _s6f_exc:   # the cut-off (hard kill) or compact_infer's own deadline: S6F0 is not used at all
            S6F_OK = False
            S6F_STAGE['killed'] = True
            S6F_STAGE['error'] = repr(_s6f_exc)[:600]
        except Exception as _s6f_exc:
            S6F_OK = False
            S6F_STAGE['error'] = repr(_s6f_exc)[:600]
        finally:
            S6F_STAGE['seconds'] = round(time.time() - _s6f_t0, 1)
            for _s6f_log in sorted(S6F_PRED.glob('*/log.txt')):
                try:
                    shutil.copyfile(_s6f_log, WORK / ('s6f_' + _s6f_log.parent.name + '_log.txt'))
                except Exception:
                    pass
        print('S6F_STAGE', json.dumps(S6F_STAGE, default=str), 'ok=%s' % S6F_OK, flush=True)
except Exception as _s6f_exc:   # never stop the notebook: stage 3 then blends without S6F0
    S6F_OK = False
    S6F_STAGE['error'] = repr(_s6f_exc)[:600]
    print('S6F_STAGE_ERROR', S6F_STAGE['error'], flush=True)
