# Competition Facts

Verified against the Kaggle competition pages and the local CSV metadata on 2026-10-01.
Update this file when a fact is re-verified or changes.

## Task

- Competition: [RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)
  (slug `rsna-knee-abnormality-detection`), Research category, USD 77,000 prize pool.
- Study-level multilabel classification of knee MRI. Each study (`StudyInstanceUID`)
  receives 12 independent probabilities.
- It is the first RSNA AI Challenge dataset that pairs every training study with its
  original radiology report.

## Metric

Macro-averaged ROC-AUC over the 12 targets:
`score = mean(AUC_i for i in 12 labels)`.
Only ranking within each label matters. Monotonic calibration does not change the score.

## Labels (official column order)

```text
StudyInstanceUID,ACL,MCL,Medial Meniscus,Lateral Meniscus,Medial OA,Lateral OA,PF OA,Effusion,Synovitis,Baker's,Contusion,Fracture
```

## Timeline

| Date | Event |
|---|---|
| 2026-10-15 | Entry deadline and team merger deadline |
| 2026-10-22 23:59 UTC | Final submission deadline |

## Code competition requirements

- Submissions run as Kaggle Notebooks; CPU or GPU run time must be at most 9 hours.
- Internet access is disabled during submission runs. All weights and packages must be
  attached as Kaggle Datasets or Models.
- Freely and publicly available external data is allowed, including pretrained models.
- Up to 5 submissions per day.
- The local `data/test.csv` has only 3 placeholder studies; the hidden test set replaces it
  on rerun.

## Data

| Item | Count |
|---|---:|
| Training studies | 4,407 |
| Training series | 24,371 (Sagittal 9,864 / Coronal 8,609 / Axial 5,898) |
| Training DICOM files | 819,078 |
| Studies with complete gold labels | 58 |
| Studies with report only (no structured labels) | 4,349 |

- Image layout on Kaggle (confirmed by the legacy pipeline):
  `{train|test}/StudyInstanceUID/SeriesInstanceUID/*.dcm` under
  `/kaggle/input/rsna-knee-abnormality-detection/` (newer Kaggle mounts may use
  `/kaggle/input/competitions/rsna-knee-abnormality-detection/`; probe both). Keep train
  and test path handling symmetric.
- `train_series.csv` / `test_series.csv` columns: `StudyInstanceUID`,
  `SeriesInstanceUID`, `Fluid_Sensitive`, `Fat_Suppression`, `Anatomical_Plane`.
- Every training study has Sagittal, Coronal, and Axial series; 3-14 series per study
  (median 5); 11-320 slices per series (median 30).
- Reports are multilingual source data and must not be modified.
- Only 58 studies have gold labels, so local validation is noisy. Treat the public
  leaderboard and any gold-only CV as complementary, noisy signals.
