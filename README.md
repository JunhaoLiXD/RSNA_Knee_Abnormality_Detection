# RSNA Knee Abnormality Detection

This repository contains data-audit tooling and a complete 2.5D MRI baseline for the
[RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)
Kaggle competition.

The current V02 implementation covers fold-safe calibrated report weak labels, MRI
series selection, DICOM preprocessing, study-level cross-validation, time-guarded
resumable training, checkpointing, test inference, and submission generation.

## Model versions

| Version | Notebook | Main change | Status |
|---|---|---|---|
| V01 | `v01-rsna-knee-2p5d-baseline.ipynb` | Initial rule-weak 3-plane 2.5D EfficientNet-B0 baseline | Kaggle score 0.613 |
| V02 | `v02-rsna-knee-2p5d-baseline.ipynb` | Fold-safe calibrated soft labels, gold weight 8, no class `pos_weight`, resumable runtime guard | Ready to run |

Starting with V02, every new model Notebook is an `.ipynb`-only artifact whose
filename starts with its two-digit version, such as `v03-...ipynb`.

## Competition task

Each sample is a complete knee MRI study identified by `StudyInstanceUID`. A study
contains multiple MRI series acquired in different anatomical planes and with
different sequence settings.

The model predicts 12 independent abnormality probabilities:

| Label | Description |
|---|---|
| ACL | Anterior cruciate ligament abnormality |
| MCL | Medial collateral ligament abnormality |
| Medial Meniscus | Medial meniscus abnormality |
| Lateral Meniscus | Lateral meniscus abnormality |
| Medial OA | Medial tibiofemoral osteoarthritis |
| Lateral OA | Lateral tibiofemoral osteoarthritis |
| PF OA | Patellofemoral osteoarthritis |
| Effusion | Joint effusion |
| Synovitis | Synovitis |
| Baker's | Baker or popliteal cyst |
| Contusion | Bone contusion |
| Fracture | Fracture |

This is a multilabel classification problem: one study may contain several positive
findings.

## Dataset summary

The local metadata contains:

- 4,407 training studies;
- 24,371 training MRI series;
- 819,078 training DICOM files;
- 58 studies with complete official binary labels;
- 4,349 studies with reports but no structured labels.

The full image audit found no missing studies, missing series, or unexpected series.

### Series distribution

| Anatomical plane | Series |
|---|---:|
| Sagittal | 9,864 |
| Coronal | 8,609 |
| Axial | 5,898 |

All 4,407 training studies contain Sagittal, Coronal, and Axial series. Preferred
fluid-sensitive fat-suppressed series are available in all three planes for 3,991
studies.

Each study contains 3-14 series, with a median of 5. Each series contains 11-320
slices, with a median of 30. The large range makes fixed-count uniform sampling more
practical than loading every slice.

### Supervision

Only 58 studies have complete human labels, so the project uses two supervision
sources:

1. Official labels with weight 8.0 in V02.
2. Fold-specific empirical-Bayes soft targets from multilingual report-rule states.

The report labeler distinguishes explicit positives, explicit negatives, and
unmentioned findings. For each fold, only its training gold rows calibrate these states
into soft targets and confidence weights. Unmentioned findings receive very low weight.
This is a baseline weak-label strategy, not a clinical-grade NLP system.

## Baseline architecture

```text
Radiology report
    -> multilingual weak-label rules
    -> target values and confidence weights

MRI study
    -> select one primary series per anatomical plane
    -> spatially sort DICOM slices
    -> uniformly sample center positions
    -> construct [n-gap, n, n+gap] 2.5D triplets
    -> shared EfficientNet-B0
    -> mean pooling within each plane
    -> concatenate three plane features and sequence metadata
    -> linear multilabel classification head
    -> 12 logits
```

The default image configuration is:

| Setting | Value |
|---|---:|
| Input size | 320 x 320 |
| Anatomical planes | 3 |
| Samples per plane | 6 |
| Triplet gap | 2 |
| Backbone | EfficientNet-B0 |
| Batch size | 1 |
| Gradient accumulation | 4 |
| Epochs | 4 |
| Default folds | Fold 0 only |

## Series selection

For each anatomical plane, the baseline uses the following priority:

1. `Fluid_Sensitive=1` and `Fat_Suppression=1`.
2. Another fluid-sensitive or fat-suppressed series.
3. Any remaining series in the same plane.
4. Within the same priority, prefer a slice count close to 32 to avoid unusually
   long 3D or high-resolution acquisitions.

A missing-plane mask is implemented even though all training studies contain all
three planes, making inference robust to hidden-test structural differences.

## DICOM preprocessing

The data pipeline:

1. Sorts slices using the projection of `ImagePositionPatient` onto the normal
   derived from `ImageOrientationPatient`.
2. Falls back to `InstanceNumber`, then to a deterministic filename order.
3. Applies `RescaleSlope` and `RescaleIntercept` when present.
4. Handles `MONOCHROME1` inversion and signed pixel data.
5. Uses the middle frame as a fallback for multi-frame DICOM files.
6. Jointly clips each triplet at the 1st and 99th percentiles.
7. Scales intensities to `[0, 1]`, resizes them, and applies ImageNet normalization.

Selected-series manifests and ordered DICOM paths are cached in the Kaggle working
directory so headers are not reread every epoch.

## Training and validation

- Splits are created at the `StudyInstanceUID` level.
- Iterative multilabel stratification is used when available.
- The fallback stratifies by gold-label status.
- Training uses confidence-weighted binary cross-entropy with soft weak targets.
- V02 does not use class `pos_weight`, avoiding the V01 overprediction failure mode.
- AMP, AdamW, gradient accumulation, cosine scheduling, clipping, and early stopping
  are enabled.
- Validation reports per-class ROC-AUC and log loss for all targets and separately
  for the gold subset.

The default notebook trains only fold 0 to verify the pipeline. For complete
five-fold training, change:

```python
cfg.folds_to_train = (0, 1, 2, 3, 4)
```

## Project structure

```text
RSNA_Knee_Abnormality_Detection/
|-- AGENTS.md
|-- README.md
|-- data/
|   |-- train.csv
|   |-- train_series.csv
|   |-- test.csv
|   |-- test_series.csv
|   `-- sample_submission.csv
|-- models/
|   |-- v01/
|   |   `-- v01_fold_0_best.pt
|   `-- v02/
|-- results/
|   |-- v01/
|   |   |-- oof_predictions.csv
|   |   |-- submission.csv
|   |   `-- weak_labels.csv
|   `-- v02/
|-- src/
|   |-- rsna-knee-submission.ipynb
|   |-- v01-rsna-knee-2p5d-baseline.ipynb  # completed V01 output
|   `-- v02-rsna-knee-2p5d-baseline.ipynb
`-- scripts/
    `-- inspect_kaggle_train_images.py
```

Local artifacts follow two strict rules:

- checkpoints belong under `models/vNN/` and include the version in the filename;
- non-model outputs belong under `results/vNN/` and should contain only artifacts
  needed for evaluation, analysis, submission, or later training.

Regenerable DICOM path caches, series-selection caches, and duplicate submissions are
not retained in `results/`.

## Running on Kaggle

1. Upload `src/v02-rsna-knee-2p5d-baseline.ipynb` to Kaggle.
2. Attach the competition dataset.
3. Select a GPU accelerator.
4. Provide pretrained EfficientNet-B0 weights through Internet access or a Kaggle
   Dataset and set `cfg.local_backbone_weights`.
5. Keep `cfg.folds_to_train = (0,)` for the first full run.
6. Run all cells and inspect DICOM preflight, series coverage, loss curves, metrics,
   and the generated submission.
7. If runtime protection triggers, save the Notebook output, attach it to a new run,
   and rerun; V02 automatically finds `v02_fold_0_last.pt` and resumes.

If pretrained weights cannot be loaded, the notebook falls back to random
initialization and prints a warning. Random initialization is supported for
reproducibility but is not recommended for the final model.

### Submission inference

Use the shared `src/rsna-knee-submission.ipynb` for submission-only inference. Set
`cfg.model_version` to the version being submitted, such as `v01` or `v02`, and
attach checkpoints named `<version>_fold_<fold>_best.pt`. The Notebook ensembles only
folds from the selected version. V01 and V02 are currently supported because they
share the same 3-plane 2.5D EfficientNet architecture.

V02 also runs test inference after completed training and writes
`/kaggle/working/submission.csv`. If runtime protection triggers, inference is skipped
until training is resumed and completed.

## Generated V02 artifacts

V02 writes the following files under `/kaggle/working/rsna_knee_v02/`:

- `weak_labels_v02.csv`;
- fold-specific rule calibration tables;
- selected-series manifests;
- ordered-path caches and ordering audit tables;
- `v02_fold_0_best.pt` with the best model weights;
- `v02_fold_0_last.pt` with full resumable training state;
- `oof_predictions_v02.csv` after completed validation;
- `submission_v02.csv` after completed inference.

The final submission is also written to `/kaggle/working/submission.csv`.

## Current validation status

- Full training image structure audit completed.
- CSV-to-image mapping validated with zero missing items.
- V02 Notebook contains 21 cells and 10 code cells.
- All code cells pass static compilation.
- The notebook is free of stored execution outputs.
- Notebook Markdown, comments, logs, and error messages are written in English.
- Full GPU training has not yet been completed in this local workspace.

## Main limitations

- Only 58 studies have complete gold labels.
- Rule-based report labels remain noisy and multilingual.
- The baseline uses one primary series per plane.
- Mean pooling may underweight small focal abnormalities.
- Gold-subset metrics are unstable because each fold contains very few gold studies.

The highest-priority next experiment is improving report-derived labels before
increasing model size or input complexity.
