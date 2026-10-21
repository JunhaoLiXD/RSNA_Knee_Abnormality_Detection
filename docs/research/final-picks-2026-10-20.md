# Final-pick audit, October 20 EDT / October 21 00:31 UTC

Status: existing selections verified; no new submission or selection change. Await v84/v85 scores and the user's final confirmation.

## Verified state

Kaggle's selected-submission filter returns exactly two entries:

| Slot | Candidate | Submission ref | Public score | Rationale |
|---|---|---:|---:|---|
| A | v80 | 57427109 | 0.958, COMPLETE | Best supported incumbent: v68 with A224 0.25; 265 original stable positive witnesses, none reversed. |
| B | v71 | 57315112 | 0.957, COMPLETE | Main Raptor/R6 weights uniform at 0.5, reducing reliance on the public authors' per-finding vector. A224 0.35. |

The small outer reader still uses per-finding weights in both candidates: v71 is not entirely free of per-label choices.
Both share the OAI-trained Raptor checkpoints and R6/anchor/stackers; B hedges the main blend weighting, not external-data
eligibility, model-family or runtime risks. L51 motivates this hedge; it is not evidence of a better private score.

At the fresh snapshot, captured **2026-10-21 00:31:18 UTC**, rank is **742 of 6,298**, public 0.958.
Silver cut is 314 at 0.958; bronze cut is 629 at 0.958. We are outside the public medal positions; private medals remain unknown.

## Persistence and pending candidates

- v80: reconstructing the original `20d` -> `20e` witnesses yields 265. Of these, 154 still have unchanged submission
  count, last submission date, displayed score and membership. All 154 remain below us; zero reverse. Exclude the other
  111 rather than treating their new results as reversals. Persistence passes for the team incumbent; it does not recover
  an exact per-submission unrounded score.
- The original v61 witness set has zero unchanged survivors (37 excluded). No fresh v61 persistence conclusion is possible,
  and it has been superseded. Do not report zero reverse with zero survivors as confirmation.
- v84 ref **57451463** (A224 0.20) is still PENDING. v85 ref **57457762** (v71 hedge with A224 0.25) is still PENDING.
- Do not replace either selected candidate on pending output. v84/v85 overlap in scoring: preserve this snapshot and take
  a fresh one when a result is known. If both score before a separating snapshot, do not attribute crossings to one of them.
- A below-best displayed tie cannot establish that v85 beats v71: the team leaderboard retains the stronger 0.958 maximum.
  A possible hedge replacement would require a reasoned user decision rather than pretending a rank crossing identified it.

## Artifact audit and practical limits

The four local notebooks v80/v71/v84/v85 pass `scripts/validate_notebooks.py`. Local commit submissions match official
column order, IDs and probability constraints; R6 receipts PASS on 3/3 placeholder studies; no recorded base-component
failures. Their main blend weights and A224 match their descriptions. No source was modified.

An attempted read of the exact remote notebook version through the kernel-source API returned HTTP 403. Remote pinned
source parity was therefore not established in this audit. The selected refs/statuses were verified independently through
the supported submissions API. No hidden-test component receipts or private score were retrieved. Placeholder equality
(v80/v84 final CSVs equal; v71/v85 final CSVs equal) is not hidden-test equivalence.

Evidence and artifact hashes: `results/v80/final_audit_20261021T0031Z.json` (ignored local artifact).
Fresh leaderboard: `external/lb/2026-10-21T0032Z` (ignored; actual capture 00:31:18 UTC).

## Recommendation for the user's decision

Retain the already selected **v80 + v71** provisionally while v84/v85 finish. Discuss any substitution after results;
no selection changed in this audit. No new probes were launched. Final deadline: **2026-10-22 23:59 UTC**, which is
**October 22, 19:59 EDT**. Verify the agreed selection and completed status again before that deadline.
