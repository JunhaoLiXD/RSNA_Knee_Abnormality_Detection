# Design note: our own 2.5D model leg (v06-v09)

Date: 2026-10-01. Status: **revision 3.3** (cache and input sampling revised after the v06
audit and the second Codex review; training sampling and memory plan after the third;
hard budget, failure handling and token-count check after the fourth; per-session hard
stops, v09 budget gate and the non-comparable A0 branch after the fifth; section 9). Revision 2 was approved as D-005; revision 3
awaits Codex review and user approval. No GPU time is spent before approval.

Implements `IMPROVEMENT_PLAN.md` Priority 1 (own diverse model, rank-blended into the v05
anchor) together with the label part of Priority 2. Background:
`docs/research/baseline-selection.md`, `docs/research/discussion-key-findings.md`.

## 1. Goal and success criteria

- **Goal.** An independently trained image model that, rank-blended into the v05 anchor
  (public LB 0.943, verified 2026-10-01) with pre-registered weights, lifts the public LB
  to **>= 0.945**, and that has passed our own **scanner-grouped** validation, so the gain
  is not only a public-board effect.
- **Why this target.** `knee-s75-w50` reached 0.945 by adding a 5-fold ConvNeXt-tiny at
  **320 px with 24 adjacent-slice triplets per slot** (weak-label CV about 0.90; sampling
  read from its code, section 2.4) at weight 0.5; `d4-blend` reached 0.946
  with a private model group at 0.45 (both verified in code).
- **Not a goal.** The Efficiency Prize; external data (postponed by the user).

## 2. Evidence gathered (verified locally, 2026-10-01)

### 2.1 Label sources against the 58 gold studies

For information only. These numbers are **not** used to choose the label scheme
(section 4.3) because the same 58 studies are the only clean test set.

| Source | n | Macro AUC | 95% CI (bootstrap) |
|---|---:|---:|---|
| pilkwang `report_labels_v2` | 57 | 0.870 | 0.832-0.900 |
| stevenleehans `llm_labels_v2` | 58 | 0.887 | 0.850-0.918 |
| stevenleehans `llm_labels_v4_blend` (= v2 blended with lixin) | 58 | 0.893 | 0.856-0.924 |
| lixin73 `labels_llm_gpt56sol` | 58 | 0.835 | 0.804-0.864 |

All tables cap at about 0.89 and their confidence intervals overlap. Mean per-label
Spearman correlation between tables on the 4,349 non-gold studies is 0.71-0.83.

### 2.2 "Not addressed" is explicit in one table

pilkwang's table has a per-finding verdict YES / NO / UNK with a confidence. UNK (report
silent) is common: Synovitis 84%, Fracture 56%, Baker's 46%, Lateral OA 33%, Medial OA
26%; UNK cells have confidence about 0.05 versus 0.85-0.95 for YES/NO.

### 2.3 Data and header facts

- 4,407 training studies; all have sagittal, coronal and axial series; 3-14 series per
  study; 11-320 slices per series.
- `Fluid_Sensitive` == `Fat_Suppression` on every row (verified).
- Scanner fingerprint fields: the maverick notebook's EDA reads `Manufacturer`,
  `ManufacturerModelName` and `MagneticFieldStrength` from headers. Their actual coverage
  under the competition's 86-tag allowlist is **not verified**; the v06 audit measures it.
- Public precomputed training corpus: `dreaddevelopment/knee-raptor-corpus` + `-ext`, CC0,
  44 slices at 336 px per study; preprocessing code not published.
- v06 audit (full training set, 2026-10-01): every series is uncompressed, single-frame and
  geometry-sortable; median 30 slices per chosen series, median slice gap 3.5 mm; no chosen
  series has fewer than 11 slices; 25.5% of studies have a single coronal series; scanner
  fingerprints cover 94.7% of non-gold studies in 45 groups, so folds are scanner-grouped.
  Details in `docs/competition.md` and `docs/experiments.md`.

### 2.4 How the 0.945 private leg samples slices (verified in its decoded code)

`knee-s75-w50` embeds its inference script as base64; decoded locally:
- Per slot it stores up to 32 slices, `linspace(0, N-1, 32)` over the **whole** ordered
  series (all slices when N <= 32), cropped to 130 mm and stored as JPEG quality 92.
- The model input `320x24` means **24 centres per slot**, `linspace(0, n-1, 24)` over the
  stored stack, each expanded to the triplet (c-1, c, c+1) as the three channels. With
  N <= 32 these are truly adjacent raw slices. 4-5 slots per study.
- Test-time augmentation shifts the centres by fractional slice offsets.

So the verified recipe has both near-full coverage and true slice adjacency; revision 2's
"24 slices" reading of the checkpoint name was wrong.

## 3. Plan overview and versions

| Version | Notebook | Kaggle resources | Purpose |
|---|---|---|---|
| v06 | `v06-dicom-audit.ipynb` | CPU | Read-only audit of all training DICOM headers and codecs; scanner fingerprints; fold file |
| v07 | `v07-cache-320.ipynb` | CPU | Per-slot JPEG cache at 320 px built with the shared preprocessing function |
| v08 | `v08-convnext-tiny.ipynb` | GPU T4 x2 | Fold 0 with the coverage check (Gate A), then the remaining folds |
| v09 | `v09-anchor-plus-v08.ipynb` | GPU T4 x2, submissions | Explicit ensemble of v05 and v08 |

In parallel with v06/v07 (CPU), a short **trainer smoke test** on the public Raptor corpus
validates the training loop, loss and metrics and measures memory and throughput on the
final input shape (Gate S, about 0.5-1 GPU h). That model is never
submitted: its test-time preprocessing cannot be reproduced exactly.

## 4. Design

### 4.1 v06: DICOM audit (before any cache or training)

For every training series: decode success, transfer syntax, presence of `PixelSpacing`,
`ImagePositionPatient`, `ImageOrientationPatient`, slice count, obliquity, and the
fingerprint fields above. Output: per-study table, failure counts, fingerprint groups.

Pass thresholds for building the cache (pre-registered):
- at least 99.5% of studies yield all chosen slots without decode errors;
- at least 99% of chosen series have spacing and geometry for physical cropping and
  sorting (others fall back to `InstanceNumber` order and full-image resize, flagged);
- the slice-selection rule picks two different series for paired slots whenever the study
  has them (no duplicated fallback series where avoidable).

### 4.2 v07: training cache (shared preprocessing function)

- **Slots:** the five v06 slots (sagittal fluid-sensitive, sagittal non-fluid-sensitive,
  coronal fluid-sensitive, coronal other, axial fluid-sensitive) with the v06 series choice;
  a missing plane gives an empty, masked slot. A series used by two slots is stored once.
- **Slices per slot:** up to 32 slices at `linspace(0, N-1, 32)` rounded over the whole
  series after sorting by `ImagePositionPatient` projected on the slice normal (fallback
  `InstanceNumber`); all slices when N <= 32 (the median chosen series has 30). The v06
  `slice_files` column (8/6/8/4/6 sparse picks) is superseded.
- **Geometry and storage:** 140 mm centre crop using `PixelSpacing` (zero padding when the
  field of view is smaller), one percentile window per series, resized to **320 x 320**,
  stored as JPEG quality 92 per slice. Raw uint8 would be about 63 GB; JPEG is expected at
  about 10-15 GB (to be measured in the dry run). The test-time path applies the same JPEG
  encode/decode round trip so train and test pixels match.
- **Laterality:** one canonical medial/lateral orientation (in-plane flip for coronal and
  axial, slice-order reversal for sagittal), following the pilkwang method.
- **Size limit:** must fit the notebook output limit (believed 20 GB); checked in a
  50-study dry run before the full run.
- **Symmetry:** the exact same function is used later in v09 on test DICOMs; v09 checks
  that it reproduces the cached arrays byte-for-byte on a few training studies.

### 4.3 Targets (fixed a priori, not chosen on gold)

- **Soft target** = mean probability of the independent full-coverage public tables:
  pilkwang v2, stevenleehans v2, lixin73, dreaddevelopment soft labels. Derived blends
  (steven v4) are excluded to avoid double-counting. Missing cells are averaged over the
  available sources.
- **"Not addressed" handling:** per-cell loss weight 0.3 where pilkwang's verdict is UNK,
  1.0 otherwise (the report is silent, so the target is a prior, not evidence).
- Soft BCE, no rounding.
- The 58 gold studies are never trained on.
- Out-of-fold pseudo-label mixing is the next step after v08, not part of it.

### 4.4 Model

- ConvNeXt-tiny (`convnext_tiny.fb_in22k_ft_in1k`, timm, ImageNet weights).
- **Input unit:** a triplet (c-1, c, c+1) of consecutive stored slices of one slot as the
  three channels, clamped at the series ends. Because the store keeps (almost) every raw
  slice, the triplet is anatomically adjacent.
- **Training centres (covering sampler):** each slot's stored stack is split into
  `K_train` equal bins and one centre is drawn uniformly inside each bin per step, so every
  step spans the whole series and every stored position is reachable. `K_train` is 4 or 8,
  chosen by Gate A0 (section 4.5). The training log records, per epoch, the fraction of
  stored positions used as a centre at least once.
- **Evaluation and inference centres:** `K_infer` evenly spaced centres per slot (Gate A).
- Features of every triplet plus a slot embedding; per-finding attention pooling over all
  triplets of the study; 12 logits.
- Training: AdamW, lr 2e-4 head / 5e-5 backbone, cosine with 1 warm-up epoch, 10 epochs,
  fp16 autocast (T4 has no native bf16), light augmentation (scale/crop, small rotation,
  intensity jitter; no left/right flip). Checkpoints `v08_fold_<k>_best.pt`.
- **Memory plan:** effective batch of 8 studies built by gradient accumulation over
  micro-batches of 2 studies (`K_train = 4`: 40 images of 320 px per micro-batch) or 1
  study (`K_train = 8`: 40 images). If 40 images do not fit, the backbone uses activation
  checkpointing before the micro-batch is reduced further. Peak memory and throughput are
  measured in the smoke test (section 4.5) before any fold is trained.

### 4.5 Validation and gates (pre-registered)

**Folds.** 5 folds over the 4,349 non-gold studies, at `StudyInstanceUID` level:
- If the audit finds a fingerprint (manufacturer + model + field strength) for at least 90%
  of studies, with at least 10 groups and no group above 40% of studies: multilabel-
  stratified **grouped** folds by fingerprint (a scanner never appears in both train and
  validation).
- Otherwise: multilabel-stratified random folds, plus a held-out report of AUC on studies
  whose fingerprint is rare (< 1% of studies) as the cross-site proxy.

**Metric for all decisions:** validation macro AUC against the soft target rounded at
0.5, plus per-label AUCs. The 58 gold studies are reported for every configuration with a
bootstrap CI, but used only as a bug detector (macro AUC < 0.80 means investigate), never
to choose between configurations.

**Gate S - smoke test (before fold 0).** On the public Raptor corpus (resized to 320 px)
with the **final** model, input shape (5 slots x `K_train` centres x 320 px), micro-batch
and accumulation, for both `K_train` = 4 and 8: run about 300 training steps and one full
validation pass on one fold. Record peak GPU memory, training images/s, validation time,
and data-loading time. Pass if peak memory stays below 14 GB and the projected fold time
(10 epochs plus validation) is at most 4 h for `K_train = 4`. The budget in section 5 is
recomputed from these numbers (section 5.1). The user reads the Kaggle GPU quota before and
after the Gate S session, which settles whether a two-GPU session is billed by session
time. JPEG decoding cost of our own cache is measured again in the first epoch of fold 0
(section 5.1, checkpoint 2).

**Gate A0 - training coverage (fold 0, `K_train` 4 vs 8, in parallel on the two T4s).**
Identical in everything else; both evaluated with `K_infer = 16`. Choose `K_train = 8` if
its macro AUC is at least 0.003 higher, or if any of ACL, MCL, Medial or Lateral Meniscus
is at least 0.01 higher without a lower macro AUC; otherwise choose 4 (half the cost). If
Gate S shows that `K_train = 8` cannot finish a fold within 5 h, only 4 is trained and the
coverage risk is recorded as untested. Running both on the two GPUs of one session is
expected to cost little extra quota (verified at Gate S).

Comparability: the two arms are compared only if both finish all epochs with the same
seed, fold, study order, augmentation seed and evaluation code, and produce finite
validation predictions. Timing is not compared (the arms share the CPU).

| A0 outcome | Action |
|---|---|
| Both arms comparable | Apply the selection rule above. |
| Arm 8 fails (OOM, NaN, crash) or exceeds 5 h projected after epoch 1 | Stop arm 8; choose 4; record training coverage as untested. No retry of arm 8. |
| Arm 4 fails, arm 8 comparable and its fold time <= 5 h | Choose 8. |
| Arm 4 fails and arm 8 fails or is too slow | One retry of arm 4 alone after fixing the cause, counted against the budget. A second failure fails the gate: stop GPU work and revise the design. |
| Arm 4 projected above 4.5 h after epoch 1 | Apply the next degradation step (section 5.1) before continuing. |
| Both arms finish with finite predictions but the comparability conditions are broken (seed, order, augmentation or evaluation mismatch) | AUCs are not used for selection. If the cause is an identified configuration error, rerun only the affected arm once with the fix (if both are affected, rerun arm 4 only and choose 4). If the cause is unknown, treat the affected arm as failed and apply the rows above. All reruns count against the budget. |

**Token-count check (inside Gate A, inference only).** With 5 slots the token count is
5 x `K`: training sees 20 tokens (`K_train = 4`) or 40 (`K_train = 8`). Gate A therefore
also evaluates `K_infer = K_train` (matched token count) and reports, per finding, the
difference between matched and each unmatched setting. A drop of more than 0.005 macro AUC
from matched to unmatched settings counts as a token-shift problem: the selected
`K_infer` is then restricted to the matched value.

**Gate A - inference coverage (fold 0, no extra training).** Evaluate the chosen fold-0 model with
`K_infer` in {`K_train`, 8, 16, 24} centres per slot. Choose the smallest `K_infer` whose macro AUC is
within 0.002 of the best and whose ACL, MCL, Medial and Lateral Meniscus AUCs are each
within 0.005 of the best. This measures how much coverage the lesion-sensitive findings
need without spending training GPU time. Resolution is fixed at 320 px (the verified
recipe); the 224 px ablation of revision 2 is dropped.

**Gate B - continue to 5 folds.** On fold 0: macro AUC >= 0.86 (the public 0.945 leg had
about 0.90 on random folds; grouped folds are expected to be lower), Medial and Lateral
Meniscus each >= 0.80, and no label below 0.65. If grouped folds are used and the gate
fails, check whether the failure is concentrated in one scanner group before deciding.

### 4.6 Blend and submission decision table (pre-registered)

`blend(w) = rank((1 - w) * rank(anchor) + w * rank(ours))` per finding. Two weights are
pre-registered: **w = 0.45** (primary, from the two public examples) and **w = 0.30**
(conservative). Our ability to estimate the right weight locally is nil (section 7.3).

| First submission: blend(0.45) | Action |
|---|---|
| >= 0.945 | Leg accepted. Submit blend(0.30) once for the hedge. |
| 0.944 | Submit blend(0.30) once. Leg accepted if either >= 0.944; move to pseudo-labels. |
| 0.943 | No measurable gain. Submit blend(0.30) once; if also <= 0.943, leg is dropped from final picks and GPU goes to label work (Priority 2). |
| < 0.943 | Leg dropped; design revisited. |

**Final two selections (by 2026-10-22):** (1) the highest-scoring accepted blend;
(2) the conservative accepted blend at the lower weight, or v05 anchor-only if no blend was
accepted. No further weight search on the public board.

## 5. GPU and runtime budget

| Item | Estimate | Basis |
|---|---|---|
| v06 audit, v07 cache | 0 GPU h | CPU notebooks |
| Gate S smoke test on public corpus | about 0.5-1 GPU h | both `K_train` settings, about 300 steps each, plus one validation pass |
| Fold 0, `K_train` 4 and 8 in parallel (Gate A0) | about 2.5-5 GPU h of session time | the `K_train = 8` run sets the session length; unmeasured until Gate S |
| Gate A (K_infer 8/16/24 on fold-0 validation) | under 0.5 GPU h | inference only |
| Remaining 4 folds, two in parallel | about 5 GPU h | 2 sessions of about 2.5 h |
| v09 submissions | 2-3 runs | anchor runtime plus about 20-30 min for our leg (1,300 studies x 5 slots x K_infer x 5 folds) |

Total about 9-14 GPU hours depending on Gate S and Gate A0: under half of one week's
quota. These numbers are placeholders until Gate S; the table is rewritten with measured
throughput before fold 0 starts.

### 5.1 Hard budget and stop rules

**Cap.** This design may consume at most **18 GPU hours** (quota units as billed) up to and
including the first v09 submission, leaving at least 12 hours of the week for Priority 2
and contingencies.

**Billing inputs, recorded before Gate S** (the user reads them from Kaggle): the v05
hidden-test runtime from the submissions page, and the week's GPU quota used so far. Up to
now the only GPU run was the v05 commit run (about 5 minutes); v06 ran on CPU. A quota
reading well above that therefore shows that the hidden-test rerun of a submission is
billed. The v09 cost in the projection is then: the v09 commit run, plus the hidden-test
rerun (the v05 runtime plus the measured cost of our leg) only if reruns are billed.

**Projection.** `P = spent + 1.2 x (remaining planned items)`, where the remaining items
are the Gate A0 session, the remaining 4 folds, Gate A evaluation and the v09 cost defined
above, each from measured throughput; 1.2 is the safety margin.

**Per-session hard stop.** Every GPU session is a checkpoint. Before launch:
`remaining_cap = 18 - spent`, and the session's time limit is
`min(1.3 x its projected duration, remaining_cap)`; the session is not launched if its
projected duration exceeds `remaining_cap`. Every GPU notebook reads this limit from its
configuration cell, checks elapsed time after every training step, and when the limit is
reached saves the last checkpoint and its state, writes a receipt saying it stopped
early, and exits cleanly. A session stopped this way triggers a recomputation of `P` and
the degradation order before anything else is launched.

**Checkpoints** (in addition to the per-session rule).
1. After Gate S, before Gate A0 starts: proceed only if `P <= 18`.
2. After epoch 1 of fold 0 (first measurement on our own JPEG cache): recompute `P` and
   the per-arm fold projection; apply the A0 table above.
3. Before each batch of remaining folds: recompute `P` with the chosen `K_train`.
4. **Before v09 (pre-submission gate):** the first v09 submission is launched only if
   `spent + v09 cost <= 18`. If not, the fallback is to submit with our leg's inference
   reduced (`K_infer` 8 and the 3 best folds) and re-check; if still above the cap, the
   submission waits for the next weekly quota.

**Degradation order** when `P > 18` at any checkpoint, applied one step at a time until
`P <= 18`:
1. Drop the `K_train = 8` arm (A0 becomes a single arm; coverage recorded as untested).
2. Reduce epochs from 10 to 7 for all folds not yet started.
3. Cap `K_infer` at 16.
4. Train 3 folds instead of 5 (the leg then averages 3 fold models).
5. If still above the cap: stop GPU work and revise the design.

The v05 hidden-test runtime is therefore an input to the projection from Gate S onward
(revision 3.3 withdraws the earlier position that it was needed only before v09). Estimates are unmeasured; the
smoke test and fold 0 calibrate them. Whether quota counts session time rather than
GPU-time is unverified. The v05 hidden-test runtime is still to be read from the Kaggle
submissions page and fixes the inference budget for v09.

## 6. Timeline

| Dates | Work |
|---|---|
| 10-02 to 10-03 | v06 audit, v07 cache dry run and full run, trainer smoke test |
| 10-04 to 10-06 | Fold 0, Gate A and Gate B |
| 10-07 to 10-09 | Remaining folds; v09 submissions per the decision table |
| 10-10 onward | OOF pseudo-label round (Priority 2) if the leg is accepted |

## 7. Risks and open questions

1. **Train/test asymmetry** in our preprocessing: one shared function and a byte-equality
   check in v09.
2. **Label ceiling** of about 0.89 on gold for every public table; addressed next by OOF
   pseudo-labels.
3. **Blend weight cannot be estimated locally:** the anchor's checkpoints were trained on
   the training studies, so any local comparison with them is in-fold, and there is no
   independent proxy model on hand. Hence two pre-registered weights and a decision table
   instead of tuning.
4. **Gold-58 noise:** only a bug detector.
5. **Runtime:** anchor plus our leg must stay under 9 hours on the hidden set.
6. **Fingerprint coverage** may be too low for grouped folds; the fallback rule in 4.5
   applies.
7. **Adjacency for long series** (v07 dry run): 29% of stored series have more than 32
   slices; most only slightly (up to about 41, stride about 1.3), but 3D acquisitions with
   up to 320 thin slices are stored at a stride of about 10 slices, so their triplets are
   not raw-adjacent (the physical gap stays small because such slices are thin).

## 8. Changes

### Revision 3.3 (after the fifth Codex review)

- Per-session hard stop: launch condition, time limit, in-notebook time check with clean
  exit, and recomputation after an early stop.
- Billing inputs (v05 hidden-test runtime, week's quota used) recorded before Gate S; a
  v09 pre-submission budget gate with a reduced-inference fallback.
- Gate A0: branch for arms that finish but are not comparable.

### Revision 3.2 (after the fourth Codex review)

- Hard budget (5.1): an 18 GPU-hour cap with a projection formula, three checkpoints and a
  fixed degradation order.
- Gate A0 failure and comparability table.
- Token-count check: Gate A also evaluates `K_infer = K_train`; the previous rebuttal
  about token counts is withdrawn.
- Quota billing for two-GPU sessions is observed at Gate S.

### Revision 3.1 (after the third Codex review)

- Training centres: fixed 4 jittered centres -> covering sampler (one centre per equal
  bin) with `K_train` 4 or 8 chosen by a fold-0 training ablation (Gate A0); per-epoch
  centre-coverage logging.
- Memory plan: micro-batching with gradient accumulation, activation checkpointing as the
  fallback; batch of 8 studies is now the effective batch.
- Gate S: smoke test on the final input shape with measured memory and throughput; the
  GPU budget is recomputed from it and again after the first epoch of fold 0.

### Revision 3 (after the v06 audit and the second Codex review)

- Cache: 32 sparse slices per study -> up to 32 slices per slot over the whole series
  (all slices for typical series), stored as JPEG at 320 px, following the verified 0.945
  leg (section 2.4).
- Input: triplets are consecutive stored slices, so they are truly adjacent; centres are
  sampled per slot (training 4 per slot with jitter, inference `K_infer`).
- Gate A: 224/320 resolution ablation -> inference-only `K_infer` coverage check with
  per-lesion criteria; resolution fixed at 320 px.
- Corrected the revision-2 reading of "320x24" (24 triplet centres per slot, not 24 slices
  per study).

### Revision 2 (after the first Codex review)

- 224 px -> 320 px primary, with a 224 px ablation from the same cache.
- 60 slices -> 32 slices per study (superseded in revision 3).
- Single label source chosen on gold -> a priori multi-source mean with UNK down-weighting.
- Gold-58 removed from all gates; decisions use grouped-fold validation.
- Random folds -> scanner-grouped folds when the audit allows, with an explicit fallback.
- Added a full DICOM audit (v06) with pass thresholds before the cache.
- Added the public-corpus trainer smoke test (not submitted).
- Single blend gate with an undefined 0.943-0.945 zone -> complete decision table with two
  pre-registered weights and final-selection rules.
- Versions renumbered: v06 audit, v07 cache, v08 model, v09 blend.

## 9. Codex review (revision 1, 2026-10-01) and disposition

Codex adversarial review verdict: needs-attention. Each finding was checked against the
repository and data before acting.

| # | Finding (severity) | Verified? | Disposition |
|---|---|---|---|
| 1 | Random folds may be inflated by scanner/site leakage; leak check had no blocking rule (high) | Partly: the leak is a claim in the maverick notebook; fingerprint fields exist in its code but coverage is unverified | **Accepted.** Audit first, grouped folds by rule, explicit fallback (4.1, 4.5). |
| 2 | Gold-58 used both to pick the label source and as a gate (high) | Yes: rev. 1 picked steven v4 by gold rank and gated on gold; the gold CIs overlap so the choice was not supported anyway | **Accepted.** Label scheme fixed a priori, gold only as bug detector (4.3, 4.5). Codex's suggestion to compare label schemes by ablation is **not adopted**: the only common ruler across schemes is the gold set, which would reintroduce the reuse. UNK handling **adopted** using pilkwang verdicts (2.2). |
| 3 | 224 px departs from the only direct evidence (320 px); macro gate hides per-label losses (high) | Yes: s75-w50 checkpoint names are `convnext_tiny_320x24` (verified in decoded code) | **Accepted.** 320 primary, 224 ablation, per-label gates (4.2, 4.5). |
| 4 | 0.45 weight has no local basis; 0.943-0.945 outcome undefined (high) | Yes for the undefined zone. A local correlation estimate is not possible (risk 3) | **Accepted** in part: two pre-registered weights, complete decision table, anchor-only fallback in final picks (4.6). The local blend-sensitivity estimate is **not adopted** (no independent proxy predictions exist). |
| 5 | Own cache not yet proven; public corpus could unblock work in parallel (medium) | Yes: rev. 1 had only a 50-study visual dry run | **Accepted** in part: DICOM audit with thresholds before the cache, public corpus used only for a trainer smoke test. Using the corpus for a submitted model is **not adopted** because its test-time preprocessing cannot be reproduced. |

### Second review (proposed adjacent-triplet change, 2026-10-01)

Codex adversarial review verdict: needs-attention. Verified before acting.

| # | Finding (severity) | Verified? | Disposition |
|---|---|---|---|
| 1 | The proposed change was not in the working tree, and the document contradicted itself (sparse 8/6/8/4/6 cache vs "three adjacent slices" model input) (high) | Yes: the review was requested before the edit was written (our process error), and the revision-2 cache and model sections conflicted | **Accepted.** Revision 3 defines the cache per slot, the triplet as consecutive stored slices with end clamping, the training and inference centre counts, and the masked missing slot (4.2, 4.4). |
| 2 | About 11 adjacent triplets cover far fewer positions than 32 sparse slices; no isolated sampling ablation; not comparable with the verified 320 px leg (high) | Yes for the coverage loss of the 11-triplet proposal. Reading the verified leg's code (2.4) showed it avoids the trade-off by storing nearly all slices | **Accepted in substance**: the 11-triplet proposal is dropped and the cache keeps near-full coverage **and** true adjacency, matching the verified recipe. The suggested training ablation (sparse vs triplets) is **not adopted** because neither variant remains; coverage is measured instead by the inference-only `K_infer` check with per-lesion criteria (Gate A). |

### Third review (revision 3, 2026-10-01)

Codex adversarial review verdict: needs-attention. Verified before acting; where we
disagree, our position is stated.

| # | Finding (severity) | Verified? | Disposition |
|---|---|---|---|
| 1 | Gate A only varies `K_infer`, so it cannot show that 4 training centres per slot are enough for focal lesions; train/inference token counts differ (20 vs up to 120) (high) | Yes in substance: the verified leg infers with 24 centres per slot and its name suggests training with 24, so `K_train = 4` is our own deviation; a lesion on 2 of 30 slices is missed by a 4-centre draw in roughly 60% of steps, which acts as label noise | **Accepted**: covering sampler, per-epoch coverage logging, and a fold-0 `K_train` 4 vs 8 ablation (Gate A0). **Partly disputed** at the time (token-count mismatch called secondary); **this rebuttal was withdrawn in revision 3.2** (fourth review, finding 3) because it miscounted the tokens. We adopt the ablation mainly because it runs on the otherwise idle second T4 of the fold-0 session. |
| 2 | Batch of 8 studies x 20 triplets at 320 px has no memory plan; 100 img/s is unproven; the smoke test did not use the final shape (high) | Yes: 160 images of 320 px with backward on a 16 GB T4 is very likely to run out of memory, and 100 img/s was an unmeasured guess | **Accepted**: micro-batching with gradient accumulation and an activation-checkpointing fallback (4.4); Gate S measures memory and throughput on the final shape and the budget is recomputed before fold 0 and after its first epoch (4.5, 5). |

Remaining standing point: Codex's earlier suggestion to compare sparse sampling against
triplets in training (second review) stays rejected; Gate A0 now tests the variable that
actually remains open (training coverage).

### Fourth review (revision 3.1, 2026-10-01)

Codex adversarial review verdict: needs-attention.

| # | Finding (severity) | Verified? | Disposition |
|---|---|---|---|
| 1 | Budget recomputation had no stop or degradation threshold; quota billing and v05 runtime unverified (high) | Yes: revision 3.1 only re-estimated the budget without binding any action | **Accepted**: 18 GPU-hour cap, projection with a 1.2 margin, three checkpoints and a degradation order (5.1); quota billing observed at Gate S. **Disputed in part** at the time (v05 runtime deferred to v09); **withdrawn in revision 3.3** (fifth review, finding 2). |
| 2 | Gate A0 had no branches for run failures or non-comparable arms (high) | Yes | **Accepted**: comparability conditions and an outcome table with retry limits (4.5). |
| 3 | The rebuttal on token counts was wrong: K_train = 4 gives 20 tokens and K_infer = 8 gives 40 (medium) | Yes: we miscounted | **Accepted; rebuttal withdrawn.** Gate A now includes the matched setting `K_infer = K_train` and a pre-registered token-shift rule (4.5), which isolates the shift at no training cost. |

### Fifth review (revision 3.2, 2026-10-01)

Codex adversarial review verdict: needs-attention.

| # | Finding (severity) | Verified? | Disposition |
|---|---|---|---|
| 1 | The cap was checked only at three checkpoints against projections; a session slower than the 1.2 margin could cross 18 h before the next check (high) | Yes | **Accepted**: per-session launch condition, time limit with an in-notebook clean stop, and checkpoints before each fold batch and before v09 (5.1). |
| 2 | The cap includes the first v09 submission, so the v05 runtime cannot be deferred; the reserved disagreement conflicts with the cap (high) | Yes: given the cap's own definition, the argument holds | **Accepted; our earlier reservation is withdrawn.** Billing inputs are recorded before Gate S, and a v09 pre-submission gate with a fallback is added (5.1). |
| 3 | Gate A0 had no branch for arms that finish but are not comparable (medium) | Yes | **Accepted**: explicit row with rerun limits (4.5). |

Standing disagreement after five reviews: only the rejection of a sparse-vs-triplet
training ablation (second review), for the reason recorded there.
