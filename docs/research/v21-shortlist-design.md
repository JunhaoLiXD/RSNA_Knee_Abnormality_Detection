# v21-v25 design: the external-levers shortlist (E6, E1, E5, E4, E7)

Status: revision 2 after the Codex review (2026-10-09, section 10). The user approved the shortlist of
`external-levers-2026-10-09.md` section 4 and its order on 2026-10-09. Inputs: STATUS (L13-L22), v18
gold outputs, `scripts/gold_label_sources.py`, the synthetic benchmark (external-levers 2.4), and the
E5 Stage 0 measurement (section 4.1, inference only).

## 0. Summary

| Step | Option | Versions | GPU (local) | Kaggle | Rule (pre-registered) |
|---:|---|---|---:|---|---|
| 1 | E6: N replaces the public reader inside the v17 fusion | `v21_submit` (ensemble) | 0 | commit run + 1 submission | adoption over v19 at public >= 0.952 |
| 2 | E1: target T3 (Gemini table as fifth source), N recipe, fold 0 | `v22` training, `v22_submit` (fold-0 leg alone) | 2.5 h | commit run + 1 submission | compute allocation: T3 becomes the target of E5/E4 if public >= 0.935 (v14: 0.934); otherwise the round-2 target |
| 3 | E5: adapt the public OAI CoAtNet through the v07 adapter | `v23` training, `v25_submit` (ensemble, number reserved) | about 2 h | commit run + 1 submission | Stage 0 passed; submission only if the adapted model passes 4.3; adoption over v19 at >= 0.952 |
| 4 | E4: own CoAtNet-rmlp-2 (ImageNet-12k init, no OAI), fold 0 | `v24` training, `v24_submit` (fold-0 leg alone) | about 6.5 h | commit run + 1 submission | full CV (folds 1-4) only if public >= 0.937 and started by 2026-10-14 12:00 UTC |
| 5 | E7: mirror TTA for N | none | <= 0.5 h | none | optional diagnostic, off the critical path |

## 1. Common rules

- Order as above; GPU work runs one job at a time on the local RTX 3080 Ti (D-016). Kaggle is used for
  commit runs and scoring only; each push and submission is asked for.
- Three roles are kept apart (Codex finding 1): **screens** (gold-58, exploratory; it has been used
  for selection many times, L3/L13/L20), **compute allocation** (a fold-0 public score decides whether
  more GPU time goes into a direction; ties go to the default), and **final adoption** (a new entry
  replaces the incumbent pick only with a displayed public score at least 0.002 higher; 0.001 is a
  tie and keeps the incumbent).
- Every submission is listed here with its weights; no other variants are submitted from this design.
  A commit run that falls back (leg not used) blocks the submission.
- Final picks: the OAI pick is v19 unless an entry here reaches 0.952; the hedge is v15 unless a
  non-OAI entry reaches 0.946.
- Cutoffs (UTC): E4 full CV starts by 2026-10-14 12:00; large experiments stop 2026-10-19; 10-20 to
  10-22 are for final blends and selection.
- Version numbers follow D-017: a training version keeps its number for its leg-alone submission; a
  submission combining versions or the public base takes a new number (v21, and v25 reserved for E5).

## 2. E6 - `v21_submit`: N in place of the reader

**Composition** (built: `notebooks/v21-submit.ipynb`). v17's CoAtNet cells unchanged (they write the
CoAtNet-only `submission.csv` and `_sota_0949.csv`); the reader cells removed; the base is copied to
`v21_base_submission.csv` before the leg starts; the v19 leg cells unchanged apart from names (v13
arm-N 5 folds, K16, two shards, absolute deadline, reference and OOF checks); fusion per finding with
v17's weights TW: `final = rank((1 - TW_f) * rank(CoAtNet) + TW_f * rank(N))`, N = mean of the five
fold ranks. N's rank (`v21_leg_rank.csv`) and the scores before the final rank (`v21_fused_scores.csv`)
are saved. Docker image pinned to v17's (`2757e0c...`). On the hidden test, a leg that is not usable
(rule of v19) leaves the CoAtNet output alone.

**Evidence.** Gold (v19 design 1.2): CoAtNet + N with TW 0.9257 vs v17 0.9245 (+0.0013, CI -0.0012 to
+0.0039). N alone 0.936 on the LB vs the reader's 0.929; v19/v20 added N outside the fusion. Against:
L21; the reader is LB-measured; expected change below 0.002.

**Gates (commit run, 3 placeholder studies; all required before submitting).**
1. `v21_base_submission.csv` equals v17's commit-run `_sota_0949.csv` byte for byte.
2. `used_leg` true, coverage 1.0, checkpoint identities (v13, N, 0..4), reference check byte-equal,
   OOF check pass at 1e-3 for the five folds.
3. Recomputed locally from the downloaded base and `v21_leg_rank.csv` with the 12 TW values: the
   pre-rank scores equal `v21_fused_scores.csv` (<= 1e-12) and the final ranks equal `submission.csv`.
   On 3 studies the final ranks alone cannot reveal wrong weights (Codex finding 2), so the pre-rank
   comparison is the check; a local synthetic test (60 studies) shows the cell matches an independent
   TW implementation to 1e-16 and differs from a global weight of 0.162 by up to 0.17.

**Decision.** Adoption over v19 at public >= 0.952; 0.950-0.951 keeps v19; <= 0.949 rejects E6.

## 3. E1 - `v22`: target T3

**Target.** `T3 = 0.5 * soft5 + 0.5 * v11 OOF`, `soft5 = (n * soft4 + gemini) / (n + 1)` per cell, `n` =
the v06 source count (`<label>__n_sources`; 4 for every non-gold cell), `gemini` = `labels_v1_gemlow`
of `nartaa/rsna-knee-hpo-assets` (CC0; 4,349 unique non-gold rows, no missing or out-of-range values,
equal to `train_labels_v1`). Cell weights (`__weight`) and the v11 OOF teacher unchanged; gold never
trained on. Built: `notebooks/v22-n-gemini-target.ipynb` (v13 with only the target changed); the
local runner (`scripts/local_v13.py --version v22`) recomputes T3 independently before training
(dry run: max abs diff 1.1e-16).

**Evidence.** Gold, 2,000 paired resamples (`scripts/gold_label_sources.py`): soft4 0.8919 -> soft5
0.8956; round-2 target 0.9235 -> T3 **0.9270 (+0.0036, CI -0.0015 to +0.0089, P(<= 0) 0.081)**. On gold
the Gemini weight is 1/4 (3 sources there) against 1/5 in training, and the v11 part is the five-fold
teacher mean, not an OOF prediction. Author's text: a CoAtNet fold 0 trained on Gemini labels scored
gold 0.904 vs 0.888 on steven v4 labels. Against: the public CoAtNet trained on a Gemini-derived blend
(correlation with the base may rise); gold is reused.

**What it tests.** A candidate recipe (T3, trained locally) against v13 N fold 0 (Kaggle-trained;
val 0.899, gold 0.920, LB 0.934 as v14), not the causal effect of the label change: training is not
bit-identical across platforms (L19 covers inference only). A matched local control with the old
target is not run (section 10, finding 3).

**Submission.** `v22_submit` = the v14 notebook with the model list `[('v22', 'N', 0)]`, weights in a
new private dataset version, and the OOF reference study re-predicted against the **v22** fold-0 OOF
(the v13 values embedded in v14 are replaced). Checks as v14 (reference byte-equal, OOF at 1e-3,
metadata, coverage).

**Rule (compute allocation).** T3 becomes the target of E5 and E4 if `v22_submit` scores >= 0.935;
otherwise the round-2 target stays (a tie goes to the default). No gold override. v22 folds 1-4 are
not part of this design.

## 4. E5 - `v23` / `v25_submit`: adapting the public OAI CoAtNet

E5 is a **joint preprocessing-and-weight adaptation** (Codex finding 4): the checkpoint is fed from
our v07 cache, not from its own DICOM pipeline, and then fine-tuned. The public checkpoint (SHA-256
`7e5315dad125...`, verified) stays the incumbent until a frozen public comparison succeeds.

### 4.1 Stage 0 (done, inference only)

Adapter: the five v07 slots map to the public slots in order (SAG_FS, SAG_NFS, COR_FS, COR_OTHER,
AX_FS -> 26/22/18/12/18 slices); a slot whose series is already used (v07 duplicates) stays zero as
in the public selection; per slot the public picks `linspace(int(0.02 n), int(0.98 n) - 1, k)` are
mapped to the stored slice with the nearest original index (`raw_index`); our canonical flips are
undone (back to the DICOM pixel orientation); the centre 267 px of the 320 px slice (116.7 mm, the
public post-crop field) is resized to 320 px; the 96-slice volume, mask, K94 window centres (windows
cross slot borders as in the public code) and the anatomical mirror view (sagittal: the three
channels of each triplet reversed; coronal/axial: width flipped; on uint8 before normalisation)
follow the public code; `RaptorClassifier` loaded strictly; fp16. Intensity: 'as_is' (our 0.5-99.5
window) or 'restretch' (2-98 percentile of the slot's stored pixels re-mapped to 0-255).

| Gold-58 | Macro AUC | Mean / min per-finding Spearman vs v18 |
|---|---:|---:|
| v18 (exact public pipeline) | 0.9228 | - |
| adapter, as_is | 0.9235 | 0.978 / 0.965 |
| **adapter, restretch** | **0.9256** | **0.984 / 0.963** |

Known differences that remain (Codex finding 4): series choice differs from the public rule in many
studies (v07 ranks candidates and prefers fat-suppressed axial series), slices are the nearest stored
ones when a series has more than 32, the intensity window and JPEG q92, crop-then-upsample instead of
a native 384 raster, and the field of undersized images. **Gate S0 (strict, revision 2):** mean
Spearman >= 0.95, minimum per finding >= 0.90, gold not below v18 by more than 0.003: **passed** with
'restretch', chosen by fidelity to v18 (not by gold).

### 4.2 Stage 1 (adaptation)

- All 4,349 non-gold studies (the checkpoint saw all of them; held-out folds would not be honest).
- Loss = `0.5 * w_cell * BCE(z, T*) + 0.5 * BCE(z, p_base)`: T* = the target chosen by E1 with the v06
  cell weights; `p_base` = the untouched checkpoint's raw probabilities (eval mode, detached, K94,
  mirror-averaged, computed once through the adapter, about 51 min locally) with weight 1. The
  teacher term is a regulariser; whether it preserves what the checkpoint learned from OAI is a
  hypothesis (Codex finding 6), checked only through per-finding drift on gold and training studies.
- Fixed schedule: 3 epochs, AdamW, LR 1e-5 backbone / 1e-4 head, cosine, 16 random window centres
  per study, the mirror view as augmentation (p 0.5), fp16, gradient checkpointing, the public
  `RaptorClassifier`; the last epoch is used. The notebook (`notebooks/v23-...`) and its exact
  settings get a short Codex re-check before the run.

### 4.3 Admission and submission

- Gold, paired over the 58 studies, reported for three outputs: v18 exact, untouched through the
  adapter, adapted through the adapter. Submission only if the adapted model beats the untouched
  adapter by >= +0.003 with P(<= 0) <= 0.2, beats v18 exact (0.9228), and loses no finding by more
  than 0.02 against the untouched adapter. Otherwise E5 stops.
- `v25_submit`: v17 with the CoAtNet output replaced by the adapted model (v07 preprocessing from
  DICOM as in our leg, then the adapter), reader and TW unchanged. Weights in a private dataset; the
  checkpoint's terms ("research and educational use, including the RSNA Knee competition"; no OAI
  data rights) are recorded with it, and the weights are not published. Commit-run checks: strict
  load, adapter parity with the local Stage 0 volumes on the reference studies, reader fusion
  applied, measured runtime extrapolated to about 1,300 studies with margin under 9 h.
- Adoption over v19 at public >= 0.952.

## 5. E4 - `v24`: own CoAtNet (a controlled recipe comparison)

- The v22 trainer with arm C: `coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k` (timm, ImageNet-12k; weights
  downloaded once from the Hugging Face hub), `img_size=320`, gradient checkpointing, **BatchNorm in
  eval mode** (`bn_eval`, as arm E: frozen statistics, no double update under checkpoint
  recomputation, no single-study batch statistics), 1 study per micro-batch with 8 accumulation steps
  (2 does not fit; the per-micro-batch weight normalisation then differs slightly from N),
  `eval_batch_tokens` 40, everything else as N (v07 triplets, K_train 4, 15 epochs, LR 1e-4 / 3e-4,
  gated per-finding attention, K_infer 16). Target T* from E1.
- **Checkpoint contract** (Codex finding 7): backbone name, `timm_kwargs` (`img_size`), head,
  normalisation and input size are stored in the checkpoint's cfg and used by training, reload and
  the submission notebook; strict loading everywhere.
- Before the fold: the trainer's smoke mode on real data (optimizer steps, reload, one K16
  evaluation) with peak GPU memory and Windows commit measured at the intended worker count (6 is a
  ceiling, L19).
- **Rule (compute allocation):** `v24_submit` (fold-0 leg alone; new OOF reference values; parity at
  1e-3) >= 0.937 (N fold 0: 0.934) -> folds 1-4 (about 26 h), if they can start by 2026-10-14 12:00.
  Below 0.937 the full CV stops for budget reasons; that is not a finding that the model cannot help
  a blend (complementarity with v19 and v15 is reported). Blends with v24 get a frozen addendum.

## 6. E7 - mirror TTA for N (optional)

Only after the above, capped at 30 minutes: N's five folds on gold, plain K16 vs the mean of plain
and mirrored probabilities (mirror on uint8 triplets before normalisation; coronal/axial width flip,
sagittal channel reversal). Our cache canonicalises laterality and N was trained without flips, so
a loss is expected. Any gain is exploratory; using TTA in a submission would need its own decision.

## 7. Timeline (UTC)

| Day | Work |
|---|---|
| 10-09 | design rev 2; v21 commit run (ask); v22 fold 0 locally (2.5 h) |
| 10-10 | v21 and v22 submissions; v23 notebook, Codex re-check, teacher predictions and adaptation (about 2 h) |
| 10-11 | v25 (if admitted); v24 smoke and fold 0 (about 6.5 h) |
| 10-12 | v24 submission; E7 if time |
| 10-12 to 10-14 | E4 full CV starts by 10-14 12:00 if admitted |
| 10-15 | team-merger deadline (user) |
| 10-19 | stop large experiments |

## 8. Risks

1. Gold reuse and selection: gold is a screen; the public LB is the external check at 0.001-0.002 noise.
2. E1 platform confound; E5 has no honest validation and changes preprocessing and weights together.
3. E1 and E5 move our models towards the public base (Gemini-derived labels, self-distillation).
4. Windows commit limit for a CoAtNet trainer (L19); the stall watchdog stays on.
5. Time: E4's five folds take about 30 h of GPU and only fit if every gate passes on schedule.

## 9. Review questions (sent to Codex for revision 1)

Gates and thresholds; T3 and the fold-0 test; the Stage 0 adapter and gate, self-distillation; E4's
single-factor swap; what to drop or reorder.

## 10. Codex review (GPT-6 Astra, high, read-only, 2026-10-09) and disposition

Verdict: proceed with changes. Every finding was checked against the files and numbers.

| # | Finding (severity) | Verified | Disposition |
|---|---|---|---|
| 1 | Adoption at +0.001 (0.951, 0.935) contradicts the 0.001-tie rule; E1's gold override at a public tie (high) | Yes | **Accepted**: screens, compute allocation and adoption separated (section 1); adoption needs +0.002 (0.952); E1's 0.935 is a compute-allocation rule with ties to the default; gold override removed |
| 2 | On 3 placeholder studies TW fusion changes no rank, so a recomputed CSV cannot show the fusion ran; `_sota_0949.csv` is written by the removed fusion cell (high) | Partly: the rank invariance is right; the wiring claim is wrong (the CoAtNet cell writes `_sota_0949.csv`, line 594 of its source) | **Accepted** for the checks: pre-rank scores and N's rank saved and recomputed; synthetic test distinguishes TW from a global weight; `used_leg`, coverage 1.0 and all leg checks required; a commit-run fallback blocks the submission. Wiring: the base is copied explicitly before the leg (already so) |
| 3 | T3 correct; gold weights Gemini 1/4 vs 1/5 in training; script still used weight 0.2 and 1,000 resamples; prefer a matched local control (medium) | Yes (Codex reproduced 0.926997 vs 0.923458, P 0.0805) | **Accepted** except the control: the script now computes T3 exactly with 2,000 resamples; the gold caveats are stated; E1 is framed as a candidate-recipe test. **Control rejected**: 2.5 GPU h for a comparison on gold and fold-0 validation that cannot change the public-score rule of section 3 |
| 4 | The adapter is not a faithful substitute: series choice differs in 44% of studies, slice indices, windowing, crop-then-upsample, border windows, mirror axis (high) | The listed differences are real; Stage 0 (run after this review was requested) measures their effect: Spearman 0.984 (min 0.963) to the exact pipeline, gold 0.9256 vs 0.9228 | **Accepted in framing, rejected in conclusion**: E5 is called a joint preprocessing-and-weight adaptation, all differences are listed (4.1); the measured fidelity is high enough to continue. Duplicate slots are zero, original indices are mapped, sagittal mirroring reverses triplet channels, no second crop is applied |
| 5 | S0 (gold >= 0.915) plus +0.003 over the adapter could admit a model below the original (high) | Yes (0.918 example) | **Accepted**: strict S0 (mean Spearman >= 0.95, min >= 0.90, gold within 0.003 of v18), admission also requires beating v18 exact and no finding losing > 0.02; three outputs reported |
| 6 | Self-distillation is a regulariser, not demonstrated protection; 0.3 cell weights weaken the teacher term; specify the teacher (medium) | Yes (the mixed target equals weighted BCE terms) | **Accepted**: two loss terms, teacher term at weight 1, teacher fixed (eval, detached, K94, mirror), preservation stated as a hypothesis, drift tracked |
| 7 | v14 embeds v13 OOF references; the submission constructor ignores `img_size` (high) | Yes (v14 OOF reference values; constructor arguments) | **Accepted**: new OOF references for v22 and v24; a checkpoint contract for backbone kwargs used in training, reload and submission |
| 8 | E4 is not strictly single-factor (micro-batch 2 -> 1, BatchNorm); the memory probe precedes optimizer state; eval chunk 160 (medium) | Yes | **Accepted**: called a recipe comparison; `bn_eval`; smoke run with optimizer steps, reload, K16 evaluation, GPU and Windows commit measured; `eval_batch_tokens` 40 |
| 9 | 0.937 is a good compute gate but must not exclude the model from every blend (medium) | Yes | **Accepted**: below 0.937 only the full CV stops; complementarity reported; dated start cutoff |
| 10 | E5 needs licence evidence, a deployment plan, runtime budget and a reserved number (medium) | Partly: the README grants "research and educational use, including the RSNA Knee competition" and says nothing about derivative weights | **Accepted**: terms recorded, weights private and unpublished, deployment checks and runtime measurement listed, v25 reserved |
| 11 | E7 should be optional and off the critical path (low) | Yes | **Accepted** |

Order: Codex proposed E4 before an unresolved E5. Stage 0 resolved the main open point (fidelity),
so the user's order E6, E1, E5, E4, E7 stays.

## 11. Codex re-check of the v23 notebook before the adaptation run (2026-10-09)

Verdict: run after the listed fixes. All six findings verified in `notebooks/v23-coatnet-adapt.ipynb`
and fixed before the adapt run; the schedule itself was judged reasonable and kept.

| # | Finding (severity) | Disposition |
|---|---|---|
| 1 | The target term was divided by the weight sum, which cancels the 0.3 down-weighting and departs from 4.2 (high) | **Fixed**: `mean(w * BCE)` over the 12 cells; teacher term unweighted |
| 2 | Accumulation counted across epochs and dropped epoch tails (1,630 instead of 1,632 updates) (high) | **Fixed**: epoch-local groups, the tail flushed with its own size, an assertion on the step count; scaler-skipped steps recorded |
| 3 | Admission thresholded the bootstrap mean; a missing v18 silently removed a condition; invalid draws unguarded (high) | **Fixed**: the observed gold difference is gated; v18 and full 58-study coverage are required; 2,000 valid draws with an attempt cap |
| 4 | Torch RNG (dropout) not seeded (medium) | **Fixed**: Python, NumPy and Torch seeded; bitwise reproducibility not claimed |
| 5 | No probability drift on gold against the untouched model (medium) | **Fixed**: per-finding mean absolute difference and Spearman on gold and on 300 training studies (saved) |
| 6 | The teacher file was trusted by name; the cfg contract lacked normalisation and label order (medium) | **Fixed**: the teacher receipt must match the checkpoint hash, intensity and study count; normalisation and labels stored; strict cfg-driven reload tested after saving |

Runtime: the runner records the peak Windows commit charge; memory after the first optimizer step is
logged; 4 loader workers.

Result (2026-10-09): not admitted (adapted 0.9230 vs untouched 0.9255 on gold, -0.0025, CI -0.0088 to
+0.0035); E5 stopped (STATUS v23, L24).

## 12. E4 smoke failure and the BatchNorm change (2026-10-09)

The first v24 smoke run (revision 2 recipe, BatchNorm in eval mode as decided in section 10 finding 8)
produced a non-finite training loss after about 27 optimizer steps (micro-steps 250-300) and NaN
validation predictions. A step-by-step replication on 400 training studies located it:

| Check | Result |
|---|---|
| ImageNet-initialised backbone, fp16 vs fp32 forward on 20 studies (80 tokens each) | no non-finite output; feature max 18.7 |
| Training replication, BatchNorm frozen, LR 1e-4 (20 warm-up steps) | parameters finite throughout, but features in fp16 become NaN at step 27 (validation feature max 6 -> 32.5 between steps 20 and 25) |
| Same, lower backbone LR 3e-5 (smoke rerun) | training loss finite to micro-step 300, validation still NaN |
| Same, **BatchNorm in train mode**, LR 1e-4 | 50 steps stable; validation feature max 16 -> 3.7, no NaN |
| Pretrained BatchNorm running variance | as small as 2.0e-6 (`stages.1.blocks.*.norm2`), eps 1e-5 |

Cause: with frozen statistics, channels whose pretrained running variance is near zero are scaled by
about `1 / sqrt(1.2e-5)` = 290; once fine-tuning moves their inputs, activations exceed the fp16 range.
**Change:** arm C uses BatchNorm in train mode (timm's default for fine-tuning; batch statistics over
the 20 tokens of one study); the memory probe's random-input BatchNorm update is undone by restoring the
buffers. The double running-statistics update under checkpoint recomputation is accepted (it changes
the effective momentum, not the training-mode normalisation). Everything else in section 5 stays.

Three further smoke runs with BatchNorm in train mode trained normally (300 micro-steps, 53 img/s, data
share 0.11 with 2 workers) but stalled in the K16 validation pass and were stopped by the stall
watchdog (15, 15 and 45 min); Windows logged two GPU timeout resets (LiveKernelEvent 141) during those
passes, and the peak commit charge was 34.7-37.0 GB against a limit of 36.5 GB (32 GB RAM, a 4.8 GB
page file; the limit was 47.3 GB when L19 was written). The evaluation itself is fast in isolation (0.46 s
per study in the main process, 947 studies in about 7 min). **Change:** arm C evaluates in the main
process (`eval_workers` 0), so no worker processes are spawned on top of the trainer; training keeps 2
loader workers. A fifth smoke run still stalled with the GPU memory full about 8 minutes into the
evaluation phase, while a replication (40 training steps, then fp16 evaluation in the same process)
ran at 0.47 s per study with 6.8 GB reserved. The stall is in the smoke-only reload check, which runs
the model in **fp32** in chunks of 40 tokens: with the training cache still reserved this exceeds 12 GB
and Windows pages GPU memory to system memory. **Change:** that check runs in chunks of 8 tokens after
`torch.cuda.empty_cache()`. The fold run does not use this code path.
