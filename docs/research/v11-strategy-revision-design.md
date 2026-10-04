# Design note: strategy revision after v09/v10 (v11 onward)

Date: 2026-10-04. Status: **revision 2.1, approved by the user 2026-10-04 (D-014)**.
Revision 2 answered the first Codex review (section 7); revision 2.1 adds two clarifications
made at approval, a corrected evaluation cost and the Gate R1 order (section 8), without
changing the direction. Grounded in `docs/STATUS.md` (D-011, D-012): versions table,
settings ledger and lessons are cited as "STATUS L<n>" (lesson n) or by version.

## 1. Where we stand

- v05 public stack anchor: **0.943** (STATUS, v05). Only safe final pick today.
- v08 own leg (ConvNeXt-tiny 2.5D, 5 folds): CV 0.840, gold 0.897; alone **0.909** (v10);
  blended at 0.45 with the anchor **0.932** (v09). A weak leg lowers the anchor (STATUS L2).
- Pipeline is sound; the problem is model quality (STATUS L5).
- Time: 18 days to the 2026-10-22 deadline; team-merger deadline 2026-10-15. Compute: 30
  GPU h per week; an anchor-based submission takes more than 5 h to score.

**Requirement for any new leg:** it must be strong enough alone to help the anchor. From
v09/v10 a 0.909 leg costs 0.011 at w = 0.45; the public 0.945/0.946 notebooks add legs whose
standalone strength is unknown but whose weak-label CV was about 0.90 on random folds. We
therefore gate blending on a **standalone public score of at least 0.935** (section 4.4).

## 2. Diagnosis of v08 (new local analyses, 2026-10-04, no GPU)

### 2.1 v08 may be under-optimised (hypothesis, tested by arm B)

Soft-target BCE, weighted as in training, over the 4,349 non-gold studies:

| Quantity | Loss |
|---|---:|
| Floor: entropy of the soft targets | 0.327 |
| Predicting each label's prevalence | 0.610 |
| v08 training loss, last epochs (fold 0 / fold 1) | about 0.46 / 0.46 |
| v08 pooled OOF loss | 0.496 |

These numbers are **not like-for-like**: the training losses are logged mini-batch values with
augmentation and 4 random centres per slot, while the OOF loss uses other checkpoints, 16 fixed
centres and no augmentation. So they do not show whether v08 over- or underfits, and the
entropy floor is a property of the report labels, not a loss an image model can reach. What
they do allow is a weaker reading: training ends far above the floor while validation AUC was
still rising at the last epoch
(fold 0: 0.8666, 0.8679, 0.8683 at epochs 8-10; fold 1: 0.8340, 0.8345, 0.8350) while the
cosine schedule reached zero. The verified 0.945 private leg builds its model with 24 slice
positions per slot (`n_slices=24`, decoded code), i.e. it trains on far more tokens per study
than our 20 (`K_train` 4 x 5 slots; STATUS settings ledger).

Caveat: v08's `K_train` 8 arm did not beat 4 at equal epochs (STATUS L6), so "more tokens"
alone is not supported; "more optimisation" (epochs, learning rate) is the better-supported
lever. v11 measures train and validation loss like-for-like (same checkpoint, no augmentation,
same `K` and weighting; section 4.1), which settles the over/underfitting question.

### 2.2 Model and labels are complementary on gold

Gold-58 AUC per label: v08 5-fold rank ensemble vs its own 4-source soft target.

| Label | Model | Soft target | Better |
|---|---:|---:|---|
| ACL | 0.956 | 0.990 | labels |
| MCL | 0.897 | 0.968 | labels |
| Medial Meniscus | 0.950 | 0.955 | tie |
| Lateral Meniscus | 0.800 | 0.878 | labels |
| Medial OA | 0.974 | 0.931 | model |
| Lateral OA | 0.783 | 0.808 | labels |
| PF OA | 0.842 | 0.903 | labels |
| Effusion | 0.975 | 0.863 | model |
| Synovitis | 0.749 | 0.788 | labels |
| Baker's | 0.964 | 0.947 | model |
| Contusion | 0.958 | 0.857 | model |
| Fracture | 0.915 | 0.815 | model |
| **Macro** | **0.897** | **0.892** | |

The image model is better on diffuse, image-visible findings; the report labels are better on
small structures the model does not yet see well (ACL, MCL, lateral meniscus).

A pre-registered 50/50 mix (from the forum recipe, not tuned on gold) of model and labels
reaches **0.917** (probability space) / **0.919** (rank space) on gold, **+0.027 over the soft
target alone (paired bootstrap 95% CI +0.010 to +0.045, P(gain <= 0) = 0.002)**. OOF
probabilities have the same per-label means as the soft targets (smaller spread), so a
probability-space mix is a usable training target.

This matches independent forum reports that blending out-of-fold model predictions into the
extracted labels (about 50/50, kept soft) and retraining was their main lever; in-fold
predictions do not work (they repeat the labels).

## 3. Options considered

| Option | Evidence for | Evidence against / cost | Decision |
|---|---|---|---|
| **A. OOF-teacher targets**: retrain on `0.5 * soft + 0.5 * v08 OOF` | Gold +0.027 with a tight CI (2.2); forum reports; OOF already exists for all 4,349 non-gold studies | Indirect leakage into our folds (3.2); gains on the target need not transfer fully to the student | **Do (arm A)** |
| **B. More optimisation**: longer training, higher backbone LR | Possible under-optimisation (2.1, hypothesis); val AUC still rising at the end | More GPU per fold; K_train 8 did not help (STATUS L6) | **Do (arm B = A + B)** |
| C. External knee MRI data | Forum speculation that it "can substantially increase score" | See 3.1: access, licence, domain and time costs; no host allow-list | **Not now** |
| D. Add public checkpoints not in the anchor (DINOv3 members, other Raptor checkpoints) | Cheap at training time | Tony Li's bundle with DINOv3 scores 0.940 < 0.943; choosing weights on the public LB is the overfitting route (STATUS L1, v05 notes) | Not now |
| E. Team merger before 2026-10-15 | A teammate with a strong own model is the most direct path past the 0.943 tie block; a forum post offers "0.942 solo, own 5-fold models + a GPU" | Social decision; submission limits and selection are shared | **User decision** |
| F. Stop and keep v05 | No risk | v05 sits inside a tie block of about 1,000 teams at 0.943 (STATUS refs); medal unlikely | Fallback only |
| G. Bigger backbone / higher resolution | Capacity limits are not excluded (2.1) | Forum: encoder scaling gave +0.001; 224-288 px models reach 0.94-0.95; budget | Deferred for budget, not ruled out; revisit if the like-for-like losses in v11 show a capacity limit |

### 3.1 External knee MRI data (checked 2026-10-04)

| Dataset | Content | Overlap with our 12 labels | Access and licence | Practical cost |
|---|---|---|---|---|
| MRNet (Stanford) | 1,370 exams, sagittal/coronal/axial, 256 px preprocessed arrays | ACL, meniscus (side not given), "abnormal" | Research Use Agreement via registration: no commercial use, no redistribution; a participant reports a no-derivative-works clause | Different preprocessing (no DICOM geometry: no mm crop or laterality); covers ACL, already our best-labelled finding (gold 0.99 for labels) |
| fastMRI+ (NYU images + MS annotations) | 1,172 knee studies, **one coronal series each**, 22 pathology boxes | Meniscus tear 663, ACL sprain 254, MCL sprain 125, effusion 142, cartilage loss ~700 (OA proxy), fracture/contusion 119 | Annotations CC BY 4.0; images require sign-up to the fastMRI data sharing agreement | Each file holds the k-space and a ready root-sum-of-squares image (`reconstruction_rss`, read directly by the official loader), so no reconstruction is needed, but both come in the same files: the knee multicoil training archive is 931 GB; single coronal plane; download infeasible in the remaining time |
| KneeMRI (Rijeka) | 917 sagittal T1 exams | ACL only | CC BY-NC-ND 4.0 (no derivatives) | ACL only; licence forbids derivatives |
| OAI / SKM-TEA | OA cohorts with semi-quantitative scores | OA, meniscus, effusion | Institutional credentialing / research agreements | Host: such steps "may present a meaningful accessibility barrier" |

Host position (topic 733965, 2026-08-27): non-commercial licences alone do not exclude a
dataset; click-through registration is generally acceptable; institutional approvals or
lengthy credentialing may not be. A request for an explicit allow-list (743416, 62 votes) is
still unanswered as of 2026-10-04. A participant cites the DeepFake competition, where top
teams were removed for external data the host had not explicitly allowed.

Assessment: the datasets that are easy to obtain (MRNet, KneeMRI) mostly cover ACL, where our
labels are already excellent and the bottleneck is the image model; their licences contain
no-derivative clauses that make training on them legally doubtful; the dataset that covers our
weak findings (fastMRI+) is single-plane and comes in about 1 TB of files. Expected gain is
speculative and small relative to option A's measured +0.027 on gold, and every path needs the
user to register and accept agreements (the agent must not). **Recommendation: no external
data in this round.** Revisit only if (1) the host publishes an allow-list that includes a
dataset, and (2) options A/B have been tried.

### 3.2 Leakage note for option A

For the fold-k student, the OOF target of a training study in fold j comes from the v08 fold-j
model, which was trained on folds other than j, including fold k. So the teacher has seen the
student's validation studies' (soft) labels: fold-level validation of the student becomes
optimistic by an amount we have not measured. Gold is untouched by training (no model has seen
its labels) and the public LB is clean. Gold does become a selection set once it is used to
choose an arm and to decide on continuing (4.2); after that the leg-alone public score (4.4) is
the independent test, and a second iteration cannot treat gold as independent.
Clean nested teachers would need 20 extra trainings; not affordable. Consequence: decisions
use gold and the leg-alone public score, with fold-0 validation as a secondary signal.

## 4. Plan

### 4.1 v11: fold-0 training with two arms (one session, two T4s)

Same cache (v07), folds (v06), model and code (v08) unless stated.

| Arm | Targets | Epochs | Backbone LR | Head LR | K_train | Isolates |
|---|---|---|---|---|---|---|
| A | `0.5 * soft + 0.5 * OOF` (v08, K_infer 16), per-cell weights unchanged | 10 | 5e-5 | 2e-4 | 4 | label effect |
| B | same as A | 15 | 1e-4 | 3e-4 | 4 | label + optimisation |

Gold studies keep no OOF and are never trained on.

Run limits (v08's 6 h per-arm limit would stop arm B): arm A time limit 6 h, arm B time limit
9 h, global deadline 11 h. Estimates with the K16 evaluations below (rev. 2.1, section 8): arm A
about 4.8 h, arm B about 7.6 h; expected session length about 7.7 h. A run that stops early or
fails is **incomplete** and never enters Gate R1 (its gold value is ignored).

Like-for-like loss (answers 2.1): at every evaluation epoch each arm also scores a fixed random
subset of 500 of its own training studies with the same settings as validation (same
checkpoint, no augmentation, `K_infer` 16, same per-cell weights against the arm's training
targets), and the receipt records train and validation loss side by side. Validation therefore
also runs at `K_infer` 16 at every evaluation (v08 used 8), and the best epoch is selected by
K16 validation macro AUC, the same metric Gate R1 uses. Evaluations start at epoch 4 as in v08.
Cost (rev. 2.1): about 17 minutes per evaluation instead of v08's 6 (section 8).

### 4.2 Gate R1 (pre-registered): continue to 5 folds?

Metrics on fold 0 at `K_infer` 16: gold-58 macro AUC (primary, clean) and fold-0 validation
macro AUC against the original soft targets rounded at 0.5 (secondary, mildly optimistic).

Definitions: an arm is **complete** if it trained all its epochs (receipt status `done`). A
complete arm is **qualified** if its fold-0 val macro AUC (K_infer 16) is at least 0.871
(v08 fold 0, same evaluation). Ranking among qualified arms is by gold; within 0.005 of the
best, the cheaper arm A is chosen. Order (rev. 2.1): filter complete arms, then qualified arms,
then rank them to pick **one** arm; rules 2 and 3 test the picked arm's gold, and "the best
such arm" is that arm. Example: A 0.912 and B 0.916, both qualified: A is picked (within
0.005) and rule 3 applies. Rules are applied in this order; the first that matches decides.

| # | Outcome | Action |
|---|---|---|
| 1 | No arm complete | One rerun of arm A alone (time limit 6 h), counted in the budget; then re-apply this table once. If still no complete arm: stop own-model work |
| 2 | The picked qualified arm has gold >= 0.915 | Train folds 1-4 with the picked arm |
| 3 | The picked qualified arm has gold in [0.905, 0.915) | Train folds 1-4 with the picked arm only if the remaining weekly quota covers the folds plus 20%; otherwise stop. Rationale: the gold CI (about +-0.03) cannot separate this band from rule 2; the leg-alone public score (4.4) is the real gate |
| 4 | Anything else (complete arms with val < 0.871, or gold < 0.905) | Stop own-model work; final picks per 4.4 with v05 |

There is no `K_train` 8 retry: at v08's speed 15 epochs at K_train 8 would take about 9-10 h
per fold, which neither fits the session limits nor the budget.

Why gold is primary now (a change from design rev. 3.3, which used gold only as a bug
detector): STATUS L3 shows gold tracked the public LB (0.897 -> 0.909) and gold is the only
metric untouched by option A's leakage (3.2). It is used for one pre-registered two-arm choice
and one continue decision; we do not tune on it, and after this it is no longer an independent
check (3.2).

### 4.3 v11 folds 1-4 and v12 leg-alone submission

- Folds 1-4 with the chosen arm through the v08 GPU queue (per-fold time limit 6 h for A,
  9 h for B). Estimates with the K16 evaluations (rev. 2.1): arm A about 4.8 h per fold, one
  session of about 9.8 h (two rounds of two folds). Arm B: about 7.6 h per fold, two sessions
  of about 7.7 h (two folds in parallel each), because two rounds of 7.6 h exceed the 11 h
  global deadline. Whether folds 1-4 keep the training-subset loss (about 1 h per fold) is
  decided after fold 0, which answers the question of 2.1; the notebook has a switch.
- **v12_submit = leg alone** (as v10; about 1 h of scoring). This is the gate for blending.

### 4.4 Blend decision table (pre-registered; replaces design 4.6 for new legs)

| v12 leg-alone public LB | Action |
|---|---|
| >= 0.940 | v13_submit: anchor + leg at w = 0.45 |
| [0.935, 0.940) | v13_submit: anchor + leg at w = 0.30 |
| < 0.935 | No blend; record and revisit |

Final selection (two picks, by 2026-10-22), over the measured candidates v05, v12 and v13:

1. Pick 1: the highest public LB among them.
2. Pick 2: the highest public LB among the remaining candidates of the other kind (anchor-based
   = v05, v13; own-only = v12), so that one pick contains the anchor and one does not when
   both kinds exist; if only one kind exists, the next best.
3. A blend is only kept as a candidate if it beats max(v05, v12) on the public LB.

### 4.5 Budget and timeline

| Step | GPU h (estimate) | Dates |
|---|---:|---|
| v11 fold 0, two arms (+ possible arm-A rerun, rule 1: up to 6) | about 7.7 (+6) | 10-05 |
| v11 folds 1-4: arm A about 9.8; arm B about 15.4 (two sessions) | 9.8-15.4 | 10-06 to 10-08 |
| v12 leg-alone commit + scoring | under 1 (+1 h scoring) | 10-07 |
| v13 blend commit + scoring | under 1 (+5-6 h scoring) | 10-08 |
| Second iteration if v13 helps (round-2 targets from v11 OOF) | 15-20 | 10-09 to 10-15 |
| Final selection | - | by 10-22 |

About 19-25 GPU h for the first iteration (up to 31 h with the rule-1 rerun; rev. 2.1 figures).
Degradation if the quota is short: drop the training-subset loss in folds 1-4 (saves about 1 h
per fold), then arm A instead of B for folds 1-4 (saves about 5.6 h), then stop. Quota checked
2026-10-04 with `kaggle quota`: 0.18 h used, 29.82 h left until the reset on 2026-10-10 00:00 UTC
(scoring reruns are not counted), so fold 0 and folds 1-4 with either arm fit in the current
window, and rule 3's quota condition (A 11.5 h, B 18.2 h) holds after fold 0.

## 5. Risks

1. **Leakage optimism** in fold validation (3.2); mitigated by gold and leg-alone LB gates.
2. **Gold-58 is small** (CI half-width about 0.03); a single arm comparison can be noise, and
   using it for selection makes it a selection set (3.2). The R1 thresholds are set below the
   teacher-mix's 0.917 to require only a plausible gain; the leg-alone LB is the real test.
3. **The student may not inherit the teacher-mix gain**; v12 measures it directly.
4. **Arm B changes two things** (epochs and LRs); acceptable because it is compared with A
   only to choose a recipe, not to attribute effects.
5. **Time**: a full cycle took about 3 days (STATUS L8); a second iteration must start by
   10-09 to finish before the deadline.

## 6. Proposed changes to `IMPROVEMENT_PLAN.md` (applied after approval)

- Mark Priority 1 (own diverse model) as tried: v08-v10, failed to help (cite STATUS v09,
  v10, L2).
- Promote Priority 2 (labels / OOF pseudo-labels) to the active priority, with the gold
  evidence of 2.2 and the under-optimisation hypothesis of 2.1.
- Record external data as considered and deferred (3.1), and team merger as a user decision
  with the 2026-10-15 deadline.
- Replace the old blend weights with the leg-alone gate of 4.4.

## 7. Codex review (revision 1, 2026-10-04, GPT-6 Astra, D-013)

Verdict: needs-attention. Each finding was checked before acting.

| # | Finding (severity) | Verified? | Disposition |
|---|---|---|---|
| 1 | R1 had no branch for gold passing but val failing, no rule when the two arms each pass one threshold, and an unclear tie rule (high) | Yes | **Accepted**: complete / qualified definitions, ordered rule table including incomplete runs (4.2). |
| 2 | The K_train 8 retry inherits v08's 6 h limit that already stopped the K8 arm; incomplete runs could still feed R1; not budgeted (high) | Yes, and worse than stated: arm B itself (15 epochs, about 6.2 h) would hit the 6 h limit | **Accepted**: explicit per-arm limits (A 6 h, B 9 h), incomplete runs excluded, K8 retry removed as infeasible, budget and degradation updated (4.1, 4.2, 4.5). |
| 3 | Final selection could drop a leg-alone v12 that beats the blend (medium) | Yes | **Accepted**: v12 is a final candidate; blends must beat max(v05, v12); pick rule over v05/v12/v13 (4.4). |
| 4 | The train-vs-OOF loss comparison is not like-for-like; the entropy floor is not image-achievable; capacity cannot be ruled out on that basis (medium) | Yes | **Accepted**: 2.1 downgraded to a hypothesis; like-for-like train/val loss added to v11 (4.1); option G deferred for budget, not ruled out. |
| - | Gold becomes a selection set after use; leakage size unmeasured (next steps) | Yes | **Accepted** (3.2, risk 2). |
| - | fastMRI files include `reconstruction_rss`, so reconstruction is not required (next steps) | Yes (official loader reads it) | **Accepted**: 3.1 corrected; the download-size argument stands, so the decision is unchanged. |

Standing points: none.

## 8. Revision 2.1: clarifications at approval (2026-10-04)

The user approved revision 2 with these two clarifications. They correct an estimate and remove
an ambiguity; the direction, arms, thresholds and decision tables are unchanged, so no new Codex
review was requested.

| # | Issue | Evidence | Resolution |
|---|---|---|---|
| 1 | 4.1 estimated about 2 minutes per evaluation for the training-subset loss | v08 logs: evaluation runs at about 113 tokens/s with time proportional to tokens (fold 0: K8 validation of 947 studies about 335 s; folds 1-4: final K16 validation plus gold 824-998 s). Fold 0 at K16: validation 947 x 80 tokens about 670 s, training subset 500 x 80 tokens about 354 s | About 17 minutes per evaluation (v08: about 6). Arm A about 4.8 h (10 x 1,010 s training + 7 evaluations), arm B about 7.6 h (15 x 1,010 s + 12 evaluations); both inside their 6 h / 9 h limits; the best epoch is selected at K16. Budget in 4.3 and 4.5 updated; a switch can drop the training-subset loss in folds 1-4 |
| 2 | Gate R1 was ambiguous when the arms straddle a threshold within 0.005 (example: A 0.912, B 0.916) | Definitions say "within 0.005 of the best, arm A is chosen"; the rule rows said "at least one qualified arm with gold >= 0.915" | Pick first, then apply rules: complete, qualified, rank (A within 0.005), one picked arm; rules 2 and 3 test the picked arm's gold (4.2). In the example A is picked and rule 3 applies |

Also noted: the qualification threshold is the literal 0.871 pre-registered in 4.2; v08's exact
fold-0 K16 value is 0.87088, so the threshold is 0.0001 stricter than v08.

## 9. Codex review of the v11 implementation (2026-10-04, GPT-6 Astra, D-013)

Scope: `notebooks/v11-oof-teacher.ipynb` (commit 9263b11) against sections 4.1, 4.2 and 8, run
locally with `codex exec` in a read-only sandbox (`codex review --commit` does not accept review
instructions). Verdict: needs-attention, two medium findings, both verified in the code.

| # | Finding (severity) | Verified? | Disposition |
|---|---|---|---|
| 1 | The per-arm time limit is checked only between training batches; validation, training-subset and gold evaluation ignore it, so an arm whose last epoch ends just before the limit still finishes as `done`, and a hung evaluation is not stopped by the arm limit (medium) | Yes | **Partly accepted.** Not a bias: 4.2 defines complete as "trained all its epochs", and the overrun is bounded by one K16 evaluation plus gold (about 18 minutes; A at most about 6.3 h, B about 9.3 h, far below the 10.9 h stop). The hang risk is real: the parent now stops a process still running one hour after its limit (`killed_hang_guard`, incomplete). The semantics are stated in the notebook |
| 2 | `collect()` reads a fixed receipt path and ignores the exit code, so a rerun in the same directory that crashes before writing its first receipt can pick up an earlier `done` receipt and pass Gate R1 (medium) | Yes (cannot occur in a fresh Kaggle batch run, which starts with an empty working directory; can occur in an interactive rerun) | **Accepted.** `launch()` deletes any receipt of the arm before starting, and a non-zero exit code marks the arm `failed` (reported status kept as `status_reported`) |

Both fixes were tested locally: a stale `done` receipt with a crashing trainer gives `failed` and
Gate R1 rule 1; a `done` receipt followed by exit code 3 gives `failed`; the hang guard and the
deadline stop give incomplete statuses; the two-arm and fold-queue runs are unchanged.
