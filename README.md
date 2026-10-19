# RSNA Knee Abnormality Detection

Working repository for the
[RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)
Kaggle competition: study-level detection of 12 knee abnormalities from multiplanar MRI
and radiology reports, scored by macro-averaged ROC-AUC. Final deadline: 2026-10-22.

Development is primarily AI-agent-driven. Agents follow `AGENTS.md` (kept local) and
share state through `docs/`.

## Status

The project restarted on 2026-09-30 from strong public Kaggle code. The earlier in-house
V01-V04 line (best public LB 0.664) is archived in `archive/legacy/`.

As of 2026-10-19 (final phase, inference-only, decisions D-033 to D-035):

| | Version | Public LB |
|---|---|---|
| Best overall | v68: goodpjw2008's public V25 recipe reproduced byte-equal (nartaa's CoAtNet-384 + 224-px CoAtNet with anatomical mirror, heliosli's R6 ConvNeXt-small with flip TTA, per-finding rank weights, a small 2.5D reader) | 0.958 |
| Best uniform-weight hedge | v71 / v73 (v68 with uniform or shrunk per-finding weights) | 0.957 |
| Best own model alone | v36 P (2.5D ConvNeXt-tiny, report-derived soft targets) | 0.937 |
| Best without OAI-derived weights | v15 | 0.944 |

Within the crowded 0.958 block, versions are compared by rank crossing between leaderboard snapshots (hidden-digit
evidence, `scripts/d033/rank_cross.py`). Every own addition to the strongest public recipe has lost a display step
(lessons L46-L50). Current phase, every version's settings and results, lessons, and next steps live in
[docs/STATUS.md](docs/STATUS.md); the run log is [docs/experiments.md](docs/experiments.md).

## Layout

```text
.
|-- README.md
|-- IMPROVEMENT_PLAN.md      # prioritized directions (as of 2026-10-10; later plans in docs/STATUS.md)
|-- environment.yml          # local conda env for analysis and CPU tests
|-- environment-gpu.yml      # local GPU training env (RTX 3080 Ti, D-016)
|-- docs/
|   |-- STATUS.md            # current state, versions, settings, lessons (read first)
|   |-- competition.md       # verified task, metric, rules, and data facts
|   |-- experiments.md       # append-only log of Kaggle runs and scores
|   |-- decisions.md         # decision log
|   `-- research/            # analyses of public notebooks and discussions
|-- notebooks/               # versioned notebooks: vNN-<name>.ipynb, submissions vNN-submit.ipynb (from v05)
|-- scripts/
|   |-- validate_notebooks.py           # static notebook checks (run after every notebook change)
|   |-- check_notebook_names.py         # notebook naming convention check
|   |-- anchor_proxy_gold.py            # gold-58 proxy of the public anchor (diagnostic)
|   |-- local_v13.py, local_v23.py      # run notebook cells on the local GPU (D-016)
|   |-- audit_v28_cache.py              # cache audit (v28)
|   |-- gold_label_sources.py           # label-source comparison on the 58 gold studies
|   |-- llm_label_pilot.py              # report-label pilot (with llm_label_rubric_v1.md)
|   |-- inspect_kaggle_train_images.py  # read-only DICOM layout audit (runs on Kaggle)
|   `-- d033/                           # final-phase tools: notebook builders (build_v63.py builds v63-v66),
|                                       # gate checks, rank_cross.py (leaderboard rank-crossing test)
|-- archive/legacy/          # abandoned V01-V04 notebooks and original README
|-- data/                    # official CSVs (not tracked)
|-- external/                # pulled third-party notebooks (kernels/), datasets, weights, leaderboard
|                            # snapshots (lb/) (not tracked)
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
   `python scripts/validate_notebooks.py`. A public notebook is reproduced unchanged apart from a provenance
   cell (and versioned input datasets where the original reads an unversioned one).
3. Run on Kaggle: training runs single fold first, then full cross-validation. Submission notebooks
   (`vNN-submit`) get a commit run whose outputs are audited (stage files, receipts, and, for public copies,
   byte equality with the author's run) before they are submitted.
4. Judge: take a leaderboard snapshot before each submission and after its score
   (`kaggle competitions leaderboard -c rsna-knee-abnormality-detection --download -p external/lb/<name>`),
   then run `python scripts/d033/rank_cross.py <before> <after>`; a version is adopted with at least 20 stable
   witnesses and no reverse crossings.
5. Record: append the run to `docs/experiments.md` and update `docs/STATUS.md`.
