# Decision Log

Record decisions that change project direction, conventions, or architecture. Newest
first. Each entry: ID, date, decision, reason, consequences.

## D-015 - 2026-10-06 - Strategy after v12: round-2 teacher (N) and an MRI-pretrained second model (M)

**Decision.** Approve `docs/research/v13-strategy-revision-design.md` revision 3.1. Fold 0 runs two
arms with the v11-B schedule and the target `0.5 soft + 0.5 v11 OOF`: N (ConvNeXt-tiny) and M
(MRI-CORE ViT-B at 224 px, frozen configuration; ImageNet EfficientNet-B3 as fallback), after a
smoke test (step S) with key, gradient, loss and reload checks and a single budget formula for
admission and stop. Gate F0 builds the deployed candidate step by step on gold (exploratory
screens); a fold-0 leg-alone submission (`v14_submit`) must reach 0.933 on the public LB before
folds 1-4; blends that include M need a measured runtime gate; pre-registered terminal states.
The gold proxy of the anchor (`scripts/anchor_proxy_gold.py`, three frozen variants) is reported
but never blocks a submission. Own LLM labels (option L) are not pursued (user decision);
external datasets stay out (no host clearance).

**Reason.** v12 scored 0.931 alone, below the 0.935 blend gate (D-014). The round-2 target scores
0.9235 on gold vs 0.9168 (CI +0.0009 to +0.0130). The anchor's public members are not stronger
than v11 on gold, so the leg must add a different pretraining domain or family (STATUS L15, L16).
Three Codex reviews (GPT-6 Astra) were verified and resolved (design sections 8-10); no standing
points. User approved 2026-10-06, including the MRI-CORE weight download.

**Consequences.** New versions: v13 (training: smoke, fold0_arms, folds), v14_submit (fold-0
diagnostic), v15_submit (5-fold leg alone), v16_submit (blend). Gold is used for selection a
fourth time; the public LB is the external check. Remote steps (dataset uploads, pushes,
submissions) still need approval each time.

## D-014 - 2026-10-04 - Strategy revision: OOF-teacher targets (v11), leg-alone gate

**Decision.** Approve `docs/research/v11-strategy-revision-design.md` revision 2.1. The own
model is retrained on `0.5 * soft target + 0.5 * v08 out-of-fold prediction` (v11). Fold 0
runs two arms in one session: A (10 epochs, LR 5e-5 / 2e-4) and B (15 epochs, LR 1e-4 /
3e-4), time limits 6 h and 9 h, global deadline 11 h; incomplete arms never enter Gate R1.
Gate R1 filters complete arms, then qualified arms (fold-0 val macro AUC at K_infer 16 >=
0.871), picks one arm by gold-58 (arm A within 0.005 of the best) and applies the rule table
to that arm. Folds 1-4 follow only per R1; then v12_submit scores the leg alone, and a blend
with the anchor is built only if the leg alone reaches 0.935 (w = 0.30) or 0.940 (w = 0.45).
Every evaluation also scores 500 fixed training studies at K_infer 16 without augmentation,
so training and validation loss are compared like-for-like. External data stays out of this
round; a team merger before 2026-10-15 is the user's decision.

**Reason.** v09 (0.932) and v10 (0.909) showed that the v08 leg is too weak to help the v05
anchor (0.943; STATUS lessons 1-2). On gold-58 the v08 model and the 4-source soft target are
complementary, and a pre-registered 50/50 mix scores 0.917, +0.027 over the target alone
(paired bootstrap 95% CI +0.010 to +0.045); forum reports name OOF pseudo-labels as their main
lever. The first Codex review (GPT-6 Astra, D-013) was verified and resolved (design section
7). At approval the user accepted two clarifications (design section 8): the measured
evaluation cost (about 17 minutes per K16 evaluation instead of 2, so arm A about 4.8 h, arm
B about 7.6 h) and the pick-first order of Gate R1. User approved 2026-10-04.

**Consequences.** Gold-58 becomes a selection set after R1 and is no longer an independent
check; the leg-alone public score is the independent test. Fold-level validation of v11 is
mildly optimistic (the teacher saw the student's validation labels). v08's OOF files are
attached to v11 as a private Kaggle dataset and the training target is computed inside the
notebook. The first iteration needs about 19-25 GPU h (up to 31 h with the R1 rerun).
`IMPROVEMENT_PLAN.md` is revised accordingly.

## D-013 - 2026-10-04 - Codex reviews use GPT-6 Astra

**Decision.** All Codex reviews of this repository use `gpt-6-astra` with reasoning effort
`high`, set in a project-scoped, git-ignored `.codex/config.toml`; review commands also pass
`--model gpt-6-astra` explicitly.

**Reason.** User request 2026-10-04. The user-level default was `gpt-5.6-sol` with effort
`low`, which the earlier reviews (D-004 to D-009) most likely ran with. A probe run in this
repository confirmed that the project file takes effect (session record: model
`gpt-6-astra`, effort `high`).

**Consequences.** Other projects keep the user-level default. The `/codex:adversarial-review`
command accepts `--model` but not an effort flag, so the effort depends on the project file.

## D-012 - 2026-10-04 - Merge the version history into STATUS.md

**Decision.** `docs/version-history.md` is removed; its content (versions table, v05 anchor
summary, own-model settings ledger, per-fold results, lessons, open hypotheses) now lives
in `docs/STATUS.md`, with the former "Best results" table folded into the versions table so
nothing is duplicated. The D-011 rule now points to `docs/STATUS.md`: read it before any
change to `IMPROVEMENT_PLAN.md` or any new strategy, and cite its versions and lessons.

**Reason.** User request 2026-10-04: one file instead of two overlapping ones.

**Consequences.** STATUS.md is longer than "short"; it is the single source for status and
results. AGENTS.md, README.md and IMPROVEMENT_PLAN.md reference STATUS.md.

## D-011 - 2026-10-04 - Version history document; plan changes must cite it

**Decision.** Keep `docs/version-history.md` as the single summary of every version's
settings, results and verdict, plus evidence-backed lessons. Every change to
`IMPROVEMENT_PLAN.md` must read it first and cite the versions and lessons that support or
contradict each direction. It is updated whenever a version gets a new result.

**Reason.** After v09 (0.932) and v10 (0.909) scored below v05 (0.943), the user asked for one
document of what was tried and what it gave, so that new plans build on measured results
rather than on assumptions. User request 2026-10-04.

**Consequences.** The session protocol (AGENTS.md) adds the update after each Kaggle run;
the D-004 Codex review of plan changes also checks consistency with this document.

## D-010 - 2026-10-03 - Submission notebooks are named vNN_submit

**Decision.** Every notebook that is submitted to the leaderboard is named
`notebooks/vNN-submit.ipynb` locally and `vNN_submit` on Kaggle (slug `vNN-submit`). The v09
blend notebook is renamed accordingly (`v09-anchor-plus-v08` -> `v09-submit`).

**Reason.** The user wants to see at a glance which version produced a leaderboard entry.
User request 2026-10-03. The local name keeps the `vNN-` prefix that the validator requires.

**Consequences.** The earlier Kaggle kernel `lingxd/v09-anchor-plus-v08` (version 1) served as
a validation run only; submissions come from `lingxd/v09-submit`. v05 keeps its name (already
submitted).

## D-009 - 2026-10-02 - K_train 4, K_infer 16; remaining folds through a GPU queue

**Decision.** Use `K_train = 4` and `K_infer = 16` for all folds of v08. Train folds 1-4 in
`MODE = 'folds'`, a work queue that starts the next fold as soon as a GPU is free, with the
final evaluation at `K_infer = 16` only.

**Reason.** Fold 0 (v08 version 1): the K_train 8 arm hit its 6 h limit, so the A0 outcome
table selects 4 (8 was also not better at K_infer 16: 0.869 vs 0.871). Gate A's rule had a
gap: it required ACL, MCL and both menisci to be within 0.005 of their best value, but
MCL peaked at K_infer 8 (0.796), so no setting qualified and the rule defined no fallback.
K_infer 16 is within 0.001 of the best macro AUC (K24 0.872), its MCL deficit of 0.008 is
inside the noise of about 90 positives, and it costs two thirds of K24 at inference, which
matters because the anchor leaves under 4 h. In version 1 the slower arm blocked GPU 0 for
about 2 h; the queue removes that idle time. User approved 2026-10-02.

**Consequences.** Future gate rules must state a fallback when no option qualifies. Our
leg's checkpoints are `v08_fold_<k>_k4_best.pt`, k = 0..4.

## D-008 - 2026-10-02 - Skip the separate Gate S run; v08 `auto` mode

**Decision.** Do not run Gate S as a separate session. v08 runs in `MODE = 'auto'`:
fold 0 with both arms (K_train 4 and 8), the Gate A0 and Gate B decisions computed in the
notebook, then folds 1 and 2 in parallel with the chosen K_train if Gate B passes and time
remains. Every arm starts with a memory probe that enables activation checkpointing and
then halves the micro-batch on out-of-memory; all processes stop cleanly before an 11 h
global deadline (Kaggle's session limit is 12 h).

**Reason.** The user reported that this week's GPU quota cannot be used up, which removes
the budget risk Gate S guarded; the remaining risks (out-of-memory, overrun) are handled
inside the run. Running overnight avoids idle GPU time. User request 2026-10-02.

**Consequences.** The 18 GPU-hour cap of design 5.1 is not binding this week. Gate S
measurements (memory, throughput, data share) come from the fold-0 receipts. v05's
hidden-test scoring took more than 5 h (user, 2026-10-02), so v09 has under 4 h of the 9 h
limit left for our leg's inference.

## D-007 - 2026-10-02 - Gate S runs on our own v07 cache

**Decision.** The Gate S smoke test runs on the v07 cache instead of the public Raptor
corpus, as `MODE = 'smoke'` of the v08 training notebook.

**Reason.** The v07 cache finished (4,407 studies, 0 errors) before the smoke test was
built, so the original reason for the public corpus (unblocking work while the cache was
pending) no longer applies. Running on our own cache measures the real input path,
including JPEG decoding, and avoids a separate corpus reader. User approved 2026-10-02.

**Consequences.** Gate S criteria, budget and later gates are unchanged; the extra
JPEG-cost measurement planned for the first epoch of fold 0 is covered by Gate S.

## D-006 - 2026-10-01 - Own model leg: design revision 3.3 approved

**Decision.** Replace revision 2's sparse cache with revision 3.3 of
`docs/research/v06-own-model-design.md`: per-slot JPEG cache of up to 32 slices over the
whole series at 320 px; adjacent-slice triplets; covering training sampler with `K_train`
4 or 8 chosen by a fold-0 ablation (Gate A0); smoke test on the final input shape
(Gate S); inference coverage and token-count check (Gate A); an 18 GPU-hour cap up to the
first v09 submission with per-session hard stops and a degradation order.

**Reason.** The v06 audit (median 30 slices, 3.5 mm gap) and the decoded code of the
public 0.945 leg showed that near-full coverage and true slice adjacency are compatible.
Four further Codex reviews were verified and resolved (design section 9); one
disagreement stands (no sparse-vs-triplet training ablation). User approved 2026-10-01.

**Consequences.** v07 builds the cache from the v06 series choice and recomputes slice
order with the same function; the v06 `slice_files` column is unused. The user records
the v05 hidden-test runtime and the week's GPU quota before Gate S.

## D-005 - 2026-10-01 - Own model leg: design revision 2 approved

**Decision.** Build our own model leg per `docs/research/v06-own-model-design.md`
revision 2: v06 DICOM audit (CPU), v07 320 px cache (CPU), v08 ConvNeXt-tiny (fold-0
224/320 ablation, then 5 folds), v09 explicit ensemble of v05 and v08 with two
pre-registered blend weights (0.45, 0.30) and a fixed decision table.

**Reason.** Revision 1 was reviewed by Codex (D-004); its five findings were verified and
addressed (design section 9). The user approved revision 2 on 2026-10-01.

**Consequences.** Labels are fixed a priori (mean of four public tables, UNK cells
down-weighted); the 58 gold studies are never trained on and serve only as a bug detector;
folds are scanner-grouped when the audit allows. Data-preparation notebooks get their own
version numbers.

## D-004 - 2026-10-01 - Codex review gate for improvement strategies

**Decision.** Every new improvement strategy or design note is reviewed by Codex (OpenAI
Codex CLI via the `codex@openai-codex` Claude Code plugin) for direction-level soundness
before any Kaggle GPU time is spent on it.

**Reason.** GPU time is the binding constraint (30 h per week until 2026-10-22); an
independent second review catches wrong directions before they cost a week of quota.

**Consequences.** Design docs stay uncommitted until reviewed so the working-tree review
sees them. Codex findings are claims to verify, not instructions; each accepted or
rejected finding is noted in the reviewed document. Procedure in `AGENTS.md` (User
preferences).

## D-003 - 2026-10-01 - v05 is the unchanged Jiwei Liu public stack

**Decision.** Version v05 (`notebooks/v05-public-stack-anchor.ipynb`) is an unchanged,
inference-only reproduction of `jiweiliu/rsna-knee-fast-2xt4-inference` version 11
(public LB 0.943). Later versions improve on it by rank-blending our own independently
trained models into it, following `IMPROVEMENT_PLAN.md` (new root-level document). The
compute budget is 30 Kaggle GPU hours per week; the goal is a medal. External knee MRI
datasets are postponed.

**Reason.** It is the highest-scoring public notebook whose inputs are all public; the
0.945-0.946 notebooks are this stack plus private models and cannot be reproduced. The
survey (`docs/research/baseline-selection.md`) shows that adding an independent model, not
reweighting the stack, is what moves the score above 0.943.

**Consequences.** v05 keeps all original cells byte-identical and only adds a provenance
cell, a version cell, and a receipt cell. It requires GPU T4 x2 and the 18 public inputs.
Our own models get new version numbers (v06+); a blend version must be defined explicitly
as an ensemble of the anchor and named versions.

## D-002 - 2026-10-01 - Agent-oriented repository layout

**Decision.** Reorganize the repository for AI-agent-driven development:
`notebooks/` for active versioned notebooks, `docs/` for shared state (status,
experiments, decisions, research), `external/` for unmodified third-party code,
`archive/legacy/` for the abandoned line, and `scripts/validate_notebooks.py` as the
standard static check.

**Reason.** Agents start each session without memory. Durable, predictable files
(`docs/STATUS.md` first) let any session resume work, and separating third-party code
from project code keeps provenance and licensing clear.

**Consequences.** `src/` was removed. Artifacts from the legacy line live under
`archive/legacy/`. New model versions continue numbering at **v05** so checkpoint and
result names never collide with archived v01-v04 artifacts.

## D-001 - 2026-09-30 - Restart from public code

**Decision.** Abandon the in-house V01-V04 line (2.5D EfficientNet-B0, report weak-label
calibration, the never-successfully-run V04 DINOv2 build) and restart from the strongest
public Kaggle notebooks.

**Reason.** After about six weeks of inactivity and with the competition closing on
2026-10-22, building on public solutions (DINOv2-based notebooks were near 0.81 public
LB in August versus our 0.664) is the fastest route to a competitive score.

**Consequences.** Do not extend legacy notebooks or reuse their design by default. The
legacy code may still be consulted as reference, for example for DICOM ordering.
