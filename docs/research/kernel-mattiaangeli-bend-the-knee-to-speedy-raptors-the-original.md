# Bend the Knee to Speedy Raptors - The Original

- Source: https://www.kaggle.com/code/mattiaangeli/bend-the-knee-to-speedy-raptors-the-original (version 39, pulled 2026-10-01)
- License: Apache 2.0 (shown on the Kaggle page)
- Public LB: 0.943 best (as of 2026-10-01). Jiwei Liu's changelog attributes the 0.943 to
  version 34, so the pulled version 39 is not guaranteed to be the scored one.
- Local copy: external/kernels/mattiaangeli__bend-the-knee-to-speedy-raptors-the-original/

This is the root of the public 0.941-0.946 lineage. Every notebook in our shortlist except
Tony Li's consolidated bundle and pilkwang's baseline is a fork or near-fork of it (pairwise
code diff 62-894 lines out of ~4,600; see `baseline-selection.md`). It is **inference only**:
it trains nothing and blends checkpoints published by about ten different authors.

## Pipeline (verified in code)

The notebook is a single sequential graph with hash-pinned assets and hard gates (for
example `_DINOV2_MATCHED_MEMBERS != 20` aborts the run).

| Stage | Family | Weights (dataset) | Input | Combination |
|---|---|---|---|---|
| 1 | DINOv2-small slot-attention, 20 members (5 folds x 4) | `pilkwang/rsna-knee-weights` (CC0) + `metaresearch/dinov2` small | 130 mm crop, 336 px cache, 3 adjacent slices as RGB, slot head per series | Per-fold raw mean then rank; per-target window pooling (`max`, `top2`, soft-max) hand-set per finding |
| 2 | "A5" attention-pooling, 5 folds (timm backbone read from checkpoint config) | `mattiaangeli/knee-mri-fold-weights` (CC0) | 130 mm, 336 px, 16 slices from band 0.12-0.88, 6 plane x fat-sat slots | Rank, blended into stage 1 at `A5_W = 0.52` |
| 3 | RadImageNet ResNet-50 encoder + attention heads (E10/E13/E11 layouts) | `marwanmath/resnet-50-radimagenet-marwan`, `antoinegg1/*heads*`, `prvsiyan/*v52*` (CC-BY-NC-SA / other) and two `sofiaanjenje` training notebooks | 224 px, 130 mm, 8 slices per slot | `_RAD_ALPHA = 0.55` reference, second pass 0.20, plus a frozen logistic calibrator stored as a zlib+base64 JSON payload (`_RAD_CAL_PAYLOAD`, decoded: keys `mean, scale, coef, intercept, gate, protocol_columns, groups`); Baker's and Fracture excluded from the Rad mix |
| 4a | "Raptor" CoAtNet (`coatnet_rmlp_2_rw_384`), 3 checkpoints in 4 views (maxspan v5 forward and reverse, native384dense v10, native384 v8) | `dreaddevelopment/raptor-knee-*` (CC0) | 384 px, 140 mm, 64-96 slices, up to 94 windows per study | Probability mean 0.60/0.10/0.10/0.20 |
| 4b | Mattia's CoAt family: residual-gated top-3, D4 depth-zone SWA3, Global96 top-3, Repair-v1 top-3 | `mattiaangeli/rsna-knee-coat*` (CC0) | 384 px adjacent-slice triplets, 96-slice stack | 0.25 each, probability mean then rank; family 0.40 vs Raptor 0.60 |
| 5 | Final per-target blend of transformer side (1-3) and CoAt side (4) | - | - | CoAt weight 0.70 by default; ACL 0.75, Medial Meniscus 0.80, Lateral Meniscus 1.00, Lateral OA 0.75, Fracture 0.75; then rank |

The submission is per-target percentile ranks (`rank(pct=True)`), which is valid for AUC.

## Use of reports and labels

Indirect only. The notebook never reads reports. The underlying checkpoints were trained by
their authors on report-derived weak labels, mostly the public LLM label table
`pilkwang/rsna-knee-llm-labels` (CC0, attached here but only as an asset dependency).
Raptor's author states every Raptor checkpoint shares one label set (author's text,
discussion 737696).

## Training recipe

None in this notebook. Training code is public for only part of the stack:
pilkwang's baseline (DINOv2 members), Sofia Anjenje's E11/E13 notebooks (Rad heads), and
Mattia's D4 notebook linked in the header (not pulled or inspected). Raptor preprocessing and training
code is **not** published (author's text in discussion 737635).

## Inference, run time and GPU

- TTA: overlapping windows, a jitter view for some DINO members, a reverse-channel Raptor
  view, horizontal flip for Rad E13.
- Hard requirement of **exactly 2 x T4** (`_d4_check_runtime` raises otherwise) and
  pinned `cv2 == 4.12.0`, `timm == 1.0.22` (pinned OpenCV wheel is attached as a dataset).
- Internal `TIME_BUDGET = 8 h`. The visible Kaggle run takes about 6 minutes, but that run
  only sees the 3 placeholder test studies. Full hidden-test runtime is not public; the
  author says it runs "comfortably in less than 9 hrs" and Raptor's author reported about
  9 h for 94 windows before speed-ups (author claims, not verified).
- Several CoAt child processes are wrapped in try/except and the blend continues without
  a failed arm (logged as an event). On the hidden set this means a silent score drop
  rather than a failed submission.

## External datasets and weights

14 datasets + 2 notebook outputs + 1 Kaggle model, all public as of 2026-10-01. Licenses:
CC0 for the DINO, A5, Raptor, CoAt and label assets; **CC-BY-NC-SA 4.0** for the
RadImageNet encoder and the Antoine heads; "other" for prvsiyan's heads; "unknown" for the
OpenCV wheel.

## Risks and open questions

- The per-target weights, pooling modes and routing (for example Lateral Meniscus 100%
  CoAt) were tuned by many authors on the public LB over about 40 versions. With ~1,300
  test studies split public/private, the 0.941 -> 0.943 steps are close to public-LB noise.
- Uses `bf16` autocast in the A5 stage on T4 (no native bf16). It runs, but see discussion
  744230 for a reported silent AUC loss from bf16 on T4; we did not check whether it
  affects this stage.
- About 1,000 teams sit at public LB >= 0.943, so this recipe alone is the medal floor, not
  an edge.
