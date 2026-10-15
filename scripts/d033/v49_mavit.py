"""v49: run hengck23's public MaViT-288 knee model (Kaggle dataset hengck23/hengck23-rnsa-knee, MIT) the way his notebook
(hengck23/mavit-288-baseline-01-1-5sec-study-1gpu, Apache 2.0) does: his fast DICOM reader (6 views x 8 three-slice windows
at 288 px), his `KneeModel.infer` with checkpoint 00000008.pth, fp16 autocast, one study per forward, no TTA.
Differences from his notebook, all on the failure paths: the state-dict load must be exact (his uses strict=False), and a
study that cannot be read (or has no readable series) gets NaN and is counted (his notebook writes zeros).
Usage: python v49_mavit.py '<json args>'
  keys: src (dataset dir), data_dir (competition dir), out_csv, receipt; optional: ckpt, device, io_threads"""
import collections
import json
import os
import sys
import time

args = json.loads(sys.argv[1])
sys.path.insert(0, args['src'])
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
from configure import NUM_SLICE, SIZE  # noqa: E402  (his constants: 8 windows per view, 288 px)
from model import KneeModel  # noqa: E402
from my_fastread_knee import make_knee_dataset_reader  # noqa: E402

T0 = time.time()
LABELS = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA',
          'PF OA', 'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']
DEVICE = args.get('device', 'cuda')
CKPT = args.get('ckpt') or os.path.join(args['src'], '00000008.pth')
receipt = {'status': 'started', 'ckpt': os.path.basename(CKPT), 'device': DEVICE, 'torch': torch.__version__}


def save_receipt():
    with open(args['receipt'], 'w') as fh:
        json.dump(receipt, fh, indent=1)


save_receipt()
comp = args['data_dir']
if os.path.isfile(os.path.join(comp, 'sample_submission.csv')):   # his LABEL order is the model's output order
    assert pd.read_csv(os.path.join(comp, 'sample_submission.csv'), nrows=0).columns.tolist()[1:] == LABELS
ids = pd.read_csv(os.path.join(comp, 'test.csv'), dtype={'StudyInstanceUID': str}).StudyInstanceUID.tolist()
series = pd.read_csv(os.path.join(comp, 'test_series.csv'), dtype={'StudyInstanceUID': str})
by_study = {k: g for k, g in series.groupby('StudyInstanceUID')}

model = KneeModel(pretrained=False)   # pretrained=False: the backbone init path of his code is not on Kaggle
saved = torch.load(CKPT, map_location='cpu', weights_only=True)   # plain tensors only (checked)
res = model.load_state_dict(saved['model_state_dict'], strict=False)
receipt.update({'missing_keys': list(res.missing_keys), 'unexpected_keys': list(res.unexpected_keys)})
if res.missing_keys or res.unexpected_keys:   # gate: every weight must load
    receipt['status'] = 'keys_mismatch'
    save_receipt()
    sys.exit(2)
model = model.to(DEVICE).eval()
reader = make_knee_dataset_reader(out_size=SIZE, num_slice=NUM_SLICE, percentile=(1.0, 99.0), crop_mm=130.0,
                                  io_threads=args.get('io_threads', 32), crop_only_if_nonsquare=True)

pred = np.full((len(ids), len(LABELS)), np.nan, np.float32)
fail_types, examples, no_view = collections.Counter(), [], []
t_read = t_model = 0.0
for i, sid in enumerate(ids):
    try:
        t = time.time()
        r = reader(sid, by_study.get(sid, series.iloc[:0]), os.path.join(comp, 'test_series'), 'valid')
        t_read += time.time() - t
        if not r['view_mask'].any():   # nothing readable: no information, not a prediction
            no_view.append(sid)
            continue
        volume = torch.from_numpy(r['volume']).unsqueeze(0).byte().to(DEVICE)
        view_mask = torch.from_numpy(r['view_mask']).unsqueeze(0).bool().to(DEVICE)
        slice_pos = torch.from_numpy(r['slice']).unsqueeze(0).float().to(DEVICE)
        t = time.time()
        with torch.no_grad(), torch.amp.autocast('cuda', dtype=torch.float16):
            prob = torch.sigmoid(model.infer(volume, view_mask, slice_pos))
        pred[i] = prob.detach().float().cpu().numpy()[0]
        t_model += time.time() - t
    except Exception as exc:   # one bad study must not stop the run
        fail_types[type(exc).__name__] += 1
        if len(examples) < 10:
            examples.append({'study': sid, 'error': repr(exc)[:200]})
    if (i + 1) % 100 == 0:
        print(f'{i + 1}/{len(ids)} studies, {time.time() - T0:.0f} s, failed {sum(fail_types.values())}', flush=True)

out = pd.DataFrame(pred, columns=LABELS, index=pd.Index(ids, name='StudyInstanceUID'))
out.to_csv(args['out_csv'])
receipt.update({
    'status': 'done', 'seconds': round(time.time() - T0, 1), 'seconds_reading': round(t_read, 1),
    'seconds_model': round(t_model, 1), 'studies': len(ids), 'failed_studies': sum(fail_types.values()),
    'studies_without_view': len(no_view), 'nan_rows': int(np.isnan(pred).any(1).sum()),
    'failed_by_type': dict(fail_types), 'failed_examples': examples,
})
save_receipt()
print('mavit receipt:', json.dumps(receipt), flush=True)
