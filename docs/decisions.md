# Decision Log

Record decisions that change project direction, conventions, or architecture. Newest
first. Each entry: ID, date, decision, reason, consequences.

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
