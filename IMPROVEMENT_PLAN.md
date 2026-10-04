# Improvement Plan

Directions for improving on the v05 public-stack anchor, in priority order, each with
the reason behind it. Written 2026-10-01 after the baseline survey
(`docs/research/baseline-selection.md`, `docs/research/discussion-key-findings.md`).
Update this file when a direction is started, finished, or dropped; record results in
`docs/experiments.md` and decisions in `docs/decisions.md`.

**Before editing this file, read `docs/version-history.md` (D-011)** and cite the versions
and lessons behind each change. Status 2026-10-04: Priority 0 done (v05 0.943); Priority 1
tried as v08-v10 and failed to help (v09 0.932, v10 leg alone 0.909); the plan below is due
for revision.

## Goal and constraints

- **Goal: a medal.** On the 2026-10-01 public board (4,730 teams) bronze (top 10%) sits
  inside the 0.943 tie block shared by about 1,000 teams, silver (top 5%) needs about
  0.945, gold (top 10 + 0.2%) about 0.956. Because so many teams sit on the same public
  stack, the realistic target is **public >= 0.946 with a model we trust on the private
  set**, which should hold a bronze through shake-up and has a chance at silver.
- **Compute: 30 Kaggle GPU hours per week**, about 90 hours until the final deadline
  (weeks starting 2026-10-01, 10-08, 10-15). No local GPU.
- **Dates:** entry and team-merger deadline 2026-10-15; final submission 2026-10-22.
- **Submissions:** 5 per day; two final selections.
- **External MRI datasets:** postponed by the user; not part of this plan for now.

## Priority 0 - Reproduce the anchor (v05)

**What.** Run `notebooks/v05-public-stack-anchor.ipynb` (Jiwei Liu v11, unchanged) on
Kaggle and submit it once.

**Why.**
- It confirms that our copy reproduces 0.943, which every later blend builds on.
- It measures the real hidden-test runtime. That number limits how large our own model
  can be: the anchor and our model must finish together in under 9 hours.
- It has to be in place before the 2026-10-15 entry deadline anyway.

**Cost.** About 5 GPU minutes for the commit run; the submission rerun time is unknown.
**Done when.** Public LB 0.943 and a recorded runtime in `docs/experiments.md`.

## Priority 1 - Our own diverse model, rank-blended into the anchor

**What.** Train our own 2.5D image model on the full training set and blend it into the
anchor by per-target rank: `rank((1 - w) * rank(anchor) + w * rank(ours))`, w about
0.45-0.5, fixed in advance.

Starting design (to be written up as a design note before building):
- Backbone: a CNN family that is not in the public stack, e.g. ConvNeXt-tiny or
  EfficientNet-B2, ImageNet-pretrained, 256-320 px.
- Input: fixed physical crop of about 140 mm; slices sorted by `ImagePositionPatient`
  projected on the slice normal; adjacent-slice triplets as channels; slots per plane and
  fat-suppression (sagittal FS, coronal FS, axial FS, sagittal non-FS); left/right knee
  normalisation; missing-plane handling kept.
- Targets: soft report-derived labels (the public `pilkwang/rsna-knee-llm-labels` table to
  start); the 58 gold studies are used for evaluation only.
- Validation: folds split by `StudyInstanceUID`, grouped by scanner/site fingerprint if
  the leak claim checks out; single fold end to end first, then 5 folds.
- Preprocessing: build a cached slice dataset once in a CPU notebook, so GPU hours go
  only to training.

**Why.**
- It is the only change with direct evidence of going above 0.943. `knee-s75-w50` adds a
  plain 5-fold ConvNeXt-tiny (320 px, weak-label CV about 0.90) at weight 0.5 and goes
  0.943 -> 0.945. `d4-blend` adds a private model group at 0.45 and reaches 0.946. Forks
  without those private models drop back to 0.943.
- Blends gain most from models whose errors differ. The public stack is DINOv2, ResNet-50
  and CoAtNet trained by other people on mostly the same labels; our own CNN with
  different preprocessing adds errors the stack does not share.
- It protects the private score. The stack's weights were tuned on the public board over
  about 40 versions; a model we validate ourselves and blend with a pre-declared weight is
  less exposed to public-board overfitting.
- It does not need to be strong on its own: the 0.945 leg had CV about 0.90.

**Cost.** About 1.5-3 GPU hours per fold at 256-320 px (estimate, to be measured on the
single-fold run); about 10-15 hours for 5 folds. Inference must fit the runtime left after
the anchor.
**Done when.** Public LB of the blend >= 0.945 and OOF/gold evaluation recorded.

## Priority 2 - Better labels for our model

**What.**
1. Combine several public report-label tables (pilkwang, stevenleehans, lixin73) into one
   soft target, keeping "not addressed" separate from explicit negatives.
2. After the first 5-fold run, mix our **out-of-fold** predictions into the soft targets
   (about 50/50) and retrain once.

**Why.**
- Several high scorers on the forum independently name labels and pseudo-labels as their
  main lever, and report that a larger encoder adds about +0.001.
- The gold labels were read from the images, not the reports (host statement), so report
  labels are noisy by design; an image model's out-of-fold predictions carry information
  the report does not, especially for findings reports rarely mention.
- It targets the weakest findings: Synovitis, Lateral OA and PF OA, where silent report
  negatives dominate.
- It costs no new data and only one extra training round.
- Out-of-fold is essential: forum reports say in-fold predictions only repeat the labels.

**Cost.** One extra 5-fold training round (about 10-15 GPU hours).
**Done when.** Gold-58 and weak-label OOF AUC improve, and the blend's public LB does not
drop. Gains on the 58 gold studies alone are not trusted (too few positives).

## Priority 3 - Anchor robustness and runtime

**What.**
1. If the anchor plus our model exceed the time limit, switch the anchor to fewer eval
   windows (the `sparse` 62/42 preset documented in `maverickss26/rsna-knee-0942-restructured`).
2. Check the stack's A5 stage, which uses bf16 autocast on T4 GPUs that have no native
   bf16: compare its predictions under bf16 and fp16 on a few training studies; if the
   rankings differ materially, run it in fp16.
3. Final selection: one submission with the pre-declared blend weight, one more
   conservative variant (for example lower weight on our model). No per-target weight
   tuning on the public board.

**Why.**
- The 9-hour limit is hard: a submission that times out scores nothing.
- The stack silently drops a CoAt reader that fails; a lower score instead of an error is
  easy to miss, so runtime and memory headroom matter.
- A forum report links bf16 on T4 to a silent AUC drop (0.851 -> 0.710 in their model).
  Whether it affects this stage is unknown; the check is cheap.
- Per-target retuning is what moved the public stack from 0.941 to 0.943; on about 1,300
  test studies such gains are close to noise and do not carry to the private board.

**Cost.** Under 1 GPU hour for the bf16 check; the rest is submissions.

## Priority 4 - A second own model (only if time allows)

**What.** A second model that differs from the first in backbone family or input
geometry (e.g. a ViT/DINOv2 fine-tune, or a different crop and resolution), added to our
leg before blending.

**Why.** `d4-blend` used a group of three student models and scored higher than the
single-model `knee-s75-w50` (0.946 vs 0.945), which suggests more independent models keep
adding. It only makes sense after Priority 1 and 2 have produced a working leg.

**Cost.** 10-15 GPU hours for 5 folds.

## Not planned, and why

- **Retuning the public stack's weights on the public board:** about 1,000 teams already
  hold this score; the gains are at noise level and overfit the public split.
- **Single-finding specialists:** `romantamrazov/rsna-knee-dinosaur-v5` added a Medial
  Meniscus specialist and stayed at 0.943.
- **External knee MRI datasets:** postponed by the user; host rules are still unclear.

## GPU budget (30 h per week)

| Week | Planned GPU use |
|---|---|
| 2026-10-01 to 10-07 | v05 commit run; cached-dataset build (CPU); our model single fold, then 5 folds (about 15-20 h) |
| 2026-10-08 to 10-14 | Label rework and a second 5-fold round (about 15 h); blend submissions; bf16 check |
| 2026-10-15 to 10-21 | Second own model if justified; final blend; select two final submissions |

Whether scoring reruns of submissions count against the weekly GPU quota is not
verified; keep a few hours of margin each week.
