# Design note: strategy revision after v12 (v13 onward)

Date: 2026-10-06. Status: **revision 3.1 after three Codex reviews (sections 8-10); for user
discussion and approval**. No GPU time is spent before approval. Grounded in `docs/STATUS.md`
(D-011, D-012): versions and lessons are cited as "STATUS v<NN>" and "STATUS L<n>". The blend
gate and final-selection rule of `v11-strategy-revision-design.md` revision 2.1, section 4.4,
stay in force. Supporting notes: `anchor-components-2026-10-06.md` (STATUS L16),
`external-pretrained-2026-10-06.md`; script `scripts/anchor_proxy_gold.py`.

## 1. Where we stand

- v05 public stack anchor **0.943** is pick 1 (STATUS v05). Our team is at rank 1,278 inside the
  0.943 tie block; any score >= 0.944 currently lands inside bronze, 0.945 is the silver line
  (STATUS ref 2026-10-05).
- v12 (v11 arm-B 5-fold leg alone) scored **0.931**, +0.022 over v10, gold 0.913 (STATUS v12, L13).
  It is below the pre-registered 0.935 blend gate, so no blend; under the v11 selection rule it
  is the own-only candidate for pick 2.
- **Target, as a sensitivity analysis.** An equal-variance binormal model fitted to the single
  v09 observation gives an effective noise correlation of 0.943 between our leg and the anchor;
  under it a leg needs about 0.935 (w 0.30) / 0.937 (w 0.45) alone to break even and about 0.939
  for a 0.944 blend (STATUS L15; Codex recomputation 0.9354 / 0.9371 / 0.9390). One macro-AUC
  observation cannot measure per-label correlation; these are orders of magnitude.
- **Anchor proxy** (STATUS L16): it matches v09 (v08 at w 0.45: -0.010 on gold, -0.011 on LB), but
  its verdict on v11 at w 0.30 depends on the proxy weights (-0.001 / +0.003 / -0.001 for three
  frozen variants). It is reported as a diagnostic only.
- **Resources.** GPU quota **8.80 h** until the reset on 2026-10-10 00:00 UTC (`kaggle quota`,
  2026-10-06), then 30 h for 10-10..10-16 and 30 h for 10-17..10-22 (scoring reruns do not count).
  Five submissions per day. Team-merger deadline 2026-10-15; final deadline 2026-10-22. Measured
  v11-B fold times without the training-subset loss: 6.48 / 6.37 / 6.75 / 6.97 h (folds 1-4); two
  folds run in parallel per session (STATUS v11 tables). Hidden test set: about 1,300 studies.

## 2. Evidence

### 2.1 What is measured

| Fact | Source |
|---|---|
| Training target (mean of 4 public LLM tables) 0.892 on gold; each public table 0.835-0.893 with overlapping CIs | STATUS settings ledger; v06 design 2.1 |
| v08 did not exceed its labels on gold (0.897 vs 0.892) | STATUS L4 |
| Under the v08 recipe, replacing the target by `0.5 soft + 0.5 v08 OOF` did not move gold (A 0.895 vs v08 fold 0 0.896) | STATUS L9 |
| With those targets, more optimisation did (B 0.911 vs A 0.895, CI +0.006 to +0.026); B's validation plateaus after epoch 9 | STATUS L10 |
| v11 5-fold 0.913 vs target 0.892 (CI -0.005 to +0.048) and vs teacher mix 0.917 (CI -0.022 to +0.014) | STATUS v11 5-fold section |
| On gold the labels beat the v11 leg on ACL, MCL, PF OA, Lateral Meniscus, Synovitis (and slightly Lateral OA); the leg beats them on Effusion, Contusion, Fracture, Medial OA, Baker's, Medial Meniscus | local analysis 2026-10-05; Codex check |
| Gold -> LB offsets differ by model: v08 0.897 -> 0.909, v11 0.913 -> 0.931, pilkwang DINOv2 OOF 0.840 -> baseline LB 0.891 | STATUS L3, L16 |
| v11 5-fold vs fold-0-only on gold: +0.0019 (CI -0.0045 to +0.0080) | Codex recomputation |

### 2.2 Competing explanations (none excluded)

1. **Label noise.** Every public table caps near 0.89 on gold, and gold is labelled from the images.
   Forum topic 745214 (participant claims): relabelling with several LLMs and voting, then OOF
   teachers, moved a DINOv2 from LB 0.931 to 0.942 with gold about +0.01; the same participant
   reports a label version with gold 0.945 but LB 0.910.
2. **Under-learning of signal already in the labels.** The labels beat the leg on several findings;
   one recipe change (L10) moved gold by +0.016; nothing else was tried.
3. **Generalisation and redundancy with the anchor** (2.1 offsets; L15, L16).

### 2.3 Round-2 teacher (local, verified)

On gold (probability mean; gold studies use the mean of the five fold models), `0.5 soft + 0.5
v08 teacher` **0.9168** vs `0.5 soft + 0.5 v11 teacher` **0.9235**: +0.0067 (paired bootstrap,
4,000 resamples: CI +0.0009 to +0.0130). This is a gain of the target proxy, not of a student; the
training rows use one OOF teacher, the gold rows the five-model mean, and L9 shows that target
gains need not transfer. It needs no API and no new data, and tests explanation 2.

### 2.4 Anchor composition and MRI-pretrained backbones

The anchor's public members are not stronger than v11 on gold; its families are ImageNet-DINOv2,
RadImageNet ResNet-50 and CoAtNet (STATUS L16, hypothesis that its strength is the mix). MRI-CORE
(ViT-B in SAM's image-encoder layout, DINOv2 self-supervision on more than 6 M MRI slices of 18
body regions including the knee; repository code and models Apache 2.0) is the only public
MRI-specific 2D backbone found with knee data; its pretraining domain differs from all anchor
families. External datasets stay out (no host clearance, topic 743416).

## 3. Options

| Option | Evidence for | Evidence against / cost | Proposal |
|---|---|---|---|
| **N. Round-2 teacher**: v11-B recipe, target `0.5 soft + 0.5 v11 OOF` | 2.3; no API; same pipeline | L9; leakage chain grows (fold validation more optimistic, design v11 3.2) | **Primary fold-0 arm** |
| **M. MRI-pretrained second model** (MRI-CORE ViT-B, frozen config 4.2), same target as N | 2.4: different pretraining domain and family | Untested adaptation; compute; single fold tests one configuration only | **Second fold-0 arm, if it passes step S** |
| M'. ImageNet EfficientNet-B3 (frozen config 4.2) | Family absent from the anchor | Same ImageNet domain as v11; BN with correlated tokens | Fallback for M in step S |
| L. Own LLM report labels | 2.2 (1); host allows LLM APIs | User's API key and spend; new sources diluted (two among six sources = 1/6 of the target) | Optional, own budget, 4.8 |
| D. Team merger before 2026-10-15 | Direct path past the tie block | Social decision | User decision |
| E. Stop; picks v05 and v12 | No risk | No medal path | Fallback |
| Not now | External datasets; distilling or fine-tuning anchor members (raises correlation); more folds or epochs of v11 (L10, L13) | | |

## 4. Plan

### 4.1 Pre-registration and conventions

- Frozen before any gold or LB result of this plan is seen: arm configurations (4.2, 4.3), targets,
  loss weights (v06 rule: 0.3 where pilkwang's verdict is UNK, else 1), seeds (2026), checkpoint
  selection (best K16 validation epoch, as v11), gate thresholds, bootstrap settings (2,000 paired
  study resamples, seed 0; a label with one class in a resample is skipped), and the three proxy
  variants in `scripts/anchor_proxy_gold.py`. Teacher weights are not tuned on gold.
- Gold gates are **exploratory screening rules**: `P(gain <= 0) <= 0.2` is the share of
  non-positive bootstrap gains for fixed predictions, not a false-positive rate, and ignores
  training randomness and repeated gold use (fourth selection use after v11 R1). Every gate
  report also gives the candidate's total gain over v11 fold 0 with its CI.
- The public LB checks in steps D and P are sequential external checks on the same public split,
  not independent validations. Scores are taken as returned; no reruns to cross a threshold.
- **Budget formula** (admission and stop use the same rule): a session may start only if
  `max(projected arm time) x 1.15 + 0.25 h <= quota at launch - 0.4 h`; its global hard stop is
  `quota at launch - 0.4 h`; each arm's time limit is `projected x 1.15`, capped by the hard stop.
  "Quota at launch" is read with `kaggle quota` right before each push.

### 4.2 Step S - smoke test for arm M (one session, about 0.5 GPU h)

Both candidate configurations run in parallel (GPU 0 MRI-CORE, GPU 1 EfficientNet-B3), so the
throughput includes the two-arm CPU sharing of F0 (STATUS L12). Each: about 300 training
micro-steps on fold 0, one K16 validation pass, and the checks below.

| Item | MRI-CORE (M) | EfficientNet-B3 (M') |
|---|---|---|
| Weights | `MRI_CORE_vitb.pth` (Apache 2.0) as a private Kaggle dataset (user approval for download and upload) | `timm` `efficientnet_b3.ra2_in1k` (internet on) |
| Architecture | SAM ViT-B image encoder vendored from `segment_anything` (Apache 2.0): embed 768, depth 12, heads 12, patch 16, window 14, global attention at blocks 2/5/8/11, no relative positions (as the MRI-CORE builder); absolute position embedding resized bilinearly from 64x64 to 14x14 at load | timm default |
| Input | v07 triplets (c-1, c, c+1) resized 320 -> 224; each channel min-max scaled to [0, 1] per slice (MRI-CORE preprocessing), no ImageNet statistics | v07 triplets at 320 px, ImageNet mean/std (as v11) |
| Features | encoder neck output 256 x 14 x 14, global average pooled -> 256-d token, then the v11 head (slot embedding, gated attention, 12 logits) | timm pooled features -> v11 head |
| Trainable | blocks 8-11, neck, head (patch embedding, position embedding, blocks 0-7 frozen) | all; BN layers in eval mode, affine parameters trainable |
| LR backbone / head | 5e-5 / 3e-4 | 1e-4 / 3e-4 |
| Schedule | as v11 B: AdamW wd 0.05, cosine, 15 epochs, warm-up 1, K_train 4, K_infer 16, micro-batch 2 x accum 4, fp16 | same |

**Correctness checks (both):** after loading, the encoder (or backbone) has **no missing keys**;
unexpected keys must be on an explicit whitelist (MRI-CORE: prompt-encoder and mask-decoder keys).
For MRI-CORE the position embedding is resized by our own code (bilinear, 64x64 -> 14x14) and
written under the model's own key, and the loaded tensor must equal that expected resized tensor
(max difference < 1e-6); the upstream loader is not used. Further: finite, non-zero gradient norms
in each trainable group; mean loss of the last 50 micro-steps below the first 50; save, reload and
predict two studies with max difference < 1e-5.

**Admission rule:** projected F0 fold time (15 epochs, evaluations from epoch 4, from the measured
throughput) must satisfy the budget formula together with arm N (projected 6.3 h from v11-B fold 0
minus its training-subset evaluations), i.e. about **<= 6.65 h** with 8.30 h quota at launch;
peak reserved memory < 14 GB; all checks pass. MRI-CORE is preferred; else EfficientNet-B3; else
F0 runs N alone. The receipt also records the projected 5-fold test inference time (K16, about
1,300 studies, two T4) used in 4.6.

### 4.3 Step F0 - fold 0, arms N and M (one session)

Notebook `notebooks/v13-<name>.ipynb`, derived from v11 (modes `smoke`, `fold0_arms`, `folds`;
receipts; deadline and hang guards; stale-receipt removal). Both arms use the target
`0.5 soft + 0.5 v11 OOF` (the five v11 OOF files as a private dataset; gold excluded) and the
v11-B schedule without the training-subset loss. Arm N = ConvNeXt-tiny exactly as v11 B; arm M =
the configuration admitted in step S. Budget by the formula in 4.1.

Arm states: **done** (all epochs trained), **completed-fail** (done but gold < 0.900, a sanity
floor), **incomplete** (stopped, killed, crashed, mount failure), **not-run** (excluded by step S).

### 4.4 Gate F0 (state machine, pre-registered)

1. **Resolve incomplete arms first.** An incomplete arm gets one technical rerun of fold 0 at the
   start of the 10-10 window (both arms in one session if both are incomplete); N's rerun has
   priority over M's. A rerun that is again incomplete makes the arm "dropped". No decision is
   taken while an arm is pending.
2. **Base.** base = N if N is done and gold(N) - gold(v11 fold 0) >= +0.003 with P(<= 0) <= 0.2;
   otherwise base = v11 fold 0 (gold 0.911).
3. **Candidate.** C = base + M if M is done and gold(rank-mean(base, M)) - gold(base) >= +0.003 with
   P(<= 0) <= 0.2; otherwise C = base. The combination is the equal-weight mean of per-label
   percentile ranks of the two models, re-ranked; it is fixed here.
4. **Outcomes.** C = v11 fold 0 alone: stop own-model work (picks v05 and v12). Otherwise C is one
   of **N-only**, **v11+M** (reuses the v11 folds; only M is trained further) or **N+M**.
5. Report C's total gain over v11 fold 0 with its CI and the proxy gain for the three variants
   (diagnostic).

### 4.5 Step D - fold-0 leg-alone diagnostic submission

`v14_submit` = C's fold-0 model(s) alone (v12 notebook generalised to k folds x m models, same
reference and OOF checks). **Continue to folds 1-4 only if LB(v14) >= 0.933.** This is a
resource-allocation threshold, not a calibrated forecast: there is no measured LB for a fold-0
v11 leg, and the 5-fold vs 1-fold gain on gold is +0.002 with a CI from -0.004 to +0.008. We
accept the risk of a false stop in exchange for not spending 13-28 GPU h on a leg that would miss
the 0.935 gate. Cost: a commit run under 0.1 GPU h, about 1 h of scoring, one submission.

### 4.6 Steps F1-4 and P (5-fold leg, blend)

- **Inference gate before folds 1-4:** if C contains M, the test runtime of the final blend
  `anchor + (N or v11) leg + M leg` must be <= 8.0 h of the 9 h limit, where the anchor-plus-
  ConvNeXt-leg part is the **measured** scoring duration of the v09 submission (start to finish,
  read from the Kaggle submissions page; this includes preprocessing, loading and merging) and the
  M leg is projected from step S plus 20%. If the v09 duration cannot be read, the gate counts as
  failed. A failed gate does not change C: the validated C continues only on the own-only path
  (v15 leg alone, no v16 blend); M is not removed from C to obtain a blend.
- **Folds 1-4** through the fold queue with the budget formula. N-only: two sessions of about 7 h
  (one N fold per GPU). v11+M: M only, two sessions. N+M: each session pairs one N fold with one M
  fold, four sessions of about 7.9 h at the admission bound: at most three in the 10-10..10-16
  window (at most two if F0 had to be rerun in that window), the rest in the 10-17 window.
  Technical failures: one rerun per fold.
- **Terminal states** (pre-registered, no ad-hoc changes to fold counts or candidate composition):
  if a fold fails again after its rerun, if the budget formula refuses a needed session, or if a
  component cannot complete five folds by 2026-10-20, that component is abandoned. The leg for v15
  is then made of the components with five completed folds (N+M falls back to N-only; v11+M falls
  back to stop), and it is judged only by its own leg-alone score. If no component completes, own-
  model work stops with the existing submissions (v05, v12, and v14 if scored).
- **P:** `v15_submit` = 5-fold C leg alone. Blend `v16_submit` = anchor + leg only if the v11 4.4 gate
  passes (>= 0.935: w 0.30; >= 0.940: w 0.45) and the inference gate holds; the proxy gain is
  reported for the three variants without a veto. Final selection per v11 4.4 (candidates v05,
  v12, v14, v15, v16).

### 4.7 Timeline and budget scenarios

| Scenario | Steps and dates | GPU h by window |
|---|---|---|
| Common start | Build v13 and local CPU tests (10-06/07); user approvals; S (10-07); F0 (10-07/08); Gate F0; D submitted (10-08/09) | until 10-10: S 0.5 + F0 <= 7.9 = 8.4 of 8.80 |
| N-only or v11+M | F1-4 two sessions (10-10/11); v15 (10-12); v16 if gated (10-12/13) | 10-10 window: about 15 |
| N+M | F1-4 three sessions (10-10..10-13) + one (10-17); v15 (10-18); v16 (10-18/19) | 10-10 window: about 23; 10-17 window: about 8 |
| Technical rerun of F0 | rerun first in the 10-10 window (<= 8 h), then at most two follow-up sessions there (<= 16 h); N+M moves two sessions to the 10-17 window and ends about 10-19/20 | 10-10 window: <= 24 + commit runs; 10-17 window: <= 16 |

Training ends by 10-20; submissions and selection by 10-21/22.

### 4.8 Option L (own LLM labels), optional and separately budgeted

Only if the user provides an API key by 2026-10-08. Prompt developed on non-gold reports only;
model, prompt, aggregation and missing-value rules frozen before any gold evaluation; at least two
model families, temperature 0; new sources averaged with the four public tables. Compare the full
target `0.5 * (mean of six sources) + 0.5 * v11 OOF` with N's target on gold: use it only if the gain
is >= +0.005 with P(<= 0) <= 0.2, and only for training in the 10-17 window after C's folds. No GPU
hours are reserved for L in the main plan.

## 5. Risks

1. **N may not transfer** (L9); step D catches it after one fold.
2. **Gold reuse**; step D and v15 are external checks on the public split, at the price of
   public-LB selection on pre-registered thresholds.
3. **Arm M adaptation** (vendored encoder, position-embedding resize, per-slice scaling, triplet
   input on a single-slice model): checked in step S; a failure rejects this configuration, not
   MRI pretraining in general.
4. **Fold 0 is the easy fold** (STATUS L7); all thresholds are relative to v11 fold 0.
5. **Mount failures** of large inputs (STATUS L14); v07 version 3 is the current cache.
6. **Time and runtime**: N+M ends about 10-19 with one day of slack; the inference gate guards the
   9 h limit.

## 6. Open questions for the user

- Approve this revision (section 4) as the plan for v13-v16?
- Approve, when needed: downloading MRI-CORE weights from Google Drive and uploading them as a
  private dataset; uploading the five v11 OOF files as a private dataset; each push and submission.
- Option L (API key) and the team merger are the user's decisions.

## 7. Proposed changes to `IMPROVEMENT_PLAN.md` (after approval)

- Record Priority 2 (v11 OOF targets) as done: leg 0.931 alone, below the blend gate (STATUS v12, L15).
- New active priority: round-2 teacher (N) with a fold-0 LB diagnostic (step D).
- Priority 4 (second own model) becomes arm M with an MRI-pretrained backbone and a step-S admission.
- Own LLM labels as an optional track; external datasets not used (no host clearance).
- Team merger as a user decision before 2026-10-15.

## 8. Codex review of revision 1 (2026-10-06, GPT-6 Astra, read-only `codex exec`)

Verdict: needs-attention. Each finding was checked before acting.

| # | Finding (severity) | Verified? | Disposition |
|---|---|---|---|
| 1 | The diagnosis "label ceiling is the best-supported bottleneck" overstates the evidence; the forum anecdote lacks its counterexample (high) | Yes | **Accepted**: 2.2 lists three competing explanations with the counterexample |
| 2 | Gate L0 scored the new labels, not the target the student learns; agreement with the image model must not be a pass criterion (high) | Yes | **Accepted**: 4.8 compares full targets, frozen before gold |
| 3 | Revision 1 changed the UNK loss-weight rule (high) | Yes, an error in revision 1 | **Accepted**: v06 rule kept (4.1) |
| 4 | Gate T did not test the deployed combination (high) | Yes | **Accepted**: Gate F0 builds and tests the deployed candidate step by step (4.4) |
| 5 | Arm M was not a defined experiment (medium) | Yes | **Accepted** in revision 2, completed in revision 3 (4.2: frozen configurations and checks) |
| 6 | Stop rules and slack were missing (high) | Yes | **Accepted**; budget formula and state machine completed in revision 3 (4.1, 4.4, 4.7) |
| 7 | Binormal figures over-interpreted; "at any weight" wrong; d4 attribution wrong (medium) | Yes | **Accepted**: section 1, STATUS L15 corrected, d4 argument removed |
| 8 | Round-2 teacher dismissed despite local evidence; suggests a fold-0 leg-alone diagnostic (medium) | Yes, reproduced | **Accepted**: arm N primary, step D (2.3, 4.5) |

## 9. Codex re-review of revision 2 (2026-10-06)

Verdict: needs-attention. Findings 1-4, 7 and 8 of the first review resolved; 5 and 6 partly.
New findings, each checked:

| # | Finding (severity) | Verified? | Disposition |
|---|---|---|---|
| 1 | The anchor proxy had a veto (gain >= -0.002) although frozen alternative weights flip its sign for v11 (equal weights +0.0028, CoAtNet only -0.0012); L16 overstated as a fact (high) | Yes, reproduced with the script | **Accepted**: three frozen variants, reported only, no veto (4.6, script); STATUS L16 and the anchor note reworded as a hypothesis |
| 2 | Arm M's speed gate cannot catch a mis-loaded or mis-adapted model; LR, pooling, trainable set, position embedding and normalisation not frozen; the MRI-CORE builder disables relative positions and loads with `strict=False` (high) | Yes (builder checked: patch 16, window 14, no relative positions, non-strict loading with key remapping and position-embedding resizing) | **Accepted**: 4.2 freezes both configurations and adds key, gradient, loss and reload checks; per-slice min-max scaling as in MRI-CORE |
| 3 | Admission and stop budgets were inconsistent (7.5 h admitted vs 7.93 h available with 15% margin); folds 1-4 for both arms exceed one window; 8.83 h was a stale quota (high) | Yes (quota now 8.80 h) | **Accepted**: one budget formula for admission and stop (4.1); M admitted at about <= 6.65 h; step S measures under two-arm load; scenarios with the 10-17 window (4.7) |
| 4 | Incomplete arms fell through to "stop"; the v11+M branch and option L's budget were undefined (high) | Yes | **Accepted**: state machine with pending, rerun and dropped states, three named candidates, M-only training for v11+M, L separately budgeted (4.4, 4.6, 4.8) |
| 5 | No gate on the final blend's hidden-test runtime (anchor > 5 h, limit 9 h) before training folds 1-4 (high) | Yes | **Accepted**: inference gate before folds 1-4 using the step-S projection (4.6) |
| 6 | Step D's 0.933 is a budget policy, not a calibrated threshold; 5-fold vs 1-fold on gold +0.0019 (CI -0.0045 to +0.0080); v14 and v15 are not independent validations (medium) | Yes | **Accepted**: wording in 4.5 and 4.1 |
| 7 | N's gold gate measures a target proxy, not a student; `P <= 0.2` is not a false-positive control; report the total gain of the chosen candidate (medium) | Yes | **Accepted**: 2.3 and 4.1 wording; total gain reported (4.4) |
| low | MRI-CORE licence stated as CC BY 4.0 in the survey but Apache 2.0 in the design | Yes | **Accepted**: survey corrected (repository: Apache 2.0; paper page: CC BY 4.0) |

Standing points: none. All numbers in sections 1-2 were recomputed by Codex from the local files.

## 10. Codex review of revision 3 (2026-10-06)

Verdict: needs-attention, three medium findings, no high ones. Revision-2 findings 1, 6, 7 and the
low item resolved; 2-5 partly, closed by the items below. Budget arithmetic (6.65 h admission) and
the Gate F0 state machine (all branches reachable and terminating) confirmed. Each finding checked:

| # | Finding (severity) | Verified? | Disposition |
|---|---|---|---|
| 1 | Allowing the resized position embedding to be "missing" lets a mis-load pass every other check; the upstream loader writes it under the unmapped key (medium) | Yes (upstream `load_from` uses the original key for the resized tensor) | **Accepted**: no missing encoder keys; our own resize written under the model key and asserted equal to the expected tensor; upstream loader not used (4.2) |
| 2 | The F0-rerun scenario needs 31 h in a 30 h window; no terminal rule after a failed rerun (medium) | Yes | **Accepted**: at most two follow-up sessions after an F0 rerun in the 10-10 window; pre-registered terminal states and fallback composition (4.6, 4.7) |
| 3 | The 6 h anchor "upper bound" is unsupported (v05 > 5 h is a lower bound) (medium) | Yes | **Accepted**: the gate uses the measured v09 scoring duration or counts as failed; a failed gate keeps C on the own-only path (4.6) |

Standing points: none.
