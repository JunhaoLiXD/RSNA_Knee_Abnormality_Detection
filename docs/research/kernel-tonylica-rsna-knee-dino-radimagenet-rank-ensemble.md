# RSNA Knee DINO-RadImageNet Rank Ensemble

- Source: https://www.kaggle.com/code/tonylica/rsna-knee-dino-radimagenet-rank-ensemble (version 11, pulled 2026-10-01)
- License: Apache 2.0 (shown on the Kaggle page)
- Public LB: 0.940 (as of 2026-10-01)
- Local copy: external/kernels/tonylica__rsna-knee-dino-radimagenet-rank-ensemble/

## What it is (verified in code)

A one-dataset consolidation of evgendvorkin's earlier public baseline (v15, 0.941). The
notebook itself is 176 lines: it verifies a SHA-256 manifest for every file in
`tonylica/rsna-knee-bend-dinov3-0917-repro-assets` (license "other", 84 files) and runs
four readable Python modules from that dataset: `transformer_rad.py`, `public_raptor.py`,
`residual_coat.py`, `blend.py`. We did not download the dataset, so the module code is not
verified.

Stated stack (author's text): 41 checkpoints -
20 DINOv2-small + 5 DINOv3-small (55/45 transformer blend), 10 RadImageNet heads,
3 Raptor CoAtNet checkpoints in 4 views (60/10/10/20), residual-gated CoAtNet epochs 4/6/8.
Per-target routing as in the 0.941 lineage. Crops: DINO 130 mm, Raptor 140 mm at
336-384 px, residual CoAt 130 mm. Requires offline 2 x T4.

## Value for us

- Cleanest engineering of the lineage: one pinned dataset and separate modules instead of a
  4,600-line notebook. A good model for how we package our own v05 assets.
- It is the only top notebook with DINOv3 members, which adds some diversity, but it lacks
  the D4 / Global96 / Repair-v1 CoAt readers and scores 0.003 below the 0.943 recipe.
