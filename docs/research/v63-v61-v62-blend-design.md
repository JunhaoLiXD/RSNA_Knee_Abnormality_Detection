# v63 design: rank blend of the two verified recipes v61 and v62 (D-033)

Status: reviewed (independent Claude sub-agent; Codex CLI not installed, see section 7), revised, commit run pushed 2026-10-16. User asked (2026-10-16) to build and push without waiting for
v62's score, after a sub-agent review finds no blocker. Submission of v63 is held until v62 has scored (see section 6).

## 1. Question and evidence

Can the two strongest verified pipelines be combined? v61 (0.957, adopted, L44) and v62 (public 0.958 recipe reproduced
byte-equal; score pending) share the CoAtNet half (R384 cell identical, `raptor_sub.csv` SHA-256 equal in both runs) and differ in:

| Component | v61 | v62 |
|---|---|---|
| R224 (nartaa 224-px CoAtNet), 0.35 of the Raptor half | with anatomical mirror (L41) | without mirror |
| Compact ConvNeXt-small slot | R7 `8c7b666e` flip-TTA, 0.65 + S6F0 0.35 | R6 `fe055406` flip-TTA |
| Outer reader (goodpjw2008) | 0.10 | none |
| Raptor vs compact weight | 0.5 (OA findings 0.5) | per finding: Lateral OA 0.2, PF OA 0.6, Synovitis 0.8, Baker's 0.35, else 0.5 |

Most public 0.956-0.958 notebooks are re-weightings of the same components; averaging them is a weight change (v20, v21, v25,
v41: no gain, L28). v61 + v62 is different: R6 and R7 are different bundles never combined, and the reader helped on three
hosts (L33, L37). Risk evidence: same-lineage additions can do nothing (v55, L43) and a public model family can hurt (v49, L39).
v62's per-finding weights are the author's choice for R6 alone (selection method unknown).

## 2. Rule (fixed before any run, not tuned)

`mix = pct(0.5 * pct(v61_anchor) + 0.5 * pct(v62_recipe))`, then `final = pct(0.9 * pct(mix) + 0.1 * pct(reader))`, per finding,
ranks over all test studies (revised after review finding 1; the first draft averaged v61's final output, which halved the reader), where

- `v61_anchor` = v61's stage-3 output before the reader (`v47_base_submission.csv`), produced unchanged by every v61 cell;
- the reader enters at v61's 0.10 under v61's own use/fallback decision (cell 24); without it, `final = mix`;
- `v62_recipe` = v62's stage-3 formula, verbatim, on R384 (`raptor_raw.csv`), R224 (`raptor224_raw.csv`) and R6, with v62's
  failure rules (each model ranked over its own non-failed studies; a study one side failed on takes the other's rank).

Equal 0.5/0.5 is the only untuned choice between two recipes of similar displayed score. **One deviation:** the R224 input to
`v62_recipe` is v61's mirrored R224 (reused, not rerun). Reason: runtime; L41 found the mirror helpful on the same family.
Consequence: `v62_recipe` is not byte-equal to v62 on the hidden test; the parity test (section 5) uses v62's own R224 to
prove the formula, and a second test documents the mirror difference.

## 3. Build

`notebooks/v63-submit.ipynb` = v61's 25 cells byte-identical (asserted by the builder) + header/config edits + new cells:

1. **R6 setup**: v62's R6 asset cell (heliosli's compact worker set-up, only BUNDLE_ID/C_SLUG/FLIP_TTA differ from v61's R7
   cell) executed with `exec` in its own namespace, temp folder `probe_r6` (no R7 file, folder or global rebound). Any
   exception: R6 skipped.
2. **R6 launch**: same controller and arguments as v62's launch cell; output `ours_r6_sub.csv`, `r6_submission_receipt.json`,
   `r6_worker*_log.txt`; own process group, killed on every exit path.
3. **Final blend**: v62's stage-3 code as a function on the files above; the v63 rule (anchor mix, then the reader); validation; `v63_receipt.json`.
   `v61_submission.csv` keeps v61's output.

Input added: `heliosli/rsna-knee-r6-frozen-fe055406-w1` (as v62; the builder keeps v62's slug; fallback mirror
`rostigor/rsna-knee-r6-fe055406`, byte-equal manifest, if Kaggle refuses the dataset version).

## 4. Runtime and fallbacks (9 h hard limit)

The R6 stage runs last, after v61 has written its complete `submission.csv`, so any R6 problem leaves exactly v61:

- Launch only if `remaining to the cut-off >= 1.3 x R7 stage seconds measured in this run` (same worker, same flip-TTA, same
  studies; R6 crop 352 vs R7's) and at least 20 min. Cut-off = notebook elapsed 8.65 h; hard kill of the process group then.
- Controller `--deadline` = cut-off - 10 min (cooperative stop; a partial run counts as failed if over 3 % unscored).
- R6 not used (output = v61 byte-equal) if: skipped, killed, non-zero exit, malformed output, more than 3 % of studies
  unscored, mean per-finding Spearman of R6 with R7 below 0.5 (from 50 jointly scored studies), or any exception in the blend.
- Expected cost: v61 and v62 each scored in about 3.5 h (handover); R6 adds roughly v62's compact stage. Hidden runtimes of the
  individual stages were not recorded, so the guard is self-calibrating from this run's R7 time.

## 5. Checks before push (local)

- Builder: v61 cells byte-identical; v62 R6 cell text identical apart from the documented temp-folder line; validator passes.
- Parity: the final-blend function run on v62's run outputs (`results/v62/run1`: raptor_raw, raptor224_raw, ours_sub as R6)
  reproduces v62's `submission.csv` (max diff <= 1e-6); with v61's run outputs and v62's `ours_sub.csv` as R6 it yields a valid
  blend; with R6 missing the output equals v61's `submission.csv` byte for byte.
- Commit run (Kaggle, 3 studies): R6 receipt PASS, bundle `fe055406fad6a12f`, R6 output equal to v62's `ours_sub.csv`, v61 part
  equal to v61's run output, final recomputed offline.

## 6. Decision rule and submission order

- **Overridden by the user (D-034, 2026-10-16 03:46 UTC):** v63 was submitted before v62 scored (ref 57253670,
  before-snapshot `16b`); the conditions below were not applied.
- Submit v63 only after v62 has scored and its rank-crossing snapshot is taken, so the two results stay separable.
- **Pre-registered (review finding 2):** submit v63 only if v62 displays at least v61's score with 0 reverse crossings against
  the v61 snapshot. Otherwise the premise "two recipes of similar score" fails (v62's per-finding weights have an unknown,
  possibly leaderboard-fitted origin; L32, L42) and v63 is not submitted. Deadline: before the October 18 probe stop.
- Judge v63 against the incumbent at that time (v61, or v62 if adopted) by rank crossing: >= 20 stable witnesses, 0 reverse.
- One submission; no weight search. If v63 loses, the final pair falls back to the incumbent and the v15/v45 hedge.

## 7. Review

The Codex plugin could not run (Codex CLI not installed on this machine), so the D-004 Codex gate was replaced, at the user's
request for a sub-agent review, by an independent read-only Claude sub-agent (2026-10-16). Verdict: no blocker for a commit run.

| # | Finding (severity) | Decision |
|---|---|---|
| 1 | Recipe-level 0.5/0.5 halves the reader to about 0.05, untested (L33, L34, L37); R384/R224 are shared, so the new parts are R6 and v62's weights (medium) | **Accepted**: mix the pre-reader anchor with the v62 recipe, then the reader at 0.10 under v61's own decision |
| 2 | Pre-register what happens if v62 scores below v61 (medium) | **Accepted**: section 6 rule |
| 3 | Cooperative deadline checked per study (item up to 900 s); 14 min margin to 9 h; no wait after killpg (low) | **Accepted**: cut-off 8.65 h; `wait(60)` after the kill |
| 4 | Receipt/bookkeeping lines outside try (low) | **Accepted**: wrapped; submission restored to v61 on any blend error |
| 5 | R224 used whenever `R224_OK`, though v61's stage 3 can still reject it (low) | **Accepted**: gate on v61's `blend_receipt.json` `r224.used`; otherwise Raptor half = R384 (documented) |
| 6 | Re-running v62 cell 7: no conflict (separate temp folder, same wheels, prefixed logs) (low) | Noted; the commit run exercises the compile shapes |
| 7 | Mirrored R224 in the v62 recipe: no technical problem (low) | Noted |
| 8 | Spearman (>= 50 studies) and 3 % branches untested on 3 studies (low) | **Accepted**: synthetic 80-study tests (2.5 % used, 3.75 % fallback, uncorrelated, constant column, NaN) pass |
| 9 | Attach exactly the `-w1` R6 slug (low) | Done; the commit run's bundle check catches a wrong one |

Local checks after the revision: validator passes; v61 cells 2-24 byte-identical; v61's own final reproduces from anchor + reader
(diff 0.0); recipe parity with v62's submission 2.4e-8; full v63 recomputation 2e-8; notebook-path fallbacks restore v61 byte for byte.
