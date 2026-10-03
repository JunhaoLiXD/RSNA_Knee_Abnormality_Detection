# Project Status

> Agents: read this file first at the start of every session and update it before
> ending a session that changed project state. Keep it short; history belongs in
> `experiments.md` and `decisions.md`.

Last updated: 2026-10-03

## Current phase

**Phase 2 - Own model leg (v08 5 folds trained: pooled OOF 0.840, gold ensemble 0.897; v09 next).** v05 (unchanged jiweiliu v11 public stack, D-003)
scored **0.943** public on 2026-10-01, reproducing the source. The design for our own
model leg is `docs/research/v06-own-model-design.md` revision 3.3 (D-006; Gate S on our
own cache, D-007): v06 audit and v07 cache are done (4,407 studies, 0 errors).
Budget: 30 Kaggle GPU hours per week; goal: a medal.

## Best results

| Scope | Version | Public LB | Notes |
|---|---|---:|---|
| New line | v05 | 0.943 | Public stack anchor, inference only |
| Legacy (archived) | v03 | 0.664 | EfficientNet-B0 2.5D, 5 folds |
| Reference: best public notebook | - | 0.946 | pjmathematician d4-blend; uses private datasets, not reproducible |
| Reference: leaderboard (2026-10-01) | - | 0.961 | #1; 0.957 at #10; 0.949 at #100; 1,001 teams >= 0.943 |

## Next steps

1. Get the fold-0 checkpoint (`v08_fold_0_k4_best.pt`) from v08 **version 1** output via
   the Kaggle web UI (CLI/API only serve the latest version); folds 1-4 are in
   `models/v08/v2/`.
2. With user approval: upload the five checkpoints as a private Kaggle dataset.
3. Build v09 (v05 anchor plus our 5-fold leg at K_infer 16, same preprocessing as v07 with
   a byte-equality check, blend 0.45 / 0.30 per design 4.6); validate on the 3 placeholder
   test studies before the first submission.

## Open questions

- Test-set DICOM transfer syntaxes: training is 100% uncompressed; the Kaggle image's
  JPEG/JPEG 2000 decoders (Pillow, pylibjpeg) were not checked by v06.
- Whether bf16 autocast in the stack's A5 stage costs AUC on T4.
- External knee MRI datasets: postponed by the user.

## Environment

- Local Python: conda env `kaggle` (Python 3.11) on PATH; recipe in `environment.yml`.
- Kaggle access: `KAGGLE_API_TOKEN` user environment variable (never print it); Kaggle
  CLI plus the `nvidia-kaggle` and `kaggle@shepsci` Claude Code plugins.
- Training and submission run on Kaggle GPUs only.
