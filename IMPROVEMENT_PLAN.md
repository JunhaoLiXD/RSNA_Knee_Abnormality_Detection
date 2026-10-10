# Improvement Plan

Directions for improving on the v05 public-stack anchor, in priority order, each with
the reason behind it. Written 2026-10-01 after the baseline survey
(`docs/research/baseline-selection.md`, `docs/research/discussion-key-findings.md`);
revised 2026-10-04 after v09/v10 per `docs/research/v11-strategy-revision-design.md`
revision 2.1 (D-014), and 2026-10-06 after v12 per `docs/research/v13-strategy-revision-design.md`
revision 3.1 (D-015), and 2026-10-08 after the anchor swap (D-019) and the v19/v20 fusion design.
Update this file when a direction is started, finished, or dropped;
record results in `docs/experiments.md` and decisions in `docs/decisions.md`.

**Before editing this file, read `docs/STATUS.md` (D-011, D-012)** and cite the versions
and lessons behind each change. "STATUS L<n>" below is lesson n of that file.

Status 2026-10-06: Priority 0 done (v05 0.943). Priority 1 tried as v08-v10 and did not
help (v09 0.932, v10 leg alone 0.909). Priority 2 done: the v11 leg scores 0.931 alone (v12),
below the 0.935 blend gate. **Active: Priority 2b, round-2 teacher and an MRI-pretrained second
model (v13, D-015).** Status 2026-10-07: Gate F0 kept N only (MRI-CORE arm M gold 0.881, below
the floor); step D passed (v14, N fold 0 alone, 0.934 >= 0.933, STATUS L17); N folds 1-4 next.
Status 2026-10-08: Priority 2b done (5-fold N leg 0.936 alone; v15 blend 0.944, STATUS L18).
**Active: Priority 5**, the OAI-based public anchor (v17 0.950, D-019) with our leg blended in (v19
0.950 at w 0.15; v20 0.949 at w 0.25). Status 2026-10-09: **Priority 6 active** (D-020): the
external-levers shortlist v21-v25.

## Goal and constraints

- **Goal: a medal.** On the 2026-10-01 public board (4,730 teams) bronze (top 10%) sits
  inside the 0.943 tie block shared by about 1,000 teams, silver (top 5%) needs about
  0.945, gold (top 10 + 0.2%) about 0.956. Because so many teams sit on the same public
  stack, the realistic target is **public >= 0.946 with a model we trust on the private
  set**, which should hold a bronze through shake-up and has a chance at silver.
- **Compute: 30 Kaggle GPU hours per quota window.** Windows reset on Saturdays at 00:00 UTC
  (10-03, 10-10, 10-17); `kaggle quota` shows the usage. Submission scoring reruns do not count
  (checked 2026-10-04: 0.18 h used after the v09 and v10 scoring runs, 29.82 h left until 10-10).
  Since 2026-10-07 also a local RTX 3080 Ti for training (D-016; about 2.5 h per ConvNeXt-tiny fold,
  STATUS L19); submissions and their inference stay on Kaggle.
- **Board on 2026-10-08:** 5,537 teams; bronze and silver cut ranks (553, 276) both sit inside the
  0.950 tie block, so ranks inside the block are decided by unrounded scores (STATUS L22).
- **Dates:** entry and team-merger deadline 2026-10-15; final submission 2026-10-22.
- **Submissions:** 5 per day; two final selections.
- **External MRI datasets:** considered and deferred for this round (design v11 section 3.1;
  see "Not planned").
- **Team merger:** the user's decision, open until 2026-10-15 (design v11 option E).

## Priority 0 - Reproduce the anchor (v05) - done

**Result.** v05 (jiweiliu v11 unchanged) scored **0.943** on 2026-10-01 and is the only safe
final pick today (STATUS v05). The commit run took 233 s; hidden-test scoring took more than
5 h, which leaves under 4 h of the 9 h limit for any leg added to the anchor (STATUS v05
anchor table, D-008).

## Priority 1 - Our own diverse model, rank-blended into the anchor - tried, did not help

**What was done.** v06 (DICOM audit, slot selection, 4-source soft targets, scanner-grouped
folds), v07 (320 px JPEG cache), v08 (ConvNeXt-tiny 2.5D, 5 folds, K_train 4, K_infer 16),
then v09 (anchor + v08 rank blend at w = 0.45) and v10 (v08 leg alone). Settings are in the
STATUS settings ledger.

**Result.** v08 CV 0.840 (scanner-grouped pooled OOF), gold-58 0.897; v09 **0.932** (-0.011
vs v05); v10 **0.909** (STATUS v08-v10). The pipeline is sound: test-time preprocessing is
byte-equal to the training cache and coverage was 100% (STATUS L5), so the shortfall is model
quality.

**What it taught.**
- The original premise "it does not need to be strong on its own" (the 0.945 leg had weak-label
  CV about 0.90) is contradicted: a 0.909 leg at w = 0.45 lowers the 0.943 anchor by 0.011
  (STATUS L2). Blending is now gated on the leg's standalone public score (Priority 2).
- Gold-58 tracked the public LB (0.897 -> 0.909) and a forum report puts a 0.950-LB model at
  about 0.930 on the same gold set, so the 0.03 gold gap was an early warning (STATUS L3).
- The model did not exceed its labels on gold (0.897 vs 0.892 for the target; STATUS L4).
- More inference coverage helps (K_infer 4 -> 16: +0.021), more training tokens did not
  (K_train 8 vs 4; STATUS L6).
- A full cycle costs about 3 days and 14 GPU h plus scoring (STATUS L8).

The v06/v07 data path and the v08 trainer are reused by Priority 2.

## Priority 2 - OOF-teacher targets for our model (v11) - done (D-014)

**Result.** Gate R1 picked arm B (15 epochs, 2x LR; gold 0.911 vs arm A 0.895); the 5-fold leg
reached gold 0.913 and pooled OOF 0.875, and scored **0.931** alone on the public LB (v12), +0.022
over v10 but below the 0.935 gate, so no blend (STATUS v11, v12, L10, L13, L15). Teacher targets
alone did not move gold (L9); more optimisation did (L10). The plan below is kept as a record.

Item 1 of the original Priority 2 (combine several public label tables into one soft target)
was done in v06: the mean of four tables, which itself scores 0.892 on gold (STATUS settings
ledger). This priority is now item 2, mixing our out-of-fold predictions into the targets.

**What.** Design `docs/research/v11-strategy-revision-design.md` revision 2.1:

1. **v11 fold 0, two arms in one session** (two T4s): targets `0.5 * soft + 0.5 * v08 OOF`
   (K_infer 16), per-cell weights unchanged, gold never trained on. Arm A: 10 epochs, LR 5e-5
   backbone / 2e-4 head. Arm B: 15 epochs, LR 1e-4 / 3e-4. Time limits 6 h (A) and 9 h (B),
   global deadline 11 h; an arm that stops early is incomplete and excluded. Every evaluation
   also scores 500 fixed training studies at K_infer 16 without augmentation, so training and
   validation loss are compared like-for-like.
2. **Gate R1** (pre-registered): complete arms, then qualified arms (fold-0 val macro AUC at
   K_infer 16 >= 0.871, v08's value), then one arm picked by gold-58 (arm A if within 0.005 of
   the best). Picked arm gold >= 0.915: train folds 1-4; [0.905, 0.915): train folds 1-4 only if
   the weekly quota covers them plus 20%; otherwise stop own-model work. If no arm completes,
   one rerun of arm A.
3. **v11 folds 1-4** with the picked arm, then **v12_submit = leg alone**.
4. **Blend gate on the leg alone** (replaces the old fixed weights of 0.45-0.5): v12 >= 0.940:
   v13_submit = anchor + leg at w = 0.45; [0.935, 0.940): w = 0.30; below 0.935: no blend.
5. **Second iteration** (round-2 targets from v11 OOF) only if v13 beats max(v05, v12) and it
   can start by 2026-10-09.

**Why.**
- On gold-58 the v08 model and the soft target are complementary: the model is better on
  diffuse findings (effusion 0.975 vs 0.863, contusion, fracture, medial OA, Baker's), the
  labels on small structures (ACL, MCL, lateral meniscus). A pre-registered 50/50 mix scores
  **0.917**, +0.027 over the target alone (paired bootstrap 95% CI +0.010 to +0.045;
  design 2.2). This is the only measured gain we have, and it addresses STATUS L4 directly.
- Several high scorers on the forum independently name OOF pseudo-labels, about 50/50 and
  kept soft, as their main lever; in-fold predictions only repeat the labels.
- The OOF predictions already exist for all 4,349 non-gold studies (v08), so the change costs
  no new data or inference.
- Arm B tests the under-optimisation hypothesis: v08's val AUC was still rising at epoch 10
  while the cosine schedule reached zero (fold 0: 0.8666, 0.8679, 0.8683 at epochs 8-10;
  STATUS settings ledger). This is a hypothesis, not a finding: the logged training loss is
  not comparable with the OOF loss (design 2.1), which is why v11 measures both like-for-like.

**Evidence against, and how it is handled.**
- Weak legs hurt the anchor (STATUS L2): blending is gated on the leg-alone score (item 4).
- The teacher saw the student's validation labels (indirect leakage; design 3.2), so fold
  validation is mildly optimistic: decisions use gold-58 and the leg-alone public score.
- Gold-58 is small (CI half-width about 0.03; STATUS v08) and becomes a selection set once R1
  uses it; the leg-alone public score is the independent test.
- More training tokens did not help in v08 (STATUS L6): arm B raises epochs and learning rate,
  not K_train.
- The student may not inherit the teacher-mix gain; v12 measures it directly.

**Cost.** About 19-25 GPU h for the first iteration (fold 0 about 7.7 h; folds 1-4 about
9.8 h with arm A or 15.4 h with arm B; v12/v13 under 1 h each plus scoring), up to 31 h with
the R1 rerun. Degradation if the quota is short: drop the training-subset loss in folds 1-4,
then arm A instead of B, then stop.
**Done when.** v12's leg-alone public score is recorded and the blend decision of item 4 is
applied; v05 stays the final pick until something beats it on the public LB.

## Priority 2b - Round-2 teacher (N) and an MRI-pretrained second model (M), v13 - done (D-015)

**What.** Design `docs/research/v13-strategy-revision-design.md` revision 3.1:

1. **Step S** (about 0.5 GPU h): smoke test of the arm-M configurations (MRI-CORE ViT-B at 224 px,
   fallback ImageNet EfficientNet-B3) with key, gradient, loss and reload checks; admission by the
   budget formula (about <= 6.65 h per fold with the current quota).
2. **Step F0**: fold 0, arm N (v11-B recipe, target `0.5 soft + 0.5 v11 OOF`) and arm M (same
   target), one session within the 8.80 h left before 2026-10-10.
3. **Gate F0**: base = N if it beats v11 fold 0 on gold by >= +0.003 (exploratory); candidate C adds
   M if the deployed rank mean beats base by >= +0.003; C = v11 fold 0 alone means stop.
4. **Step D**: `v14_submit` = C's fold-0 models alone; continue only if the public LB >= 0.933 (a
   resource-allocation threshold).
5. **Folds 1-4**, inference-time gate for blends that include M (measured v09 duration), then
   `v13_submit` leg alone and `v15_submit` blend under the v11 4.4 gate (design names `v15_submit` /
   `v16_submit`, renamed by D-017); pre-registered terminal
   states if components cannot finish by 2026-10-20.

**Why.**
- The round-2 target scores 0.9235 on gold vs 0.9168 for the v08-teacher target (+0.0067, CI
  +0.0009 to +0.0130; design 2.3); it needs no API or new data and tests the under-learning
  explanation (STATUS L10).
- The v11 leg is redundant with the anchor (STATUS L15, L16): a second model must bring a
  different pretraining domain or family; the anchor has ImageNet-DINOv2, RadImageNet ResNet-50
  and CoAtNet, while MRI-CORE is MRI-pretrained (Apache 2.0, knee included;
  `external-pretrained-2026-10-06.md`).
- Folds of one model agree (STATUS L13), so a fold-0 leg-alone submission is an affordable early
  check before 13-28 GPU h of further folds.

**Evidence against, and how it is handled.**
- A better target need not give a better student (STATUS L9): step D measures it after one fold.
- Gold is small and reused (STATUS L3, L13): gold gates are exploratory screens; the public LB
  (steps D and P) is the external check.
- MRI-CORE adaptation risks: frozen configuration and correctness checks in step S; EfficientNet-B3
  fallback.
- The anchor proxy on gold is not a gate (its verdict depends on the proxy weights, STATUS L16).

**Cost.** Step S + F0 about 8.4 GPU h before 2026-10-10; folds 1-4 about 15 h (N-only or v11+M) or
about 31 h over two windows (N+M); commit runs under 0.1 h each.
**Done when.** v13_submit's leg-alone score is recorded and the blend gate applied, or a gate stops the
work; v05 stays pick 1 until something beats it.

**Result (2026-10-08).** Arm M dropped at Gate F0 (gold 0.881). Arm N: 5 folds (fold 0 on Kaggle,
folds 1-4 locally, D-016), gold 0.920 vs v11 0.913 (+0.007, CI +0.002 to +0.013); public 0.934 for fold
0 alone (v14) and **0.936** for 5 folds (v13_submit). Both pre-registered blends with v05 were submitted
at once (D-018): w 0.30 **0.944** (v15), w 0.45 0.943 (v16) (STATUS L17, L18).

## Priority 5 - OAI-based public anchor plus our leg (v17-v20) - active (D-019)

**What.** v17 = the public 0.950 notebook (CoAtNet-384 SWA trained with OAI + ConvNeXt reader)
unchanged; v18 = gold-58 diagnostic of its components; v19 / v20 = v17 output + our 5-fold N leg,
outer rank blend at w 0.15 / 0.25 (`docs/research/v19-fusion-design.md` revision 2, Codex-reviewed).

**Why.** All public notebooks at 0.949-0.950 share this checkpoint; without it the frontier is our
0.944 (STATUS L20). On gold our leg is about as different from the CoAtNet as the reader that adds
+0.001 on the LB (STATUS L21).

**Result.** v17 0.950; v19 0.950 (tie, kept per the decision rule); v20 0.949 (rejected). The leg adds
about nothing to this base (STATUS L21). Rank 268 of 5,543 on 2026-10-09 and sliding.

**Risk.** The OAI rule question is unresolved (topic 743416); the user accepted it (D-019). v15
(0.944, non-OAI) stays the second final pick as a hedge.

## Priority 6 - External levers and a stronger own model - done, no gain (D-020)

The fusion lever is nearly used up (STATUS L21): a 0.936 leg ties when added to a 0.950 base. Options
by pipeline stage were collected with Codex in `docs/research/external-levers-2026-10-09.md`; the
shortlist runs in order per `docs/research/v21-shortlist-design.md` revision 2:

1. **E6 `v21_submit`**: N in place of the public reader inside the v17 fusion (no training).
2. **E1 `v22`**: N with target T3 (CC0 Gemini report labels as a fifth source; gold +0.0036 over the
   round-2 target, CI -0.0015 to +0.0089); fold 0 locally, then a fold-0 LB check against v14 (0.934).
3. **E5 `v23` / `v25_submit`**: short adaptation of the public OAI CoAtNet through the v07 adapter
   (Stage 0 passed: Spearman 0.984 to the exact public pipeline).
4. **E4 `v24`**: own CoAtNet-rmlp-2 (ImageNet-12k, no OAI) in our pipeline; fold 0, full CV only at
   LB >= 0.937.
5. E7: optional mirror-TTA check for N.

**Why.** STATUS L20-L21 (the leg is redundant; gold cannot rank families, so LB checks are budgeted);
L4/L17 (target quality moved the student before); external-levers 2.1 (no public table beats our
mean, Gemini is complementary). Adoption over v19 / v15 needs +0.002 on the displayed public score.

**Result (2026-10-10).** No gain: E6 v21 0.949 (L26); E1 v22 equals v13 fold 0 (L23); E5 v23 not
admitted (L24); E4 v24 fold 0 0.934 = N fold 0, below the 0.937 gate, stopped (L27); E7 not run.
Superseded by Priority 7.

## Priority 7 - Local views and a second CoAtNet input path - active (D-021)

After the verified public 0.954 (CoAtNet + an anatomy-anchored local-view model, `public-landscape-2026-10-10.md`),
the plan `docs/research/plan-2026-10-10-local-views.md` runs as designed in
`docs/research/v25-local-views-design.md` revision 2 (Codex-reviewed):

1. **I1 `v25_submit`**: the public CoAtNet through the exact pipeline and the v07 adapter, rank mean, then
   v17's reader fusion (no training; gold +0.0024 over v17).
2. **B1 `v26` / `v27_submit`**: N recipe with a second, central 100 mm view cropped from the v07 cache and
   the report-only target; fold 0 locally, then v17 + leg at w 0.15.
3. **B2 `v28` / `v29` / `v30_submit`**: the local view rendered from DICOM at 100 mm (new cache), same
   model; folds by the decision table (stop below 0.951; 2 folds at 0.951, 4 at >= 0.952).

**Why.** STATUS L23-L27: changing only the target (v22, v23) or only the backbone (v24) leaves our model
redundant with N, and N adds nothing to the OAI CoAtNet (L21, L26); the 0.954 model differs from ours in
views and supervision. L24: the v07 adapter reproduces the public checkpoint, so a second input path costs
no training. Adoption over v19 needs a displayed 0.952; large experiments stop 2026-10-19.

## Priority 3 - Anchor robustness and runtime

**What.**
1. If the anchor plus our model exceed the time limit, switch the anchor to fewer eval
   windows (the `sparse` 62/42 preset documented in `maverickss26/rsna-knee-0942-restructured`).
2. Check the stack's A5 stage, which uses bf16 autocast on T4 GPUs that have no native
   bf16: compare its predictions under bf16 and fp16 on a few training studies; if the
   rankings differ materially, run it in fp16.
3. **Final selection** (superseded on 2026-10-08: picks are v19 + v15, see STATUS and D-018/D-019;
   original text kept below) (two picks by 2026-10-22, over the measured candidates v05, v12, v13;
   replaces "pre-declared blend weight plus a conservative variant"): pick 1 is the highest
   public LB; pick 2 is the highest of the other kind (anchor-based v05/v13 versus own-only
   v12), so one pick contains the anchor and one does not when both exist; a blend stays a
   candidate only if it beats max(v05, v12). No per-target weight tuning on the public board.

**Why.**
- The 9-hour limit is hard: a submission that times out scores nothing. Anchor scoring alone
  took more than 5 h (STATUS v05).
- The stack silently drops a CoAt reader that fails; a lower score instead of an error is
  easy to miss, so runtime and memory headroom matter.
- A forum report links bf16 on T4 to a silent AUC drop (0.851 -> 0.710 in their model).
  Whether it affects this stage is unknown; the check is cheap.
- Per-target retuning is what moved the public stack from 0.941 to 0.943; on about 1,300
  test studies such gains are close to noise and do not carry to the private board.
- The selection rule follows v09: a blend can be worse than its parts (STATUS L2), so a strong
  leg alone must stay selectable (Codex review finding 3, design section 7).

**Cost.** Under 1 GPU hour for the bf16 check; the rest is submissions.

## Priority 4 - A second own model - now arm M of Priority 2b

**What.** A second model that differs from the first in backbone family or input
geometry (e.g. a ViT/DINOv2 fine-tune, or a different crop and resolution), added to our
leg before blending.

**Why.** `d4-blend` used a group of three student models and scored higher than the
single-model `knee-s75-w50` (0.946 vs 0.945), which suggests more independent models keep
adding. It only makes sense once Priority 2 has produced a leg that passes the leg-alone gate
(>= 0.935); v08's folds were highly correlated (gold Spearman 0.92, STATUS v08), so diversity
has to come from a different model, not more folds. A bigger backbone or higher resolution
(design option G) is deferred for budget, not ruled out: revisit if v11's like-for-like losses
show a capacity limit.

**Cost.** 10-15 GPU hours for 5 folds.

**Update 2026-10-06.** Moved into Priority 2b as arm M with an MRI-pretrained backbone (STATUS L16;
the d4 comparison above is not evidence for own-model ensembles, since both notebooks include the
anchor, Codex review of design v13).

## Not planned, and why

- **Retuning the public stack's weights on the public board:** about 1,000 teams already
  hold this score; the gains are at noise level and overfit the public split (STATUS L1).
- **Single-finding specialists:** `romantamrazov/rsna-knee-dinosaur-v5` added a Medial
  Meniscus specialist and stayed at 0.943.
- **Public checkpoints not in the anchor** (DINOv3 members, other Raptor checkpoints): a public
  bundle with DINOv3 scores 0.940 < 0.943, and choosing them by public LB is the overfitting
  route (design v11 option D).
- **External knee MRI datasets** (checked 2026-10-04, design v11 section 3.1): MRNet and
  KneeMRI mostly cover ACL, where our labels are already excellent (gold 0.99), and carry
  no-derivative clauses; fastMRI+ covers our weak findings but is a single coronal plane in
  about 1 TB of files; the host has not published an allow-list. Revisit only if the host
  allows a dataset and Priority 2 has been tried. Any registration is the user's to do.
  Rechecked 2026-10-06 (`external-pretrained-2026-10-06.md`): still no host answer (topic
  743416); KneeCoT ruled out by the host. MRI-pretrained public weights (MRI-CORE) are used
  instead (Priority 2b). Since 2026-10-08 public weights trained with OAI are used as the anchor
  (D-019, Priority 5); training on OAI ourselves is still not planned (access is institution-gated).
- **Distilling or fine-tuning the anchor's public members:** their training-set OOF is weaker than
  ours (0.851 vs 0.875 against the soft target) and copying them would raise the correlation with
  the anchor (STATUS L15, L16).
- **Own LLM report labels** (design v13 option L): not pursued, user decision 2026-10-06.

## GPU budget (30 h per quota window)

| Quota window (UTC) | Used / planned GPU use |
|---|---|
| 2026-09-26 to 10-02 | Used: v05 commit, v06/v07 (CPU), v08 fold 0 and folds 1-4 (6.5 h + 7.6 h) |
| 2026-10-03 to 10-09 | Used: v11 fold 0 (7.5 h), folds 1-2 (6.5 h), folds 3-4 (7.0 h), v12 commit; 8.80 h left on 10-06. Planned: v13 step S (0.5 h) and fold 0 (<= 7.9 h) |
| 2026-10-03 to 10-09 (actual) | ... plus v13 step S and F0 (about 6.6 h), v14/v13/v15/v16/v17/v19/v20 commits and v18 (under 0.2 h each); v13 folds 1-4 ran locally instead (D-016); 1.80 h left on 10-08 |
| 2026-10-10 to 10-16 | Commit runs for Priority 5/6 submissions; Priority 6 training mostly local, Kaggle GPU for anything the local GPU cannot run |
| 2026-10-17 to 10-23 | Priority 6 if approved; final selection by 10-22 |

Scoring reruns do not count against the quota (checked 2026-10-04 with `kaggle quota`); keep a
few hours of margin per window for reruns of failed sessions.
