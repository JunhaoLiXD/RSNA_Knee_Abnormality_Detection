# Public notebooks: update 2026-10-11

Follow-up to `public-landscape-2026-10-10.md`. Sources: the competition Code page sorted by public score
(built-in browser, 2026-10-11 ~02:00 UTC), five notebooks pulled to `external/kernels/` with metadata, the
current file list, README and manifest of `heliosli/rsna-knee-compact-v1`
(`external/datasets/heliosli__rsna-knee-compact-v1-meta-20261011/`), and forum topics 737950, 743416,
744056, 747455, 748011, 748111. Authors' text is marked as such; everything else was read in the code or
the files.

## 1. Scores (Code page, best public score)

| Public LB | Notebook (updated) | Inputs (kernel metadata) | Usable by us |
|---:|---|---|---|
| **0.954** | heliosli/rsna-knee-blend-gold-dataset-restored (V3; 0.954 is V1; Apache 2.0) | `heliosli/rsna-knee-compact-v1`, `nartaa/...-swa-weights-20261007`, `heliosli/rsna-orthofoundation-fold0-epoch7-20261004` | yes, all three public now |
| 0.954 | matterhorn3838/rsna-knee-v2-velciraptor-dinosaur-speed | the same three (same code, bundle `209a32c8b50a6b1c`) | copy of the above |
| 0.954 | heliosli/one-click-955-... | an input not visible to us (`''`), bundle `55bd00b3ba0f4e22` ("R3 ConvNeXt, crop 384") | no |
| 0.952 | jenillangaliya/rsna-knee-0-952-tri-hybrid-multi-scale-mil | two inputs not visible to us | no |
| 0.951 | romantamrazov/rsna-knee-dinosaur-the-last | `goodpjw2008` reader + `nartaa` weights (the v17 assets, plus the 224-crop CoAtNet in the same dataset) | yes |
| 0.951 | versia-7, template, blend-gold (V1), blend3, dual-stage | older S6 bundle `c7ebab1e` | - |
| 0.950 | v17-type and others | - | (our v17/v27) |

## 2. The S6 files are public again

`heliosli/rsna-knee-compact-v1`, new version 2026-10-10 19:50 UTC: `E_lrprior_s0_f0..f3.pt` (ConvNeXt-small,
200 MB each), `side_cls.pt`, `manifest.json`, `state_spec.json`, README. README (author's text): the files were
removed "because someone told me it wasn't allowed, but it seems to be allowed after all"; the latest version
equals Version 10 byte for byte (bundle `209a32c8b50a6b1c`). Manifest: convnext_small (ImageNet-22k init),
4 folds, 16 epochs, report-derived targets, `gold_in_training: 0`, `official_labels_read_by_trainer: false`,
views v4, 3.5 mm slabs, crop 352 of 384. Dataset licence: not set.

The 0.954 notebook (read in the code): stage 1 runs the public 0949 CoAtNet notebook as published; stage 2
runs the S6 inference from the author's code in the OrthoFoundation dataset (`cloud_code`), which uses
`anatomy.pt` (SKM-TEA V-Net) for the knee anchors; stage 3 is a per-finding rank blend with fixed weights,
CoAtNet 0.7 and S6 0.3. `best.pt` (OrthoFoundation-L) and the KneeXNet weights are not referenced.

## 3. Rule status (forum, 2026-10-11)

- No host ruling on OAI, SKM-TEA, MRNet or fastMRI. The only explicit ruling: KneeCoT prohibited (topic
  734109, a formal institutional agreement). Host guidance quoted in topic 743416 (2026-08-27): straightforward
  registration or click-through data-use agreements are generally acceptable, institution-specific approvals
  are not. A participant reports OAI approval on NDA as an individual, immediately (743416).
- The S6 path adds one asset beyond D-019's risk: the SKM-TEA segmentation checkpoint (SKM-TEA is distributed
  by Stanford AIMI after registration and a research use agreement). Its category under the host guidance is
  the same as OAI's; not ruled.
- Using other participants' public weights is allowed by rule 2.6.b; the winner's-obligation question (topic
  744056) matters only for prize winners.

## 4. Other notes

- romantamrazov 0.951: the v17 assets with per-finding weight changes for Lateral OA, Synovitis and Contusion
  (a 224-crop CoAtNet and an Effusion x Baker's signal), tuned across its versions V14-V21 on the public LB.
- Topic 748011 (author's text): across 15 own submissions, gold-58 AUC correlates with the public LB at
  r = 0.66 and AUC against LLM-extracted labels on ~4,300 studies at r = 0.87. Consistent with L20/L28; our
  validation AUC (soft labels, ~950 studies per fold) may be the better local screen.

## 5. Options

1. **Reproduce the 0.954 notebook unchanged** (new anchor version; like v17 for the 0.950 notebook). Cost: one
   commit run and one submission, no training; hidden-run time per the author's deadline settings (8.3 h cap).
   Expected 0.954 if the reproduction is exact. Rule risk: D-019 plus SKM-TEA.
2. **That anchor plus our v26 leg at w 0.15** (v27 lifted v17 in the hidden digits, L29). Same risk.
3. Keep v27 + v15 and continue D-022 only (no new rule risk).

A change from D-021 ("no SKM-TEA, KneeXNet or OrthoFoundation assets") needs the user's decision and a recorded
decision; a short design note with a Codex review before building.
