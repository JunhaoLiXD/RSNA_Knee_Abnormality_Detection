# RSNA Knee baseline v1

- Source: https://www.kaggle.com/code/pilkwang/rsna-knee-baseline-v1 (version 15, pulled 2026-10-01)
- License: Apache 2.0 (shown on the Kaggle page)
- Public LB: 0.891 (as of 2026-10-01); 654 votes, the most-voted notebook of the competition
- Local copy: external/kernels/pilkwang__rsna-knee-baseline-v1/

## Why it is on the list

Not a score candidate, but the root of two assets the whole 0.94 lineage depends on:
`pilkwang/rsna-knee-weights` (the 20 DINOv2 members, CC0) and
`pilkwang/rsna-knee-llm-labels` (LLM-read report labels with per-target confidences, CC0).
It is also the best-explained preprocessing reference.

## Content (Markdown read; key code spot-checked)

- Backbone: DINOv2-small (`build_model(unfreeze_last, variant="small", pool="cls_mean")`,
  last N blocks trainable), slot head per series. `GROUP = 3` adjacent slices as the three
  channels, `EPOCHS = 10`, `SEED = 2026`.
- Labels: two readers - a multilingual clause-level rule extractor (assert / negate /
  hedge, nine languages, confidence becomes a sample weight) and the public LLM table; the
  LLM table is used when attached.
- Series metadata: notes that `Fluid_Sensitive` and `Fat_Suppression` in
  `train_series.csv` agree on every row, so it re-derives weighting and fat suppression
  from DICOM headers (TR/TE, sequence names). The agreement claim is **verified** on our
  local CSVs: 24,371/24,371 train rows and 15/15 test rows have equal values.
- Slice order: filenames are SOP Instance UIDs with no anatomical order (rank correlation
  about 0.01); sorts by projection of `ImagePositionPatient` on the slice normal.
- Physical sampling: fixed-mm crop so the pixel pitch stays below about 0.5 mm.
- Laterality: normalises left/right knees per plane so medial/lateral labels are learnable.
- Inference: per-target rank averaging across members.

## Value for us

Reference for preprocessing and for the label source, and the provenance of the DINO
members inside the public stack.
