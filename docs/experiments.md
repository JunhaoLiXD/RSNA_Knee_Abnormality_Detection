# Experiment Log

Append one row per completed Kaggle run (training or submission). Never edit past rows
except to fill in a pending score. Use the version prefix that appears in the notebook
filename.

| Date | Version | Notebook | Base / change | Folds | CV (metric, scope) | Public LB | Kaggle run link | Notes |
|---|---|---|---|---|---|---:|---|---|
| 2026-10-02 | v08 | `notebooks/v08-convnext-tiny.ipynb` | ConvNeXt-tiny 2.5D, 320 px, 5 slots, soft 4-source targets; `auto` mode fold 0, K_train 4 vs 8 | fold 0 of 5 (scanner-grouped) | val macro AUC 0.871 (K_infer 16, 947 studies, soft target >= 0.5); gold-58 0.896 (CI 0.864-0.918) | - | https://www.kaggle.com/code/lingxd/v08-convnext-tiny (version 1) | K_train 4: 4.1 h, peak 5.8 GB, 67.5 img/s, data share 0.28; K_train 8 hit the 6 h limit (best epoch 8, K16 0.869) so 4 chosen (A0 table). Gate A: K4 0.850 / K8 0.868 / K16 0.871 / K24 0.872; K_infer 16 chosen (D-009). Gate B pass (min label MCL 0.788). Stage 2 not launched (4.3 h left < 4.7 h needed). Session 6.46 h |
| 2026-10-02 | v07 | `notebooks/v07-cache-320.ipynb` | Full 320 px JPEG cache, all 4,407 studies | - | - | - | https://www.kaggle.com/code/lingxd/v07-cache-320 (version 2) | 0 study errors, 0 slice decode errors; 14.56 GB; 61 min CPU; side from tag 2,200, geometry 2,131, unresolved 76 (1.7%); geometry agrees with the tag on 98.6% of 2,133 tagged studies. Output listing is large: download with `--page-size 200` and a file pattern |
| 2026-10-01 | v07 | `notebooks/v07-cache-320.ipynb` | Dry run of the 320 px JPEG cache (first 50 studies) | - | - | - | https://www.kaggle.com/code/lingxd/v07-cache-320 (version 1) | 0 errors; projected full cache 14.4 GB, 1.1 h CPU; 22.7 kB per slice, median 30 slices per slot; side from tag 26, geometry 23, unresolved 1; tag vs geometry agreement 26/26; previews checked: orientation consistent across L/R knees |
| 2026-10-01 | v06 | `notebooks/v06-dicom-audit.ipynb` | CPU audit of all training DICOMs, slot selection, targets, folds | 5 (scanner-grouped) | - | - | https://www.kaggle.com/code/lingxd/v06-dicom-audit (version 1) | All gates pass: 4,407/4,407 studies decode, 141,024 selected slices 0 errors, 24,371/24,371 series geometry-sorted; 45 fingerprint groups, coverage 94.7%; 56 min CPU |
| 2026-10-01 | v05 | `notebooks/v05-public-stack-anchor.ipynb` | Unchanged jiweiliu/rsna-knee-fast-2xt4-inference v11 (inference only) | - | - | 0.943 | https://www.kaggle.com/code/lingxd/v05-public-stack-anchor (version 1) | Reproduces the source score. Commit run 233 s on 3 placeholder studies, no failed arms; hidden-test scoring took more than 5 h (user report, 2026-10-02) |
| 2026-08-09 | v03 (legacy) | `archive/legacy/notebooks/v03-...` | EffNet-B0 2.5D + calibrated report weak labels | 5 | gold macro AUC 0.632 (58 studies) | 0.664 | - | Best result of the abandoned in-house line |
| 2026-08-06 | v01 (legacy) | `archive/legacy/notebooks/v01-...` | First EffNet-B0 2.5D baseline | 1 | - | 0.613 | - | Archived |
