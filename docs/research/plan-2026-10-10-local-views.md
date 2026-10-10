# Plan after the S6 template (2026-10-10)

Question (user, 2026-10-10): re-plan with Codex around the 0.954 template (public CoAtNet + heliosli's
anatomy-anchored compact model S6, `public-landscape-2026-10-10.md`) for the best value. Codex
(GPT-6 Astra, high, read-only) reviewed the embedded S6 sources and the author's code bundle; its
findings below were checked. Plan for discussion; any GPU training still needs a design note and a
Codex review (D-004).

## 1. What S6 is, and what is verified

- Views (`px_cache.py`, embedded in the notebook): per series a full field view plus anatomical 100 mm
  local views (joint, patellofemoral, posterior for sagittal/axial; two compartment views offset +-30 mm
  for coronal), rendered from DICOM at a 288 px cache size; thin stacks are averaged into about 3.5 mm
  slabs; a piecewise-linear intensity mapping keeps the tails instead of clipping.
- Localisation (`knee_anchor_bank_v2.py`): joint centre from the SKM-TEA V-Net on sagittal series,
  projected through DICOM geometry into the other series; fallback is the field centre.
- Model and loss (`compact_train.py`): 2.5D windows (3 physically adjacent slices), timm encoder
  (ConvNeXt-small per the notebook), per-class attention over all windows; arm `E_lrprior` minimises
  `-log[(1 - p) + r p]` with `r` the author's report-derived likelihood ratio (`|lr_prior` column). The
  table that produces `r` is **not** public. Folds are hash-based, gold excluded.
- Licence: the 0.954 notebook page states "released under the Apache 2.0 open source license"
  (checked in the browser, 2026-10-10), so its embedded sources can be reused with attribution. The
  author's `cloud_code` package in the dataset (licence "other", "no new open-source license is
  granted") is not covered: native cache and DICOM geometry must be our own.
- `best.pt` (OrthoFoundation-L fold 0, still public) was trained on **48 of the 58 gold studies** and its
  pretraining metadata records fastMRI (Codex, read from the checkpoint metadata). Together with the
  KneeXNet (OAI-derived) and SKM-TEA dependencies of its inference path, it is dropped.
- Full reproduction of the author's cache does not fit Kaggle outputs: 819,078 training slices at 288 px
  are about 68 GB per view before compression.

What creates the complementarity is not isolated: the local views at native resolution, the author's
report supervision and loss, full window coverage and intensity handling are confounded. Our own
evidence (STATUS L23-L26) says a changed backbone alone (v24) and a slightly changed target (v22) do
not escape redundancy; the new model must change views and supervision.

## 2. Plan

| Track | What | Cost | Gate / submission |
|---|---|---|---|
| A. I1 | Public CoAtNet through two preprocessing paths (exact + v07 adapter), probability mean, reader and TW unchanged | no training; about half a day of engineering | one submission |
| B1. Quick local-view screen | N recipe with two token sets per slot from the **v07 cache**: the 140 mm field and a central 100 mm crop (229 cache px resized to 320), report-only target (the four tables, no image teacher), fold 0 | local about 4-5 h | v17 + B1 at a fixed outer weight 0.15 (one submission); a weak result does not reject B2 (v07 has lost detail) |
| B2. Native local views (main bet) | Own Kaggle CPU cache from DICOM: per slot series, full field plus 100 mm local views around the acquisition centre (no SKM-TEA), at a native-derived resolution, JPEG shards under 15 GB each; same model and report-only target; fold 0, then more folds only after a positive blend | 1.5-3 days of engineering; cache 2-5 CPU h; fold 8-16 local h | v17 + B2 at 0.15 (one submission); >= 0.951 funds one more fold, >= 0.952 funds 3-4 folds |
| C. v24 | fold-0 leg submission already pushed | - | informational; no automatic folds 1-4 even at 0.937 (gate by ensemble contribution) |
| D. Merger | a team with runnable S6-like models is the best value per day | user's decision; deadline 2026-10-15 | - |

Dropped: author-pipeline reproduction, OrthoFoundation `best.pt`, SKM-TEA/KneeXNet localisation (extra
rule risk), T2 sequence head, T3/T4 new backbones, reader retraining, more teacher rounds or label voters.

Decision rules: new legs are tested as `rank(0.85 rank(v17) + 0.15 rank(leg))` (one fixed weight);
adoption over v19 needs 0.952; 0.951 funds limited expansion.

## 3. Schedule (UTC)

| Day | Local GPU | Kaggle | Submissions |
|---|---|---|---|
| 10-10/11 | B1 fold 0 (after its design review) | B2 100-study rendering pilot (CPU) | I1 |
| 10-12 | B2 exporter finished; B1 checks | B2 cache shards (CPU) | B1 blend |
| 10-13 | B2 fold 0 | parity and runtime check | - |
| 10-14 | B2 inspection | - | B2 blend; merger decision |
| 10-15/16 | B2 folds as gated | quota reset 10-17 | expansion blend |
| 10-17/18 | packaging, final inference | final checks | final candidates |
| 10-19 | freeze | | |
