# Project Status

> Agents: read this file first at the start of every session and update it before
> ending a session that changed project state. Keep it short; history belongs in
> `experiments.md` and `decisions.md`.

Last updated: 2026-10-02

## Current phase

**Phase 2 - Own model leg (v07 cache complete; v08 trainer built, Gate S next).** v05 (unchanged jiweiliu v11 public stack, D-003)
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

1. User to provide the billing inputs required before Gate S (design 5.1): v05
   hidden-test runtime (Kaggle submissions page) and this week's GPU quota used.
2. With user approval: push `notebooks/v08-convnext-tiny.ipynb` with `MODE = 'smoke'`
   (GPU T4 x2, internet on; inputs: v06 and v07 outputs) for Gate S. Built 2026-10-02;
   trainer tested locally on CPU (synthetic data, smoke and fold modes, metric and
   alignment unit checks); not run on a GPU yet.
3. After Gate S: recompute the budget (5.1), then fold 0 with both arms (Gate A0, Gate A).

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
