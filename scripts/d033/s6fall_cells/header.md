# v61 - v54 + nartaa's all-data S6 (S6F0) in the ConvNeXt slot at 0.35 (D-033)

Explicit ensemble version (D-017), decision D-033 (`docs/research/silver-push-2026-10-14.md`). The base is v54, unchanged
except for the cells listed under "Our changes": nartaa's 384-px CoAtNet with its 224-px sibling (R224, with the anatomical
mirror) in the Raptor slot, heliosli's R7 ConvNeXt-small (with its own flip-TTA) in the ConvNeXt slot, the outer goodpjw2008
reader. The addition is a second ConvNeXt-small model in the ConvNeXt slot: nartaa's all-data S6 checkpoint ("S6F0").

## Provenance of the addition

- Model: `E_prior_s42_fall.pt` (sha256 `0c7297d58f061ab4e5d7c55046f51fa3e8934928046f0647a0c7854e98371c12`), dataset
  `nartaa/rsna-knee-s6fall-weights` (https://www.kaggle.com/datasets/nartaa/rsna-knee-s6fall-weights). **Licence CC BY-NC 4.0**
  (use for non-commercial purposes with credit to nartaa and, for the architecture, heliosli). heliosli's S6 architecture
  (`compact_train.Net`, convnext_small, per-finding spatial attention + window-attention MIL) retrained by nartaa from the timm
  ImageNet-22k initialisation on report-derived soft labels (JEV blend), 4,263 competition studies, gold-58 excluded, no OAI data
  (dataset README and `checkpoint-manifest.json`); 0.950 public alone.
- Code: component B of nartaa's public notebook https://www.kaggle.com/code/nartaa/rsna-knee-s6fall-solo (Apache 2.0; the script
  as pulled on 2026-10-15, sha256 `__NARTAA_SHA__`; write-up:
  https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/749359). His environment probe, launcher and
  component-B stack probe are embedded byte for byte; his argument list, GPU split, receipt checks and the one retry of failed
  studies are ported. Not taken: the 0.949 CoAtNet component A (we run no second CoAtNet here) and his hard-error policy (here any
  failure leaves the blend exactly as v54). Inference code: heliosli's older `compact_infer.py` (sha256 `34f433fe...`; R7 uses
  `8401812c...`), run unchanged. The code bundle `s6_extras.bin` (heliosli's public-notebook `compact_*` scripts and MONAI 0.6.0
  files, Apache 2.0) and `code_manifest.json` come from nartaa's dataset; the other 272 code files and `anatomy.pt` come from
  heliosli's `rsna-orthofoundation-fold0-epoch7-20261004`, which this notebook already attaches for R7. Every file is checked against
  pinned sha256 values before use.

## Our changes (against v54)

1. This cell and the configuration cell (`VERSION = 'v61'`).
2. New cells "Stage 2f [s6f]" (markdown + code), after the R224 stage: S6F0 as its own guarded stage (own temp folder, own output
   files `ours_s6f_sub.csv` / `ours_s6f_receipt.json`, no global or file of the R7 stage touched, `submission_receipt.json` untouched),
   an absolute cut-off at `READER_DEADLINE_S - READER_MIN_S - 15 min` (the R224 cut-off; the reader keeps its launch allowance), no
   start with less than 50 min left, compact_infer's own deadline 20 min before the cut-off (reaching it counts as a failure), every
   process in its own process group killed on every exit path.
3. Stage-3 blend, three hunks: an `[s6f]` validation block, one mix in the per-finding loop
   (ConvNeXt slot rank = 0.65 x rank(R7) + 0.35 x rank(S6F0) over the studies both scored; a study S6F0 failed on keeps rank(R7)),
   and an `s6f` record in `blend_receipt.json`. S6F0 is not used (stage 3 equals v54's) when the stage did not finish, its output
   is malformed, more than 3 % of the studies are unscored by S6F0, or its mean per-finding Spearman with R7 is below 0.5 (from 50
   jointly scored studies on).
4. Every other cell is byte-identical to v54 (asserted in the builder).

Weight 0.35 is fixed before any run (the R224 precedent), not tuned. Extra input to attach: `nartaa/rsna-knee-s6fall-weights`.

---

Base notebook header (v54):
__BASE_BODY__
