# Aggressive routes above the 0.954 block: independent proposals, cross-review, consensus (2026-10-12)

Status: discussion note, no decision yet. User request 2026-10-12: Claude and Codex (GPT-6 Astra, high, read-only, web
search on) each propose, without seeing the other's text, what the teams far above us do and which aggressive options could
give a large gain (failure acceptable); then review each other and converge on what is worth trying. Any GPU training that
follows needs its own design note and decision (D-004); this note does not reopen the leg line closed by D-029 or extend
D-030's cap. Evidence cited from STATUS: v08, v11, v13, v14, v17, v32-v39, v36; lessons L9, L10, L17, L19, L20, L21, L23,
L26-L31.

## 1. Situation

Leaderboard 2026-10-12 13:05 UTC (`external/lb/2026-10-12e`): 5,824 teams; top 0.966; 27 teams >= 0.961 (gold cut rank
21 at 0.962); 69 >= 0.958; 199 >= 0.955; 709 at 0.954 (silver cut rank 291 and bronze cut rank 582 inside the block); we
are rank 524 (v37 0.954). Of the top 60, 37 are solo; median submission count of teams >= 0.958 is 119 vs 23 at 0.954, but
several 0.960-0.964 teams have 2-35 submissions. 0.954 -> 0.958 means cutting the mean ranking error 0.046 -> 0.042
(-8.7%): about +0.016 AUC on each of three findings or +0.008 on six (Codex).

## 2. What the top teams most likely do (merged)

| # | Hypothesis | Evidence | Strength |
|---|---|---|---|
| 1 | Stronger complete training recipes for own models (0.950-0.959 per architecture), mainly better handling of noisy supervision: out-of-fold pseudo labels mixed into report labels (heavier towards the model than 50/50), soft targets | Forum 735304 (claims): azamat1ch ConvNeXt-T 5-fold 0.959; colum2131 ConvNeXt-T 0.953 / DINOv2-S 0.951 / pair 0.955, pseudo labels, no external data; CoolinLai ResNet-50 5-fold 0.954; Archit Konde CoAtNet single fold 0.950; k256.dev fold 0 0.947 with LLM labels only. Ours: v10 0.909 -> v12 0.931 -> v13 0.936 -> v36 P 0.937 | consistent claims from about eight posters; not reproduced |
| 2 | Better use of anatomy, sampling and auxiliary tasks | S6 (verified): up to 176 training windows per study, batch 2, 16 epochs, head LR 10x, non-zero state gates and OA-extent branches (Codex, checkpoint read), `E_lrprior` likelihood-style loss; our N: 20 tokens per step, head LR 3x; v07 thins 30.6% of slot entries (AX_FS 47.9%) | verified differences, unattributed |
| 3 | A few strong complementary models rather than many weak ones | v32/v37 0.954 with S6; v35 six-model leg 0.953, v39 no gain (L21, L26, L31) | ours |
| 4 | External image supervision on weak findings (OAI) | nartaa: +0.005 from 2,399 OAI knees on three findings, not compute-matched (746792) | claimed |
| 5 | More experiments and public-LB selection | submission counts | part of the visible lead; private value unknown |

Corrections from the cross-review (verified by Claude): the public CoAtNet trained with **12 windows per study** (94 only at
inference; `external/forum/topic_746792.txt` line 42) with head LR 0.00195 vs backbone 4.01e-5 (about 49x), so dense
training is **not** shared by both strong models; the shared feature is a **much faster head** (CoAtNet 49x, S6 10x, ours
3x). S6's `freeze_blocks 16` applies only to the ViT (OFL) path; its ConvNeXt-small trains fully
(`compact_train.py` lines 233-247).

## 3. The two independent proposals (short)

| Claude | Codex |
|---|---|
| A dense-bag retrain of N (K_train 16, frozen early stages, head LR 10x, P target); B patient-identity probe; C heavier pseudo-label round; D team merger (user's call); E VLM (not now); F per-finding LB probing (not aggressive) | A **S6 held-out teacher** (S6 folds are `sha1(uid)[:8] % 4`, verified in `compact_train.py` line 654) -> new student, then DINOv2-S student; B native-resolution disease ROI specialists for six findings; C report-state multitask with matched hard negatives |

## 4. Cross-review outcome

| Item | Outcome | Reason |
|---|---|---|
| Claude A (dense student) | **Kept, as a bounded test; its evidence is weaker than first stated** | Coverage of a 2-3-slice lesion per step with the actual stratified sampler is 50.5% / 61.7% at K 4 (86% / 95% at K 8; 100% at K 16; exact integration and Monte Carlo by Codex). v08 K 8 vs K 4 at 320 px completed 98% of K 4's optimizer steps and was behind at every matched epoch from 5 (epoch 8: 0.8642 vs 0.8679), and v36 G (K 8 at 224 px) was -0.0005: two negative signals for K 8 on report-label validation. K 16 with a 10x head LR has never been run. Our `train_blocks_from` freeze only works for ViT (`bb.blocks`); a stage-level ConvNeXt freeze must be added. Throughput is data-bound (P: 158 img/s, data share 0.46, Windows commit peak 35.9 GB), so plan up to 8 h per fold and do not raise loader workers (L19) |
| Claude B (patient identity) | **Dropped** | heliosli's audit reads PatientID but publishes no result; `exact_duplicates.py` works within a study only; three placeholder test studies cannot show hidden-test overlap; identity-based label transfer is a leak exploit with rule risk |
| Claude C (heavier pseudo labels) | **Dropped for now** | rank means are not probability targets; a full OOF of a new model does not exist yet; the S6 teacher is the better teacher test |
| Claude D, E, F | D the user's call (declined earlier); E not this week; F conflicts with D-030's non-renewable cap | - |
| Codex A (S6 teacher -> student) | **Kept**, student trained with the same dense recipe | the strongest available teacher with a recoverable held-out assignment; L17 (a teacher change moved our student) vs L21 (a student copying the anchor adds little; v37 is half S6). Teacher cost: v34 measured 18.23 s per study per GPU for four models, i.e. about 17 GPU h for the 3,402 fold-0 training studies; one model per study saves model time but not DICOM decoding and localisation, so a 150-study pilot must measure it. Leakage: S6's own targets (`opusv11b_rr3_plv21_cdr`) may contain earlier all-fold pseudo-label rounds (size unknown); the student's validation is not evidence, the LB decides |
| Codex B (ROI specialists) | **Withdrawn by Codex** | raw-DICOM caches, localisation QC and inference integration cannot deliver a first result within 48 h |
| Codex C (state multitask) | **Deferred** | S6 already carries state branches; new losses and pair mining enlarge the surface |
| Codex's DINOv2 second student | **Removed this week** | prove one student's blend value first |

## 5. Consensus plan (for the user's decision)

Frozen dense recipe (both students identical except the target): ConvNeXt-tiny ImageNet init, v07 320 px / 140 mm, five
slots, **K_train = K_infer = 16**, 15 epochs, seed 2026, effective batch 8, **LR backbone / head 1e-4 / 1e-3**, stem and
stages 0-1 frozen, stages 2-3 and the head trained with gradient checkpointing; everything else as P. Micro-batch 2 x
accum 4, single fallback 1 x 8, fixed after the smoke run.

| When | Step | Where | Kill / gate |
|---|---|---|---|
| 10-12 | D-030 continues unchanged (v40 and W scoring; v41 after v40's comparison) | Kaggle | D-030 rules |
| 10-12 | Dense-recipe smoke: frozen parameters unchanged, gradients in stages 2-3, peak memory, throughput | local | stop the dense line if a fold projects above 8 h or the fallback is unstable |
| 10-12/13 | **Dense-P fold 0** (target = P's round-3 target) | local, <= 8 h | - |
| 10-12/13 | **S6 teacher pilot**: 150 training studies, each scored only by its held-out fold model; check the hash assignment, raw probabilities, branches, coverage and the quota actually charged | Kaggle | cancel the S6 student if the full fold-0 teacher projects above 10 GPU h |
| 10-13/14 | S6 teacher for the fold-0 training studies (differences from the author's 4,344-study pool listed, nothing dropped silently); **Dense-S6 fold 0** (target `0.7 S6 probability + 0.3 report soft`) | Kaggle; local | - |
| 10-13/14 | Each student alone on the LB (fold 0) | 2 submissions | both < 0.944: the new line ends |
| 10-15/16 | Better of the two (tie: Dense-P): **v37 : student = 0.75 : 0.25 rank blend**, fixed, not stacked on v40/v41, no per-finding search | 1 submission | adopt by D-030's rules (display or rank crossing) |
| 10-16/18 | Only if that blend displays >= 0.956 and above the incumbent: folds 1-2 locally, three-fold student at the same outer weight | 1 submission | no gain: keep the one-fold blend (L31); no automatic five folds |
| 10-19 | Model development stops; full-run time measured and extrapolated (1.5x margin <= 6.5 h) | - | 10-20/21 final verification |

Budgets: local GPU <= 46 h (smoke 2, two fold-0 runs 16, conditional two folds 16, reserve for D-030's conditional v36
work 11, verification 1); Kaggle <= 20 GPU h (teacher 10, top-up 2, commit runs and diagnostics 3, D-030 2, failures 3),
capped by the quota actually left before the 2026-10-17 refresh; **this line: at most four submissions** (two students,
one fixed blend, one conditional expansion), unused ones lapse, at most five per day in total; candidate scorings for the
anchor stay sequential. D-030's own cap of five is unchanged and cannot be triggered by this line. If nothing passes,
the picks stay D-030's qualified winner or v37, plus v15; an S6-taught student is not an independent hedge.

Expected value, stated plainly: the most likely outcome of each step is no breakthrough; the joint chance that a fixed
blend displays >= 0.956 is low (both reviewers put individual routes at roughly 10-20% before these corrections).

## 6. Remaining disagreements

| Point | Claude | Codex |
|---|---|---|
| Strength of the density hypothesis | a plausible mechanism worth one run | weaker: K 8 was negative twice; only one bounded test |
| Kill rule on validation | first proposed `val >= P + 0.003` | rejected (teacher-leaky, report-label proxy); Claude accepts: the LB decides |
| Identity probe | cheap to look at | not a scoring route this week; Claude accepts |

## 7. Follow-up (user question): is the top teams' advantage an architecture we cannot get?

**Architectures are public and small.** Forum posters who are now near the top name standard timm backbones (claims, not
reproduced; ranks from `external/lb/2026-10-12e`): azamat1ch (team rank 4, 0.964, 29 submissions): ConvNeXt-T 5-fold 0.959,
EfficientNetV2-S 0.956, CoAtNet 0.952; coolinlai (in the rank-21 team): ResNet-50 224 px 5-fold 0.954; tuckerarrants (in
the rank-22 team): ResNets/EfficientNets, 224/288 px "sweet spot"; tennogh (in the rank-7 team): 288 px with OOF pseudo
labels; andy2709 (rank 30): Qwen 3.5 2B + LoRA single fold 0.950. ConvNeXt-T is **our** backbone (N: fold 0 0.934,
5 folds 0.936), so the 0.02 gap at equal capacity is in the recipe (labels, pseudo-label rounds, sampling, optimisation,
preprocessing), not the architecture. The rules require external models and data to be publicly available, so a legitimate
top solution cannot rest on a private in-house model; nothing in the evidence points to one.

**Two complete strong recipes are public and in hand:** heliosli's S6 training code (`compact_train.py` and 820 files) and
nartaa's CoAtNet training script with labels and folds (`external/datasets/nartaa__rsna-knee-hpo-assets/`: `train_knee.py`,
`labels_v1_blend.parquet`, `folds_v0.json`). nartaa's own history (746792): all-data CoAtNet 0.939 -> 0.940 (96 slices,
native 384 cache, 94 windows) -> 0.942 (label blend + JEV labels) -> 0.945 with OAI -> 0.949. Without OAI that public recipe
is 0.940-0.942 for one all-data model, above our 0.936 five-fold N; its settings differ from ours in head LR (0.00195 vs
backbone 4.01e-5, about 49x; ours 3x), all-data training, three-epoch weight averaging and labels.

**Is "more model complexity does not help" wrong?** Supported as a statement about *our current pipeline*: our CoAtNet-rmlp-2
equalled N (L27), MRI-CORE ViT-B was worse (v13 arm M), a forum team reports +0.0011 from scaling the encoder (735154) and
another seven architecture ablations within 0.008 (735304), lumbar 2024 1st place found ConvNeXt-small > base > large; and
N is not underfitting (v11 B: training-subset AUC 0.923 vs validation 0.898, L10). Not established as a general law: once
the recipe bottleneck is removed, capacity can matter again (S6 uses ConvNeXt-small at 384 px with up to 176 windows), and
study-level aggregation (cross-slice / cross-series modelling) is barely tested by us. Verification: one controlled fold-0
arm (ConvNeXt-small in our trainer, everything else as the chosen recipe; about 4-5 h locally, one LB slot), best run
after a recipe change has moved our model, because before that it would most likely repeat L27.

## 8. GitHub search for the top teams' code (user request, 2026-10-12)

Method (read-only, `gh` API): 14 queries for repositories pushed after 2026-08-01 -> 286 knee/RSNA repositories; repository
owners matched against all 6,725 leaderboard usernames; the same-name GitHub accounts of every member of the top-100 teams
checked for recently pushed repositories. Same-name accounts are only presumed to be the same person.

- **Top 60 teams: no public code for this competition** (most members have no same-name account or only unrelated recent
  repositories). No repository owner from the top 500 matches a leaderboard username (best match: rank 595).
- **One top-100 team publishes everything**: `github.com/VaryaStrizhneva/RSNA-project` (team rank 89, 0.957, 2 members,
  45 submissions; **no licence**, so ideas only: no code or annotation reuse). Their log (`docs/experiments.md`, read):

| Their row | What | Public LB |
|---|---|---|
| #31 | heliosli S6 verbatim (= our v32) | 0.954 |
| #32 | + their per-finding ROI "experts" (resnet18), per-column rank blend 0.5 | 0.953 |
| #33 | same experts with a **convnext_nano** encoder, one variable | **0.957** (rank 173 -> 61 at the time) |
| #34 | blend 0.6 | 0.956 |
| earlier | experts on nartaa's CoAtNet: 0.949 -> 0.951; on the old public stack 0.940 -> 0.944 | - |

  Experts: one model per finding for eight columns (Lateral/Medial Meniscus, ACL, MCL, Medial/Lateral/PF OA, Baker's
  axial) on anatomy-shaped boxes cut around landmarks in patient millimetres, at native resolution 0.21-0.29 mm/px (a
  1.5 mm tear spans 5-7 px; our v07 cache 0.44 mm/px); landmarks from a heatmap model trained on about 170 manually
  annotated studies; about three weeks of work. Out-of-fold, the per-column gain tracks the host's weakness (Lateral
  Meniscus, ACL, PF OA, Medial Meniscus pay most). Their measured zeros match ours (L23 etc.): label tables and their
  fusion, per-column weight schemes, more epochs, extra planes for existing experts, the old stack's 28 models. Their
  conclusion, consistent with L21/L26/L31: "against a 0.954 host the only thing that pays is being better, not being
  different". Encoder quality paid at the expert level (convnext_nano vs resnet18: +0.0056 column AUC, t 3.56 over 40
  paired folds; +0.004 on the LB), a counterpoint to "capacity does not matter" (section 7).

**Implication.** This is the most direct evidence so far for a route from our exact base (v32/v37 = S6 + CoAtNet, 0.954) to
0.957: per-finding high-resolution ROI specialists, blended per column. It revives Codex's withdrawn option B on evidence,
but not on feasibility: we have no local DICOMs; ROI rendering needs Kaggle; our localisation would have to come from S6's
public anatomy/anchor code (`anatomy.pt`, accepted by D-023 for S6 only, so a new decision), and the team needed about three
weeks. Any plan built on it needs a feasibility probe first (what S6's anchor code returns per study, rendering cost per
study on Kaggle, cache size) and a Codex review.
