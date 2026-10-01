# Baseline selection for v05

Date: 2026-10-01. Status: **recommendation, awaiting discussion with the user**. No v05
notebook has been written.

Sources: Kaggle kernel list (CLI, sorted by score and votes), Kaggle web API for public
scores and data sources, leaderboard download, 13 pulled notebooks in
`external/kernels/`, about 25 forum topics. Per-notebook notes are linked below; forum
findings are in [discussion-key-findings.md](discussion-key-findings.md).

## 1. Shortlist

Public LB is the notebook's best public score as listed by Kaggle on 2026-10-01. "Inputs
public" means every attached dataset is visible to others (private inputs appear as
"[Private Datasource]" on the page and as empty slugs in `kernel-metadata.json`).

| # | Notebook | Public LB | Votes | Last run | Version pulled | License | Inputs public | Note |
|---:|---|---:|---:|---|---|---|---|---|
| 1 | [pjmathematician/rsna-knee-d4-blend](kernel-pjmathematician-rsna-knee-d4-blend.md) | **0.946** | 98 | 2026-09-28 | v3 | Apache 2.0 | **No** (3 private) | 0.943 stack + private model leg at 0.45 |
| 2 | pjmathematician/rsna-knee-d4-lite (same note) | 0.945 | 110 | 2026-09-26 | v1 | Apache 2.0 | **No** (3 private) | 30-line diff to #1 |
| 3 | [aastikrajan15/knee-s75-w50](kernel-aastikrajan15-knee-s75-w50.md) | 0.945 | 46 | 2026-09-27 | v1 | Apache 2.0 | **No** (1 private) | 0.943 root + own 5-fold ConvNeXt-tiny at 0.5 |
| 4 | [jiweiliu/rsna-knee-fast-2xt4-inference](kernel-jiweiliu-rsna-knee-fast-2xt4-inference.md) | 0.943 | 206 | 2026-09-23 | v11 | Apache 2.0 | Yes (18) | Fast 2xT4 version of the 0.943 recipe |
| 5 | [mattiaangeli/bend-the-knee-to-speedy-raptors-the-original](kernel-mattiaangeli-bend-the-knee-to-speedy-raptors-the-original.md) | 0.943 | 195 | 2026-09-22 | v39 (0.943 from v34) | Apache 2.0 | Yes (18) | Root of the lineage |
| 6 | [evgendvorkin/rsna-versia-5](kernel-evgendvorkin-rsna-versia-5.md) | 0.943 | 262 | 2026-09-26 | v18 | Apache 2.0 | Yes (19) | Annotated copy of #4 |
| 7 | [romantamrazov/rsna-knee-dinosaur-v5](kernel-romantamrazov-rsna-knee-dinosaur-v5.md) | 0.943 | 116 | 2026-09-30 | v24 | Apache 2.0 | Yes (21) | #6 + Medial Meniscus specialist; public training notebook |
| 8 | [maverickss26/rsna-knee-0942-restructured](kernel-maverickss26-rsna-knee-0942-restructured.md) | 0.942 | 178 | 2026-09-20 | v7 | Apache 2.0 | Yes (17) | Readable 0.942 step with presets |
| - | [tonylica/rsna-knee-dino-radimagenet-rank-ensemble](kernel-tonylica-rsna-knee-dino-radimagenet-rank-ensemble.md) | 0.940 | 100 | 2026-09-12 | v11 | Apache 2.0 | Yes (1 bundle) | Clean one-dataset packaging, DINOv3 members |
| - | [pilkwang/rsna-knee-baseline-v1](kernel-pilkwang-rsna-knee-baseline-v1.md) | 0.891 | 654 | 2026-08-08 | v15 | Apache 2.0 | Yes | Source of the DINO weights and LLM labels |

**Every notebook from 0.940 to 0.946 belongs to one lineage.** Pairwise code diffs between
#3-#8 are 62-1,460 lines on ~4,600-line notebooks (computed locally); #1-#3 are the 0.943
stack plus a private extra model. Scores of 0.941 -> 0.943 came from per-target weight
retuning on the public LB over the same checkpoints (history in versia-5, verified against
the weight literals in code).

## 2. Comparison

All rows in the top block share the same public models; differences are listed only where
they exist. V = verified in code; A = author's claim only.

| Aspect | 0.943 public stack (#4-#8, root #5) | Private-leg variants (#1-#3) | Tony Li bundle | pilkwang baseline |
|---|---|---|---|---|
| Backbones | DINOv2-S x20, A5 timm x5, RadImageNet ResNet-50 + heads, Raptor CoAtNet-RMLP-2 x3 (4 views), 4 Mattia CoAt readers (V) | + #1: unknown private "fleet" (S_dist/S_coat/S_cnxl); #3: ConvNeXt-tiny x10 (V) | DINOv2-S x20, DINOv3-S x5, Rad, Raptor, residual CoAt (A, modules not inspected) | DINOv2-S (V) |
| Input | DINO 130 mm/336 px, 3-slice RGB, slot head; A5 16 slices 0.12-0.88 band; Rad 224 px, 8 slices; Raptor/CoAt 140 mm, 384 px, 64-96 slices, up to 94 windows (V) | #3: 130 mm, 320 px, 24 slices (V) | 130/140 mm, 336-384 px (A) | 130 mm fixed-mm crop, geometric slice sort, laterality normalisation (V/A) |
| Reports / weak labels | None at inference; checkpoints trained by others on LLM report labels (pilkwang CC0 table) (A) | #3: own folds, filename CV 0.896-0.915 on weak labels (V) | as left | Rule extractor + LLM table, confidence as sample weight (A) |
| Training | None (inference only) (V); training code public only for DINO, Rad heads, some CoAt | Not public | None | Yes, 10 epochs (V) |
| Inference / ensembling | Window pooling per target, jitter / reverse / flip views, rank blends with hand-set per-target weights, frozen logistic calibrator (V) | Extra rank blend 0.45-0.5 (V) | Rank blends (A) | Rank averaging (V) |
| Runtime / GPU | Exactly 2 x T4 required (V); internal budget 8 h (V); full hidden runtime unknown, author says < 9 h (A) | Leg budgeted into remaining 9 h (V) | 2 x T4 (V) | ~6 min visible run |
| External deps | 14 datasets + 2 notebook outputs + DINOv2 model; CC0 except RadImageNet & Antoine heads (CC-BY-NC-SA 4.0), prvsiyan heads ("other"), OpenCV wheel ("unknown") (V) | + private datasets | 1 dataset ("other") | 3 datasets |
| Reproducible by us | **Yes** | **No** | Yes | Yes |

## 3. What the evidence says

1. **0.943 is the floor, not an edge.** 1,001 of 4,730 teams are at >= 0.943 public; bronze
   (top 10%) currently falls inside that tie block, silver needs about 0.945, gold about
   0.956 (leaderboard download, 2026-10-01).
2. **The step above 0.943 comes from adding an independent model, not from reweighting.**
   #3 adds a plain 5-fold ConvNeXt-tiny (320 px, weak-label CV about 0.90) at 50% rank
   weight: 0.943 -> 0.945. #1 adds a private model fleet at 45%: 0.946. Forks of #1 without
   the private data fall back to 0.943 (verified on the board).
3. **Strong single models exist.** Forum reports of single 2.5D models at 224-288 px
   scoring 0.94-0.954 public, with label work (soft labels, out-of-fold pseudo-labels) as
   the main lever (participants' claims, several independent authors).
4. **The public stack's weights are tuned to the public LB.** Expect shake-up risk; a
   blend with an independently validated model is also a hedge for the private LB.

## 4. Recommendation

**v05 = a faithful reproduction of `jiweiliu/rsna-knee-fast-2xt4-inference` v11** as
`notebooks/v05-public-stack-anchor.ipynb`, inference only, unchanged weights, with a
provenance cell and pinned dataset versions. Use it as the anchor for every later blend.

Why this one:

- Highest score (0.943) among notebooks whose inputs are all public; #1-#3 cannot be
  reproduced.
- It is the parent of the 0.945-0.946 notebooks, so their extra-leg pattern drops in
  unchanged (the blend code in #1 is about 60 lines and already has fallback gates).
- Most-forked and best-documented 0.943 version (changelog of every weight change; versia-5
  and maverick give readable maps of the same stack).
- Engineered for the 9 h / 2 x T4 limit, which leaves room for our own model.

Rejected alternatives: the root (#5) has the same models but slower scheduling and an
unidentified scored version; versia-5 / DINOsaur V5 add nothing measurable over #4; Tony
Li's bundle is cleaner but 0.003 lower; building our own model from scratch as the only
submission gives up the free 0.943 floor three weeks before the deadline.

### Reproduction cost

- Training: none. Engineering: copy the notebook, add provenance and our version string,
  keep the 18 inputs (all public), no logic changes. About half a day including validation.
- Kaggle: one GPU commit run (~5 min on the 3 placeholder studies) and **one submission**
  to confirm 0.943 and measure the real hidden-test runtime (unknown; must stay below 9 h
  with headroom for our own leg). Requires your approval before pushing or submitting.
- Risks: dataset versions can change under us (the notebook hash-pins most assets and
  fails loudly, which is good); a failed CoAt child silently lowers the score instead of
  failing; T4 queue delays.

### Three most promising directions after reproduction

1. **Train our own diverse model and rank-blend it into the anchor (~0.4-0.5 weight).**
   Strongest evidence (#1, #3: +0.002-0.003 public). Start with a single 2.5D CNN
   (ConvNeXt-tiny or EfficientNet, 224-320 px, 130-150 mm crop, sagittal/coronal/axial
   slots, soft LLM labels), StudyInstanceUID-level folds, single fold end-to-end first.
   Romantamrazov's public ConvNeXt trainer is a usable template. Diversity matters more
   than its standalone score, but we cannot measure that diversity directly: the public
   checkpoints were trained on the training studies (any comparison there is in-fold) and
   hidden-test logs are not visible. The blend weight will have to be set a priori (the
   0.45-0.5 used by #1/#3) and confirmed by one public-LB submission.
2. **Label work for that model: soft multi-source labels plus out-of-fold pseudo-label
   bootstrapping.** Combine public LLM label tables (pilkwang, stevenleehans, lixin73),
   treat "not addressed" differently from explicit negatives, then mix our own OOF
   predictions 50/50 into the soft targets and retrain. Several high scorers name this as
   their main lever; it is cheap (no new data) and targets the weak findings (Synovitis,
   Lateral OA, PF OA).
3. **Robustness and runtime of the anchor.** (a) Measure the anchor's real runtime and use
   the existing `sparse` window preset (maverick) if needed to make room for our leg;
   (b) check the bf16-on-T4 path in the A5 stage, which a forum report links to silent AUC
   loss; (c) prefer simple, pre-declared blend weights over public-LB tuning for the final
   private submission. Lower expected gain than 1-2, but low cost and it protects the
   private score.

## 5. Questions for the user

1. Accept `jiweiliu` v11 as the v05 anchor, unchanged?
2. OK to push the v05 notebook to Kaggle (private) and spend one submission on it?
3. For direction 1: budget per week of Kaggle GPU hours we can spend on training, and
   whether you want to aim for the Efficiency Prize (it would favour a single fast model
   over the 2 x T4 stack).
4. External knee MRI datasets (MRNet, OAI, fastMRI): stay out unless the host clarifies?
   Recommendation: stay out.
