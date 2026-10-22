# Final pair selection, 2026-10-22

- Date: 2026-10-22 (deadline 23:59 UTC); D-036, STATUS block 2h, lessons L51-L53.
- Question (user): which two submissions to select so that the pair is strong and the two hedge each other.
- Kaggle scores a team by the better of its two selected submissions on the private split; the public split is the only
  feedback we have. Public differences inside the 0.958 block are ~1e-4; private noise is ~3e-3.

## Evidence

| Version | What it is | Public | Hidden order (rank crossing, >= 20 stable witnesses, 0 reverse) |
|---|---|---:|---|
| v68 | goodpjw2008 V25 copy (per-finding weights, A224 0.35, R6 flip, R224 mirror, tiny reader) | 0.958 | base |
| v80 | v68 with A224 0.25 | 0.958 | above v68 (+265) |
| v83/v84/v88 | v80 with A224 0.15 / 0.20 / 0.30 | 0.958 | none above v80 (0 / 0) |
| v86 | v80 + R7 0.2 | 0.958 | none above v80 (0 / 0) |
| v89 | v80 with Gaussian-rank fusion | 0.958 | above v80 (+43) |
| **v90** | v80 with z-logit fusion (R384 raw and R6 as standardised logits, R224 Gaussian rank) | 0.958 | **above v89 (+309); rank 444** |
| v91 | v80 with logistic-rank fusion | RESULT_V91 | RESULT_V91_X |
| v94 | v90 with R224 probabilities as z-logit too | RESULT_V94 | RESULT_V94_X |
| v71 / v85 / v87 | uniform Raptor weights (v87: + A224 0.25, R7 0.2) | 0.957 | not observable (below our best) |
| v93 | v87 with z-logit fusion (R7 z-logit too) | **0.958** | not above v90 (0 / 0, `22i` -> `22j`); first uniform-weight entry at 0.958 |

Every public recipe at >= 0.950 uses the same OAI CoAtNet (`public-landscape-2026-10-21.md`); the user declined a non-OAI hedge.

## What can go wrong on the private split, and what hedges it

1. **Per-finding Raptor weights are public-fitted** (L51: every +-0.05 move loses a display step; a sharp public optimum).
   Hedge: uniform weights (v87 family). Cost on public: one display step (0.957).
2. **The fusion gain is public-specific.** v89/v90 gained 43 + 309 witnesses on public; z-logit changes how much each model's
   confidence counts, and confident errors could cost on private. Hedge: one pick with rank fusion (v80/v87) and one with
   z-logit (v90/v93) — or both z-logit if we trust it.
3. **Run noise / tie at three decimals** is not hedgeable and is below private noise.

A pair hedges best when the two picks differ in the risks that are both plausible and not already priced into public.

## Candidate pairs

| Pair | Risk 1 (weights) | Risk 2 (fusion) | Comment |
|---|---|---|---|
| v90 + v93 | hedged (v93 uniform) | not hedged (both z-logit) | both carry the strongest public signal (+309) |
| v90 + v87 | hedged | hedged (v87 rank fusion) | two independent changes between the picks |
| v90 + v80 | not hedged | hedged | v80 = v90 without the fusion change only |
| v94 / v91 variants | as v90 | as v90 | only if they cross above v90 |

## Recommendation

PENDING the three results. Draft before results: A = v90 (or v94 if it crosses above v90), B = v93 if it scores normally.

## Review (Codex)

PENDING.
