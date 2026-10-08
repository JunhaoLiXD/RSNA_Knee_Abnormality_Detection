# Competition Facts

Verified against the Kaggle competition pages and the local CSV metadata on 2026-10-01
(rules, prizes and test-set facts re-read on 2026-10-01 during the baseline survey).
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
- Scores are shown with 3 decimals (leaderboard, its download, and the submissions API all return 3
  decimals), but ranking uses the unrounded score: on 2026-10-08 our team ranked 72nd of 379 teams
  displayed at 0.950, ahead of 282 teams whose last submission was earlier than ours, which a
  rounded score with time tie-breaks would not produce. Daily quota resets at 00:00 UTC.
- The local `data/test.csv` has only 3 placeholder studies; the hidden test set (about
  1,300 studies per the data page) replaces it on rerun. The `Report` column is absent at
  test time.
- Prevalence is not guaranteed to match between train, public and private test sets.

## Efficiency Prize (second track)

- USD 18,000 of the pool (7,000 / 6,000 / 5,000). Main board: USD 59,000 for places 1-10.
- Score to minimise on the private set:
  `AUC / (Benchmark - maxAUC) + RuntimeSeconds / 32400`, where Benchmark is the
  `sample_submission.csv` score and maxAUC the best private AUC.
- Only the submissions selected for the main board are considered.
- Public efficiency ranks: notebook `ryanholbrook/rsna-knee-abnormalities-efficiency-lb`.

## Host rulings (forum)

- Commercial LLM APIs may be used to read reports and derive labels; LLM-derived labels or
  embeddings may be used for training (host, topic 733965).
- Gold labels were assigned from the images, independently of the reports; images are
  authoritative when they disagree (host, topic 733826).
- External datasets: a non-commercial licence alone does not exclude a dataset;
  click-through registration is generally acceptable; institution approvals, IRB or long
  credentialing may not be (host, 733965). No explicit allow-list yet (topic 743416).
- Winners must publish code and weights openly; see the Prizes page.

## Data

| Item | Count |
|---|---:|
| Training studies | 4,407 |
| Training series | 24,371 (Sagittal 9,864 / Coronal 8,609 / Axial 5,898) |
| Training DICOM files | 819,078 |
| Studies with complete gold labels | 58 |
| Studies with report only (no structured labels) | 4,349 |

- Image layout on Kaggle (verified 2026-10-01 in the legacy notebooks and the public
  notebooks): `{train_series|test_series}/StudyInstanceUID/SeriesInstanceUID/*.dcm` under
  `/kaggle/input/rsna-knee-abnormality-detection/` (newer Kaggle mounts may use
  `/kaggle/input/competitions/rsna-knee-abnormality-detection/`; probe both). Keep train
  and test path handling symmetric.
- `train_series.csv` / `test_series.csv` columns: `StudyInstanceUID`,
  `SeriesInstanceUID`, `Fluid_Sensitive`, `Fat_Suppression`, `Anatomical_Plane`.
  `Fluid_Sensitive` and `Fat_Suppression` are identical on every row of both CSVs
  (verified 2026-10-01), so they encode one property, not two.
- Every training study has Sagittal, Coronal, and Axial series; 3-14 series per study
  (median 5); 11-320 slices per series (median 30).
- Reports are multilingual source data and must not be modified.
- Training DICOM audit (v06, 2026-10-01, all 819,078 files): every training series is
  uncompressed Explicit VR Little Endian, single-frame, and has full
  `ImagePositionPatient`/`ImageOrientationPatient` geometry; no header or decode errors.
  The data page's mention of JPEG Lossless / JPEG 2000 therefore applies only to the test
  set (or not at all); test-time decoding must still handle them.
- Pixel spacing median 0.32 mm (1-99%: 0.14-0.70); field of view median 160 mm, 5.7% of
  chosen series below 140 mm; slice gap median 3.5 mm; 28% of series are oblique by more
  than 10 degrees, 3% by more than 20.
- `Laterality` tag is present on 49% of series (values R/L/RIGHT/LEFT); `StationName` and
  `InstitutionName` are stripped. `Manufacturer` + `ManufacturerModelName` +
  `MagneticFieldStrength` give a scanner fingerprint for 94.7% of non-gold studies (45
  groups, largest 12%). Label prevalence differs strongly between scanner groups.
- Only 58 studies have gold labels, so local validation is noisy. Treat the public
  leaderboard and any gold-only CV as complementary, noisy signals.
