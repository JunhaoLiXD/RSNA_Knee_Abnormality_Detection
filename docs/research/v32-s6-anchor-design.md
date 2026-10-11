# v32-v33 design: the restored 0.954 public notebook as anchor (S6), then our leg on top

Status: revision 2 after the Codex review (section 6; all required changes accepted). Decision D-023. Evidence:
`public-landscape-2026-10-11.md`, STATUS L21, L22, L26-L29, D-019, D-021, D-022. User decision 2026-10-11:
"option 1 first, then look at option 2, after consulting Codex".

## 0. Summary

| Item | Version | GPU training | Kaggle | Rule (pre-registered) |
|---|---|---:|---|---|
| Reproduce heliosli/rsna-knee-blend-gold-dataset-restored (public 0.954) | `v32_submit` | 0 | commit run + 1 submission | component gates (section 2); the new best public submission if it scores above v27 |
| S6 and leg throughput on Kaggle (two T4, about 150 training studies as a mock test set) | `v34-s6-throughput` (diagnostic) | 0 | one run, about 1.5 GPU h | sets the leg's launch allowance for v33 |
| v32 + our v26 fold-0 leg at w 0.15 | `v33_submit` | 0 | commit run + 1 submission, only after v32 succeeds | adopted over v32 only if displayed higher or above v32 by the D-022 rank-crossing test; a tie keeps v32 |

v33 tests adding the fixed v27 leg to the new base (not the base change itself). No three-fold v33 follows
automatically.

## 1. What v32 runs (read in the code)

Source identity: the five code cells are identical across the restored notebook (version 3; the version history
shows "Diff +0 -0" for versions 2 and 3 against version 1, which scored 0.954), the earlier
`blend-mine-in-private-lb-luck-to-all-upvoters` and the matterhorn3838 copy (Codex, verified); the seven embedded
source hashes and eight `CODE_SHA` module hashes pass; `anatomy.pt` and `state_spec.json` match the manifest
(`manifest.json` SHA-256 `1c1211e64b73f1f6...`). Described as **source-identical to the available
0.954-associated pulls**; the historical image and input versions of the scored run are not recorded anywhere we
can read, and `geometry_bank.py`, `anatomy.py`, `anatomy_runtime.py` and the vendored MONAI are used but not in
`CODE_SHA`.

- Stage 1: the public 0949 CoAtNet notebook (our v17 cell 6 verbatim in `/tmp/raptor_run.py`, plus the
  checkpoint check and two marked changes: `raptor_sub.csv`, raw probabilities `raptor_raw.csv`), a subprocess
  with a 2 h timeout. Author's version-3 output `raptor_sub.csv` is byte-identical to our v17 `_sota_0949.csv`.
- Stage 2: S6 (four ConvNeXt-small fold models of `heliosli/rsna-knee-compact-v1`, bundle `209a32c8b50a6b1c`,
  hashes checked against the manifest), the author's mainline code, pinned wheels installed into the notebook
  environment (**timm 1.0.29 -> 1.0.25, pydicom 3.0.2 -> 3.0.1**, kernel log), knee anchors from `anatomy.pt`
  (SKM-TEA V-Net), a side classifier; two GPU workers with two loader processes each.
- Stage 3: per-finding percentile-rank blend, CoAtNet raw probabilities 0.7 + S6 0.3; a study one model failed
  on takes the other's rank.
- **Two fatal thresholds.** Stage 3 raises if more than 3% of studies fail in the CoAtNet; the S6 controller
  (`probe_dual.py`, `--max-fallback-fraction 0.03`) exits non-zero if more than 3% of studies are S6 fallbacks
  (39 of 1,300 allowed, 40 abort), and stage 2's cell then raises before stage 3. The S6 receipt says `PASS`
  whenever any study was scored, so it is not a success signal by itself (return code, worker exit codes,
  `timed_out` and counts are checked together).
- **The 8.3 h deadline is cooperative.** It is checked only after a loader item has been scored
  (`compact_infer.py` 466); the loader item timeout is 900 s and the stage-2 `subprocess.run` has no timeout.
  It does not bound the stage's end. The author's scored 0.954 therefore implies that S6 finished with at most
  3% fallbacks within Kaggle's limit, under the conditions of that run.

**Runtime (conditional estimates, not measured).** The placeholder timings are all first items of their loader
processes (cold imports and model set-up inside the "decode" timer); the 16 s second completion consumed a
prefetched item. Per study: classifier GPU 19.8 s, anchors about 2.1 s, decode 47.6 s and render 2.0 s on four
loaders. For about 1,300 studies on two T4: GPU work alone 3.6 h, with anchors about 4.0 h, preparation sustained
on four loaders with ideal overlap about 4.7 h; an effective 40 s per study per GPU gives 7.2 h, 50 s gives 9.0 h.
Planning estimate 4-5 h for S6 plus stage 1 and set-up. To keep 97% coverage before 8.3 h with a 0.5 h stage 1,
S6 needs about <= 44.5 s per study per GPU.

## 2. v32 - reproduction

Notebook: the author's cells unchanged (one mis-encoded markdown character in the credits restored to a middle
dot), plus our provenance and configuration cells first and a read-only receipt cell last. The receipt records
the hashes of the stage outputs, of every input file used (manifest, fold models, side model, state spec,
`anatomy.pt`, code archive, wheels), the S6 and blend receipts, and validates the submission format;
`submission.csv` is not modified. v32 accepts the upstream cooperative-deadline and abort-threshold behaviour as
part of an unchanged reproduction.

Commit-run gates (3 placeholder studies), all required before the submission; numerical parity on these studies,
not byte identity or hidden-test equivalence:
1. `raptor_sub.csv` byte-equal to v17's `_sota_0949.csv` and the author's output; `raptor_raw.csv` values equal
   to the author's after UID and column alignment (absolute tolerance 1e-6, rtol 0; `cudnn.benchmark` is on).
2. S6: controller and stage succeed, worker exit codes 0, not timed out, 3/3 scored, 0 fallbacks; `ours_sub.csv`
   equal to the author's within 2e-6 absolute (six-decimal output) with identical per-column ranks including ties.
3. `submission.csv` equal to the author's within 1e-6 absolute with identical ranks.
4. Input hashes equal the manifest and the author's run where recorded; submission columns, order, finiteness.
A tolerance is not loosened after a failure.

## 3. v34 throughput diagnostic and v33

**v34-s6-throughput** (before v33): the v32 stages 1-2 and the v27 leg, run on about 150 training studies
presented as a test set through a symlinked data directory in `/kaggle/temp` (no labels used, no submission);
measures S6 seconds per study per GPU after warm-up, the leg's wall time, memory, and the wheel effect on the leg
(reference and OAI checks under timm 1.0.25 / pydicom 3.0.1). Its numbers set the leg's launch allowance.

**v33**: v32's cells, then:
- The anchor (v32's `submission.csv`) is saved immediately after stage 3; every leg failure restores it and the
  notebook still completes successfully.
- The leg (v27's: v26 fold 0, two views, v19 checks: reference byte-equal, OOF at 1e-3, coverage >= 98%) runs
  **after stage 3** in the environment S6 left (validated by v34 and the commit run), two shards, process-group
  kill at an **absolute deadline of 8.6 h** from notebook start (24 min before Kaggle's 9 h). It is launched only
  if the time left before 8.6 h is at least the measured leg time times 1.5, and **at least 60 min** until
  measured; otherwise it is skipped (v33 = v32).
- Outer blend `rank(0.85 * rank(v32 output) + 0.15 * rank(leg))`, as v27.
- Commit-run gates: everything in section 2 for the anchor part, saved anchor equal to v32's commit-run output,
  `used_leg = true`, both shards done, full coverage, leg probabilities equal to v27's leg probabilities on the
  three placeholder studies within 1e-3 (direct, independent of final ranks: with three studies a 0.15 leg cannot
  reorder the anchor), blend recomputed locally. Local tests of the fallback paths (timeout, missing or failed
  shard, malformed output) and of the outer blend on a synthetic case large enough for ranks to change.
- A failed compatibility check on the hidden run is a valid fallback, but a commit run in which the leg fell back
  does not count as a test of v33.

## 4. Budget, comparators, picks, rules

- **Submissions (replaces D-022's list of further candidates):** v30 (submitted), v31, v32, v33; the optional
  qualifying B2 expansion and the fixed B1+B2 combination are dropped. D-022's training caps stand: neither a
  0.954 anchor nor a small v33 win renews fold funding.
- **Order and comparators:** v32 first. The rank-crossing test only shows a gain over the team's current best: once
  v32 is the best, v31 (v17-based) is judged by its displayed score only and cannot be compared with v27 in the
  hidden digits. Pending scores are resolved and a stable snapshot is taken before each submission; an
  unresolvable displayed tie keeps the incumbent.
- **Final picks (if v32 reproduces about 0.954):** the supported winner of v32/v33 plus v15 (non-OAI); v32 on an
  unresolved tie. v27 remains the alternative if the user prefers to avoid the SKM-TEA asset; it shares the OAI
  dependency. v15 separates from this anchor family but is no insurance against a team-level eligibility ruling.
- **Dependency risk:** per Kaggle's product clarification (discussion 131462), deleting a dataset after a completed
  synchronous rerun keeps the scores already generated; a later required rerun could fail. The used files are
  archived locally outside git (`external/datasets/`); no team-controlled Kaggle copy, because redistribution
  rights are not granted (licence not set / "other").
- **Rules (D-023, narrow):** accepted on top of D-019 (OAI CoAtNet): the SKM-TEA segmentation checkpoint
  `anatomy.pt`, the S6 fold models and side classifier (another participant's public models, rule 2.6.b; the
  manifest declares `gold_in_training 0`, not audited), and the author's code. Not used: OrthoFoundation `best.pt`,
  KneeXNet weights. KneeCoT stays prohibited. Host guidance favours click-through agreements but is not a ruling
  on SKM-TEA; the author's restoration is not host approval; the notebook's Apache 2.0 licence does not license
  the attached weights.

## 5. Risks

1. Rule risk (section 4). 2. Hidden S6 runtime above the abort threshold, or a hang past 9 h (cooperative
deadline); the author's scored run is the only evidence. 3. Dependency deletion before an exceptional rerun.
4. Public-LB selection among variants of one base (D-022 caps).

## 6. Codex review (GPT-6 Astra, high, read-only, 2026-10-11) and disposition

Verdict: v32 proceed with changes; v33 proceed with changes, conditional on v32. Findings checked in the source.

| # | Finding (severity) | Verified | Disposition |
|---|---|---|---|
| 1 | S6 aborts above 3% fallbacks (`probe_dual.py` 29, 155-157), not only CoAtNet; `PASS` is set when any study scored (high) | Yes | **Accepted**: both thresholds documented; success = return codes, exit codes, counts |
| 2 | Runtime estimate confused a prefetched study with throughput; cold timings in "decode" (high) | Yes (timer before set-up, all placeholder items first-of-loader) | **Accepted**: conditional estimates (4-5 h planning); v34 throughput diagnostic before v33 |
| 3 | 8.3 h is cooperative; no hard timeout in stage 2; "v33 never worse than v32" false (high) | Yes (`compact_infer.py` 466, item timeout 900 s, no subprocess timeout) | **Accepted**: leg after stage 3, saved anchor restored on any leg failure, 8.6 h absolute leg deadline, launch allowance >= 60 min until measured; v32 accepts the upstream behaviour |
| 4 | Source identity strongly supported, historical execution identity not established; some runtime modules unhashed (high) | Yes | **Accepted**: wording "source-identical to the available pulls"; the receipt records all input hashes |
| 5 | Three-study checks cannot show numerical equivalence or that the v33 leg contributes (0.15 cannot reorder three studies) (high) | Yes (recomputed: v27-leg blend ranks equal the anchor's) | **Accepted**: value-level gates with fixed tolerances; direct leg-probability parity with v27; synthetic outer-blend test |
| 6 | v33 tests adding the leg, not the base; submission budget exceeds D-022's list; rank crossing only against the current best (medium) | Yes | **Accepted**: v26 fold 0 for one v33 test; budget v30, v31, v32, v33; order and comparator rules in section 4 |
| 7 | Dataset deletion is a conditional rerun risk (high) | Yes (Kaggle clarification cited by Codex, not re-read) | **Accepted**: local archive; no redistribution; final-pick policy in section 4 |
| 8 | Accepting OAI does not accept SKM-TEA; public availability is not licensing (medium) | Yes | **Accepted**: D-023 narrow with the asset list |
