# Final pair selection, 2026-10-22

- Date: 2026-10-22 (deadline 23:59 UTC); D-036, STATUS block 2h, lessons L51-L53.
- Question (user): which two submissions to select so that the pair is strong and the two hedge each other.
- Kaggle scores a team by the better of its two selected submissions on the private split; the public split is the only
  feedback we have. Public differences inside the 0.958 block are ~1e-4; the private-split uncertainty of a difference
  between two highly correlated entries is not quantified here (the earlier ~3e-3 figure was a rough guess, see review 1).

## Evidence

| Version | What it is | Public | Hidden order (rank crossing, >= 20 stable witnesses, 0 reverse) |
|---|---|---:|---|
| v68 | goodpjw2008 V25 copy (per-finding weights, A224 0.35, R6 flip, R224 mirror, tiny reader) | 0.958 | base |
| v80 | v68 with A224 0.25 | 0.958 | above v68 (+265) |
| v83/v84/v88 | v80 with A224 0.15 / 0.20 / 0.30 | 0.958 | none above v80 (0 / 0) |
| v86 | v80 + R7 0.2 | 0.958 | none above v80 (0 / 0) |
| v89 | v80 with Gaussian-rank fusion | 0.958 | above v80 (+43) |
| **v90** | v80 with z-logit fusion (R384 raw and R6 as standardised logits, R224 Gaussian rank) | 0.958 | **above v89 (+309); rank 444** |
| v91 | v80 with logistic-rank fusion | **error** | hidden-test run exceeded the runtime limit (no score); stage 3 differs from v80 only by a rank transform (seconds), so most likely runtime variance on a pipeline already near 9 h (v88 took ~9 h to score) |
| v94 | v90 with R224 probabilities as z-logit too | pending at 19:40 UTC | same pipeline as v90, also exposed to the runtime limit |
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

## Additional facts (2026-10-22 19:40 UTC)

- **The fusion gain is not specific to one stack.** z-logit lifted the per-finding stack (v80 -> v89 +43 -> v90 +309) and
  the uniform-weight stack (v87 0.957 -> v93 0.958, the first uniform entry to reach the 0.958 display). Two different weight
  settings moving the same way makes "public-specific" (risk 2) less likely than a single crossing would.
- **Runtime risk is settled for scored entries.** v91 errored on the runtime limit; v90 and v93 completed, and a code
  competition computes public and private scores in the same run, so a completed pick cannot time out later.
- v93 shows no crossing against v90 (0 / 0): no evidence that it is above v90 on public (not a proof that it is below).

## Recommendation

**A = v90 (ref 57510370), B = v93 (ref 57522487).** v94 replaces A only if it scores and crosses above v90 before the
deadline.

- A carries every public gain we have evidence for (A224 0.25 +265, fusion +43 +309).
- B differs from A in the per-finding weights, the one choice with sharp-optimum evidence of public fitting (L51), and adds
  R7 (a second compact training): if the weights were fitted to the public split, B is the pick that does not depend on
  them. B keeps the fusion gain, which now has support on two stacks, so the hedge no longer costs a display step.
- Not hedged: the fusion itself (both picks use z-logit). Hedging it would mean B = v87 (rank fusion), which gives up the
  gain on the uniform stack (0.957 vs 0.958) to protect against a risk the second stack's result makes less likely.
- Alternatives considered: v90 + v87 (hedges both risks, but B is weaker on every observable); v90 + v80 (hedges only the
  fusion, keeps the fitted weights in both); v90 + v89 (two near-identical stacks, little hedge).

## Review (Codex, GPT-6 Astra, effort high, read-only, 2026-10-22 ~20:00 UTC)

Codex re-ran the crossings (v89 43 / 0, v90 309 / 0, v93 0 / 0: equal to ours) and read the stage-3 code. Its pick:
**A = v90, B = v93, medium confidence**; second choice v90 + v87 if both risks must be covered.

| # | Finding | Verified | Disposition |
|---|---|---|---|
| 1 | 309 witnesses are not 309 independent validations; both stacks use the same public labels, so public selection bias is not excluded; "0 / 0 means v93 <= v90" is too strong; the ~3e-3 private noise figure is unsupported | Yes (reasoning; wording in this doc) | **Accepted**: wording corrected above. The direction of the recommendation does not change. |
| 2 | v93 (and v87, v82, v86) fallback defect: when R6 fails on a study, R7's fill of the compact side is overwritten by `b[our_fail] = rr[our_fail]`; if R384 and R6 both fail, the row gets 0.0 even when R7 scored it | Yes (`notebooks/v93-submit.ipynb` cell 16 blend loop) | **Accepted as a real defect, low impact**: it only touches studies R6 fails on (0 in every commit run, receipts PASS); such rows fall back to the Raptor side as in v90. It weakens the R7 part of the hedge on failed rows only and exists in v87 too, so it does not favour another B. Not fixable before the deadline (no slots). |
| 3 | +-14 logits are not a reason to reject z-logit: standardisation uses the whole test set (the private split is a subset scored from the same run), the mean shift is order-neutral and the logit temperature cancels in the sd; the real risk is a few over-confident errors and the sd changing with case mix | Yes (code: `zlogit_on` standardises over all non-failed test rows) | **Accepted**: the fusion risk is real but unquantified; rank fusion would hedge it at the cost of the observed gain. |
| 4 | v93 is a substantive hedge for the per-finding weights (Lateral OA / PF OA / Synovitis / Baker's 0.20 / 0.60 / 0.80 / 0.35 -> 0.50; R7 about 10 % of the pre-fusion weight), not for a common z-logit failure | Yes | **Accepted**; matches the "not hedged" line of the recommendation. |
| 5 | `pct(b)` keeps the fused order; Part B (reader at 0.003-0.035) re-ranks without undoing it; the both-failed centre 0.0 is not necessarily the median; the reader subprocess has no hard timeout (the 8.2 h check only gates its start), a plausible but unproven cause of v91's timeout; completed entries are unaffected | Yes | **Accepted**; no action (completed picks cannot time out). |
| 6 | Replace A by v94 only on a clean crossing that meets the >= 20 / 0 rule; do not select v90 + v94 together (no hedge); do not change scored code now | - | **Accepted**. |

**Final recommendation (after review): A = v90 (57510370), B = v93 (57522487).** If v94 scores before the deadline and
crosses above v90 by >= 20 stable witnesses with 0 reverse, A = v94 and B stays v93.
