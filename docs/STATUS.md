# Project Status

> Agents: read this file first at the start of every session and update it before
> ending a session that changed project state. Keep it short; history belongs in
> `experiments.md` and `decisions.md`.

Last updated: 2026-10-03

## Current phase

**Phase 2 - Own model leg (v09_submit submitted 2026-10-03, score pending).** v05 (unchanged jiweiliu v11 public stack, D-003)
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

1. When the user reports the v09_submit score: fill in `docs/experiments.md` and apply the
   pre-registered decision table (design 4.6): >= 0.945 accept the leg and submit w = 0.30
   once as the hedge; 0.944 or 0.943 submit w = 0.30 once; < 0.943 drop the leg.
2. Next improvement after that: OOF pseudo-label round for the weakest labels (MCL,
   Lateral OA, PF OA), per `IMPROVEMENT_PLAN.md` Priority 2 (needs a design note and Codex
   review before GPU time).

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
