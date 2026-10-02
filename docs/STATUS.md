# Project Status

> Agents: read this file first at the start of every session and update it before
> ending a session that changed project state. Keep it short; history belongs in
> `experiments.md` and `decisions.md`.

Last updated: 2026-10-01

## Current phase

**Phase 2 - Own model leg (design rev. 3.3 approved as D-006; v07 cache built).** v05 (unchanged jiweiliu v11 public stack, D-003)
scored **0.943** public on 2026-10-01, reproducing the source. The design for our own
model leg is in `docs/research/v06-own-model-design.md` (revision 2 after Codex review:
v06 DICOM audit, v07 cache, v08 model, v09 blend), approved as D-005.
Budget: 30 Kaggle GPU hours per week; goal: a medal.

## Best results

| Scope | Version | Public LB | Notes |
|---|---|---:|---|
| New line | v05 | 0.943 | Public stack anchor, inference only |
| Legacy (archived) | v03 | 0.664 | EfficientNet-B0 2.5D, 5 folds |
| Reference: best public notebook | - | 0.946 | pjmathematician d4-blend; uses private datasets, not reproducible |
| Reference: leaderboard (2026-10-01) | - | 0.961 | #1; 0.957 at #10; 0.949 at #100; 1,001 teams >= 0.943 |

## Next steps

1. With user approval: run v07 in full (`DRY_RUN = False`; dry run passed 2026-10-01: projected 14.4 GB, 1.1 h CPU, orientation verified on previews).
   (50 studies) to measure cache size, time, side-inference agreement and look at the
   preview montages; then a full run with `DRY_RUN = False`. Built and validated
   2026-10-01; tested locally on the synthetic 12-study tree (orientation rules unit-tested
   for all planes and sides); not run on real data yet.
2. User to read from Kaggle before Gate S: v05 hidden-test runtime (submissions page) and
   this week's GPU quota used.
3. Gate S smoke-test notebook (design section 4.5).

## Open questions

- Test-set DICOM transfer syntaxes: training is 100% uncompressed; the Kaggle image's
  JPEG/JPEG 2000 decoders (Pillow, pylibjpeg) were not checked by v06.
- v05 hidden-test runtime: shown only on the Kaggle submissions page; not recorded yet.
- Whether bf16 autocast in the stack's A5 stage costs AUC on T4.
- External knee MRI datasets: postponed by the user.

## Environment

- Local Python: conda env `kaggle` (Python 3.11) on PATH; recipe in `environment.yml`.
- Kaggle access: `KAGGLE_API_TOKEN` user environment variable (never print it); Kaggle
  CLI plus the `nvidia-kaggle` and `kaggle@shepsci` Claude Code plugins.
- Training and submission run on Kaggle GPUs only.
