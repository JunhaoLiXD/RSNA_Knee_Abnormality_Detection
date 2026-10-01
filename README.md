# RSNA Knee Abnormality Detection

Working repository for the
[RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)
Kaggle competition: study-level detection of 12 knee abnormalities from multiplanar MRI
and radiology reports, scored by macro-averaged ROC-AUC. Final deadline: 2026-10-22.

Development is primarily AI-agent-driven. Agents follow `AGENTS.md` (kept local) and
share state through `docs/`.

## Status

The project restarted on 2026-09-30 from strong public Kaggle code. The earlier in-house
V01-V04 line (best public LB 0.664) is archived in `archive/legacy/`. Current phase,
best scores, and next steps live in [docs/STATUS.md](docs/STATUS.md).

## Layout

```text
.
|-- README.md
|-- environment.yml          # local conda env (analysis only; training runs on Kaggle)
|-- docs/
|   |-- STATUS.md            # current state and next steps (read first)
|   |-- competition.md       # verified task, metric, rules, and data facts
|   |-- experiments.md       # append-only log of Kaggle runs and scores
|   |-- decisions.md         # decision log
|   `-- research/            # analyses of public notebooks and discussions
|-- notebooks/               # active versioned notebooks: vNN-<name>.ipynb (from v05)
|-- scripts/
|   |-- validate_notebooks.py           # static notebook checks
|   `-- inspect_kaggle_train_images.py  # read-only DICOM layout audit (runs on Kaggle)
|-- archive/legacy/          # abandoned V01-V04 notebooks and original README
|-- data/                    # official CSVs (not tracked)
|-- external/                # pulled third-party code (not tracked)
|-- models/                  # checkpoints by version (not tracked)
`-- results/                 # retained run outputs by version (not tracked)
```

## Setup

```bash
conda env create -f environment.yml
```

Set a Kaggle API token as the user environment variable `KAGGLE_API_TOKEN`, then check
access:

```bash
kaggle competitions list -s rsna-knee
```

## Workflow

1. Research: pull public notebooks into `external/kernels/` and write analyses in
   `docs/research/`.
2. Build: create `notebooks/vNN-<name>.ipynb` and validate it:
   `python scripts/validate_notebooks.py`.
3. Run on Kaggle: single fold first, then full cross-validation; submit.
4. Record: append the run to `docs/experiments.md` and update `docs/STATUS.md`.
