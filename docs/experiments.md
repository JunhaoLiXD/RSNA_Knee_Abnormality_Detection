# Experiment Log

Append one row per completed Kaggle run (training or submission). Never edit past rows
except to fill in a pending score. Use the version prefix that appears in the notebook
filename.

| Date | Version | Notebook | Base / change | Folds | CV (metric, scope) | Public LB | Kaggle run link | Notes |
|---|---|---|---|---|---|---:|---|---|
| 2026-10-01 | v06 | `notebooks/v06-dicom-audit.ipynb` | CPU audit of all training DICOMs, slot selection, targets, folds | 5 (scanner-grouped) | - | - | https://www.kaggle.com/code/lingxd/v06-dicom-audit (version 1) | All gates pass: 4,407/4,407 studies decode, 141,024 selected slices 0 errors, 24,371/24,371 series geometry-sorted; 45 fingerprint groups, coverage 94.7%; 56 min CPU |
| 2026-10-01 | v05 | `notebooks/v05-public-stack-anchor.ipynb` | Unchanged jiweiliu/rsna-knee-fast-2xt4-inference v11 (inference only) | - | - | 0.943 | https://www.kaggle.com/code/lingxd/v05-public-stack-anchor (version 1) | Reproduces the source score. Commit run 233 s on 3 placeholder studies, no failed arms; hidden-test runtime not recorded yet |
| 2026-08-09 | v03 (legacy) | `archive/legacy/notebooks/v03-...` | EffNet-B0 2.5D + calibrated report weak labels | 5 | gold macro AUC 0.632 (58 studies) | 0.664 | - | Best result of the abandoned in-house line |
| 2026-08-06 | v01 (legacy) | `archive/legacy/notebooks/v01-...` | First EffNet-B0 2.5D baseline | 1 | - | 0.613 | - | Archived |
