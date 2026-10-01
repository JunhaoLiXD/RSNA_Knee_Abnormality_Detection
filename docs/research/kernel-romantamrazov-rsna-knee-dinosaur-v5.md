# RSNA Knee | DINOsaur V5? (inference) and DINOsaur V5? train

- Source: https://www.kaggle.com/code/romantamrazov/rsna-knee-dinosaur-v5 (version 24, pulled 2026-10-01)
- Training notebook: https://www.kaggle.com/code/romantamrazov/rsna-knee-dinosaur-v5-train (page shows version 5 of 10; pulled 2026-10-01)
- License: Apache 2.0 (both, shown on the Kaggle pages)
- Public LB: 0.943 (as of 2026-10-01)
- Local copies: external/kernels/romantamrazov__rsna-knee-dinosaur-v5/,
  external/kernels/romantamrazov__rsna-knee-dinosaur-v5-train/

## Inference notebook

Base is versia-5 / Jiwei 0.943 (663-line diff to Jiwei). Author's stated change: add the
public `renta0426/rsna-knee-public0033-meniscus-bag-v1` specialist for **Medial Meniscus
only** (10% weight; 10% Transformer, 80% CoAt/Raptor hybrid), leaving the other 11
targets "byte-identical" to the 0.943 anchor, and writing safe/main/strong variants
(5/10/15%). The score did not move above 0.943. All 21 inputs are public (verified on the
page). Also attaches `tonylica/rsna-knee-bend-dinov3-0917-repro-assets`.

## Training notebook (verified in code, not run)

A "ConvNeXt diversity arm" trainer, one of the few public training notebooks in the
lineage:

- Backbone `convnext_tiny.fb_in22k_ft_in1k` (Kaggle model `ambrosm/convnext-tiny...`),
  224 px, 150 mm crop, up to 8 series per study, slices at quantiles
  (0.15, 0.325, 0.50, 0.675, 0.85).
- Labels: a consensus of whatever public report-label CSVs are attached (pilkwang,
  stevenleehans, lixin73 and others), kept soft and "gently sharpened"; the 58 gold studies
  are identified separately.
- Two stages: weak-label adaptation of the ConvNeXt on non-gold studies, then cached study
  features with a label-aware attention head (label embeddings + 2-layer transformer across
  labels). `StratifiedKFold` is imported; we did not verify the fold grouping.
- Run time: about 47 min on the visible run (from the kernel list).

## Value for us

The training notebook is a cheap, public template for a "diversity arm" in the same
spirit as the private legs that reach 0.945-0.946. The inference notebook shows that a
single-label specialist did not move the public score.
