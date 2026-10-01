# Project Status

> Agents: read this file first at the start of every session and update it before
> ending a session that changed project state. Keep it short; history belongs in
> `experiments.md` and `decisions.md`.

Last updated: 2026-10-01

## Current phase

**Phase 2 - Own model leg (design).** v05 (unchanged jiweiliu v11 public stack, D-003)
scored **0.943** public on 2026-10-01, reproducing the source. The design for our own
model leg is in `docs/research/v06-own-model-design.md` (revision 2 after Codex review:
v06 DICOM audit, v07 cache, v08 model, v09 blend) and awaits user approval (D-004)
before any GPU time.
Budget: 30 Kaggle GPU hours per week; goal: a medal.

## Best results

| Scope | Version | Public LB | Notes |
|---|---|---:|---|
| New line | v05 | 0.943 | Public stack anchor, inference only |
| Legacy (archived) | v03 | 0.664 | EfficientNet-B0 2.5D, 5 folds |
| Reference: best public notebook | - | 0.946 | pjmathematician d4-blend; uses private datasets, not reproducible |
| Reference: leaderboard (2026-10-01) | - | 0.961 | #1; 0.957 at #10; 0.949 at #100; 1,001 teams >= 0.943 |

## Next steps

1. User approval of design revision 2 (Codex findings and dispositions in its section 9);
   then commit.
2. Read the v05 hidden-test runtime from the Kaggle submissions page and record it in
   `docs/experiments.md`.
3. After approval: build `notebooks/v06-dicom-audit.ipynb` (CPU) and the public-corpus
   trainer smoke test.
4. Entry and team-merger deadline is 2026-10-15 (already satisfied by the v05
   submission).

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
