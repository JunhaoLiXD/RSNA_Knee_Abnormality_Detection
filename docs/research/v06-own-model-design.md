# Design note: our own 2.5D model leg (v06-v09)

Date: 2026-10-01. Status: **revision 2 after Codex adversarial review (section 9); awaiting
user approval (D-004)**. No GPU time is spent before approval.

Implements `IMPROVEMENT_PLAN.md` Priority 1 (own diverse model, rank-blended into the v05
anchor) together with the label part of Priority 2. Background:
`docs/research/baseline-selection.md`, `docs/research/discussion-key-findings.md`.

## 1. Goal and success criteria

- **Goal.** An independently trained image model that, rank-blended into the v05 anchor
  (public LB 0.943, verified 2026-10-01) with pre-registered weights, lifts the public LB
  to **>= 0.945**, and that has passed our own **scanner-grouped** validation, so the gain
  is not only a public-board effect.
- **Why this target.** `knee-s75-w50` reached 0.945 by adding a 5-fold ConvNeXt-tiny at
  **320 px / 24 slices** (weak-label CV about 0.90) at weight 0.5; `d4-blend` reached 0.946
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

## 3. Plan overview and versions

| Version | Notebook | Kaggle resources | Purpose |
|---|---|---|---|
| v06 | `v06-dicom-audit.ipynb` | CPU | Read-only audit of all training DICOM headers and codecs; scanner fingerprints; fold file |
| v07 | `v07-cache-320.ipynb` | CPU | Training cache at 320 px built with the shared preprocessing function |
| v08 | `v08-convnext-tiny.ipynb` | GPU T4 x2 | Resolution ablation on fold 0, then 5 folds of the chosen configuration |
| v09 | `v09-anchor-plus-v08.ipynb` | GPU T4 x2, submissions | Explicit ensemble of v05 and v08 |

In parallel with v06/v07 (CPU), a short **trainer smoke test** on the public Raptor corpus
validates the training loop, loss and metrics (about 30 GPU minutes). That model is never
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

- **Slots and slices (32 per study):** sagittal fluid-sensitive 8, sagittal
  non-fluid-sensitive 6, coronal fluid-sensitive 8, coronal other 4, axial
  fluid-sensitive 6; evenly spaced over the central 10-90% of the series after sorting by
  `ImagePositionPatient` projected on the slice normal (fallback `InstanceNumber`); a
  missing plane gives an empty, masked slot.
- **Geometry:** 140 mm centre crop using `PixelSpacing`, resized to **320 x 320**, per-slice
  percentile windowing to uint8. 320 px matches the only reproduced-in-code successful
  recipe; 224 px inputs for the ablation are produced by on-the-fly downsampling of the same
  cache.
- **Laterality:** one canonical medial/lateral orientation (in-plane flip for coronal and
  axial, slice-order reversal for sagittal), following the pilkwang method.
- **Size:** 4,407 x 32 x 320 x 320 bytes = 14.4 GB uncompressed; must fit the notebook
  output limit (believed 20 GB; checked in a 50-study dry run, and the cache is written as
  compressed per-study arrays if needed).
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
- Three adjacent slices of one slot as RGB channels; features of every triplet plus a slot
  embedding; per-finding attention pooling over the study; 12 logits.
- Training: AdamW, lr 2e-4 head / 5e-5 backbone, cosine with 1 warm-up epoch, 10 epochs,
  fp16 autocast (T4 has no native bf16), batch 8 studies, light augmentation (scale/crop,
  small rotation, intensity jitter; no left/right flip). Checkpoints
  `v08_fold_<k>_best.pt`.

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

**Gate A - resolution (fold 0, 224 vs 320, run in parallel on the two T4s).** Choose 320
unless 224 has macro AUC within 0.005 of 320 and no label more than 0.01 worse, in which
case choose 224 (cheaper). Each configuration must also pass Gate B to be eligible.

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
| Trainer smoke test on public corpus | about 0.5 GPU h | 1 epoch on a subset |
| Gate A: fold 0 at 224 and 320 in parallel | about 4 GPU h of session time | 320 px is about 2x the cost of 224 px (estimate) |
| Remaining 4 folds, two in parallel | about 8 GPU h | 2 sessions of about 4 h |
| v09 submissions | 2-3 runs | anchor runtime plus 10-20 min for our leg |

Total about 13 GPU hours: under half of one week's quota. Estimates are unmeasured; the
smoke test and fold 0 calibrate them. Whether quota counts session time rather than
GPU-time is unverified. The v05 hidden-test runtime is still to be read from the Kaggle
submissions page and fixes the inference budget for v09.

## 6. Timeline

| Dates | Work |
|---|---|
| 10-02 to 10-03 | v06 audit, v07 cache dry run and full run, trainer smoke test |
| 10-04 to 10-06 | Gate A and Gate B on fold 0 |
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

## 8. Changes from revision 1

- 224 px -> 320 px primary, with a 224 px ablation from the same cache.
- 60 slices -> 32 slices per study (fits the cache at 320 px; the public 0.945 leg used 24).
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
