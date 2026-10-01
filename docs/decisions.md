# Decision Log

Record decisions that change project direction, conventions, or architecture. Newest
first. Each entry: ID, date, decision, reason, consequences.

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
