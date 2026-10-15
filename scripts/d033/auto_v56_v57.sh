#!/usr/bin/env bash
# Usage: bash auto_v56_v57.sh v56|v57
# v56: wait for version 2, check its outputs equal the author's run, submit.
# v57: wait for version 1, check it (R384, R7 equal v56's; R224 changed by the mirror; format), submit after 00:00 UTC.
set -u
cd /e/Project/RSNA_Knee_Abnormality_Detection
V=$1
A=external/kernels/heliosli__0-9573-latest_20261014/output
sleep 30
until s=$(kaggle kernels status lingxd/$V-submit 2>&1); ! echo "$s" | grep -q -E "RUNNING|QUEUED"; do sleep 60; done
echo "$V: $s $(date -u)"
echo "$s" | grep -q COMPLETE || { echo "$V commit run did not complete: no submission"; exit 1; }
OUT=results/$V/run$([ "$V" = v56 ] && echo 2 || echo 1)
rm -rf "$OUT"; mkdir -p "$OUT"
kaggle kernels output lingxd/$V-submit -p "$OUT" --page-size 200 > "$OUT/_download.log" 2>&1
h() { sha256sum < "$1" | cut -c1-16; }
ok=1
if [ "$V" = v56 ]; then
  for f in raptor_sub.csv raptor224_sub.csv ours_sub.csv submission.csv; do
    a=$(h $A/$f); b=$(h $OUT/$f); echo "$f author $a ours $b"; [ "$a" = "$b" ] || ok=0
  done
  MSG="v56_submit (D-033): public 0.9573 notebook (heliosli) reproduced: R384 + R224 (0.35 of the Raptor half) + R7; R7 bundle read from the versioned compact-r7cnxfsss; outputs byte-equal to the author's run"
else
  for f in raptor_sub.csv ours_sub.csv; do
    a=$(h results/v56/run1/$f); b=$(h $OUT/$f); echo "$f v56 $a v57 $b"; [ "$a" = "$b" ] || ok=0
  done
  python - "$OUT" <<'PYEOF' || ok=0
import sys, json
import numpy as np, pandas as pd
R = sys.argv[1]
a = pd.read_csv(f"{R}/raptor224_raw.csv").set_index("StudyInstanceUID")
b = pd.read_csv("results/v56/run1/raptor224_raw.csv").set_index("StudyInstanceUID").loc[a.index]
d = float((a - b).abs().max().max()); print("R224 raw max change by the mirror:", d)
sub = pd.read_csv(f"{R}/submission.csv", dtype=str)
labels = pd.read_csv("data/sample_submission.csv", nrows=0).columns.tolist()
ids = pd.read_csv("data/test.csv", dtype=str).StudyInstanceUID.tolist()
ok = d > 1e-3 and sub.columns.tolist() == labels and sub.StudyInstanceUID.tolist() == ids and np.isfinite(sub[labels[1:]].astype(float).to_numpy()).all()
print("v57 checks:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
PYEOF
  MSG="v57_submit (D-033): v56 (public 0.9573 recipe) + anatomical mirror TTA on the CoAtNet-224 stage (varshithakolupuri's [s9] hunks)"
  # wait for the 00:00 UTC submission reset
  while [ "$(date -u +%H)" != "00" ]; do sleep 60; done
  sleep 30
fi
if [ $ok = 1 ]; then
  ver=$(echo "$OUT" | grep -o 'run[0-9]*' | tr -d run)
  kaggle competitions submit -c rsna-knee-abnormality-detection -k lingxd/$V-submit -v $ver -f submission.csv -m "$MSG" 2>&1 | tail -1
  kaggle competitions submissions -c rsna-knee-abnormality-detection 2>&1 | sed -n '3p' | cut -c1-70
else
  echo "$V checks failed: no submission"
fi
date -u
