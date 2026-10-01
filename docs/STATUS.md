# Project Status

> Agents: read this file first at the start of every session and update it before
> ending a session that changed project state. Keep it short; history belongs in
> `experiments.md` and `decisions.md`.

Last updated: 2026-10-01

## Current phase

**Phase 1 - Anchor reproduction.** Decision D-003: v05 is an unchanged reproduction of
`jiweiliu/rsna-knee-fast-2xt4-inference` v11 (public LB 0.943, all inputs public).
`notebooks/v05-public-stack-anchor.ipynb` is built and passes static validation; it has
not run on Kaggle yet. Improvement directions and reasons: `IMPROVEMENT_PLAN.md`.
Budget: 30 Kaggle GPU hours per week; goal: a medal.

## Best results

| Scope | Version | Public LB | Notes |
|---|---|---:|---|
| New line | - | - | Not started |
| Legacy (archived) | v03 | 0.664 | EfficientNet-B0 2.5D, 5 folds |
| Reference: best public notebook | - | 0.946 | pjmathematician d4-blend; uses private datasets, not reproducible |
| Reference: best reproducible public | - | 0.943 | Speedy Raptors lineage (jiweiliu v11) |
| Reference: leaderboard (2026-10-01) | - | 0.961 | #1; 0.957 at #10; 0.949 at #100; 1,001 teams >= 0.943 |

## Next steps

1. With user approval: push v05 to Kaggle (private, GPU T4 x2, the 18 public inputs from
   the source `kernel-metadata.json`), run it, and spend one submission to confirm 0.943
   and record the hidden-test runtime in `docs/experiments.md`.
2. Write the design note for v06 (our own 2.5D model, `IMPROVEMENT_PLAN.md` Priority 1)
   and discuss it before building; then build the cached slice dataset and run a single
   fold.
3. Entry and team-merger deadline is 2026-10-15: the account must have accepted the
   competition rules by then (a first submission confirms it).

## Open questions

- Which public notebook version produced each 0.943 score is not shown by Kaggle; the
  reproduction run will tell.
- Full hidden-test runtime of the public stack is unknown (needs one submission).
- Whether bf16 autocast in the stack's A5 stage costs AUC on T4.
- External knee MRI datasets: postponed by the user.

## Environment

- Local Python: conda env `kaggle` (Python 3.11) on PATH; recipe in `environment.yml`.
- Kaggle access: `KAGGLE_API_TOKEN` user environment variable (never print it); Kaggle
  CLI plus the `nvidia-kaggle` and `kaggle@shepsci` Claude Code plugins.
- Training and submission run on Kaggle GPUs only.
