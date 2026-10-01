# Project Status

> Agents: read this file first at the start of every session and update it before
> ending a session that changed project state. Keep it short; history belongs in
> `experiments.md` and `decisions.md`.

Last updated: 2026-10-01

## Current phase

**Phase 0 - Restart from public code.** The in-house V01-V04 line is archived (see
`decisions.md`, D-001). No active model version exists yet.

## Best results

| Scope | Version | Public LB | Notes |
|---|---|---:|---|
| New line | - | - | Not started |
| Legacy (archived) | v03 | 0.664 | EfficientNet-B0 2.5D, 5 folds |

## Next steps

1. Rank public notebooks for this competition by public LB score and votes; shortlist the
   top 5-8.
2. Pull the top candidates into `external/kernels/` and analyze them in
   `docs/research/`.
3. Write `docs/research/baseline-selection.md` with a comparison table and a
   recommendation; discuss with the user before building `notebooks/v05-...`.

## Open questions

- None yet.

## Environment

- Local Python: conda env `kaggle` (Python 3.11) on PATH; recipe in `environment.yml`.
- Kaggle access: `KAGGLE_API_TOKEN` user environment variable (never print it); Kaggle
  CLI plus the `nvidia-kaggle` and `kaggle@shepsci` Claude Code plugins.
- Training and submission run on Kaggle GPUs only.
