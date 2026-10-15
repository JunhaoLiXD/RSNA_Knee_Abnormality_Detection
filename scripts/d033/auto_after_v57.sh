#!/usr/bin/env bash
# After v57 (ref 57198530) has scored: snapshot, rank crossing against 2026-10-15a; if v57 did not move us (< 20 witnesses
# above->below), submit v55 (v54 + old S6, commit run passed); otherwise stop for a decision.
set -u
cd /e/Project/RSNA_Knee_Abnormality_Detection
SCR="scripts/d033"
until s=$(kaggle competitions submissions -c rsna-knee-abnormality-detection 2>&1 | grep 57198530); echo "$s" | grep -q -E "COMPLETE|ERROR"; do sleep 900; done
echo "v57: $(echo "$s" | awk '{print $1, $3, $4, $(NF-1), $NF}')"
SNAP=external/lb/2026-10-15b
mkdir -p $SNAP && kaggle competitions leaderboard -c rsna-knee-abnormality-detection --download -p $SNAP > /dev/null 2>&1
out=$(python "$SCR/rank_cross.py" external/lb/2026-10-15a $SNAP 2>&1); echo "$out"
w=$(echo "$out" | grep -o 'above->below [0-9]*' | grep -o '[0-9]*$')
r=$(echo "$out" | grep -o 'below->above [0-9]*' | grep -o '[0-9]*$')
echo "witnesses above->below $w, below->above $r"
if [ "${w:-0}" -lt 20 ]; then
  kaggle competitions submit -c rsna-knee-abnormality-detection -k lingxd/v55-submit -v 1 -f submission.csv \
    -m "v55_submit (D-033): v54 (v47 + R7 flip-TTA + R224 with mirror TTA) + heliosli's old S6 in the ConvNeXt slot at 0.35" 2>&1 | tail -1
  kaggle competitions submissions -c rsna-knee-abnormality-detection 2>&1 | sed -n '3p' | cut -c1-70
else
  echo "v57 moved us by $w witnesses: no automatic submission, decide the base first"
fi
date -u
