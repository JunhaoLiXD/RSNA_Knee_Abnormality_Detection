# RSNA Knee Abnormality Detection

Working repository of team **JerryMouse** for the
[RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection) Kaggle
competition (2026): study-level detection of 12 knee abnormalities from multiplanar MRI, scored by macro-averaged
ROC-AUC. The competition closed on 2026-10-22.

Development was primarily AI-agent-driven (Claude Code, with Codex as a reviewer). Agents kept their shared state in
[`docs/`](docs/); every decision, run and lesson is recorded there.

## Result

| | |
|---|---|
| Private leaderboard | **rank 486 of 6,425** (top 7.6%, bronze zone; final standings pending Kaggle's verification) |
| Selected submissions | `v90` and `v93`, both **private 0.943** (public 0.958); the two best of our 71 scored submissions |

## Final solution

The final submissions build on the strongest public recipe (goodpjw2008's V25, public 0.958) and change how its models are
combined:

- **Models (all public, inference only):** nartaa's CoAtNet-384 (trained with OAI data) and its 224-px sibling with an
  anatomical mirror TTA; heliosli's compact ConvNeXt-small R6 with flip TTA (R7 as a second compact model in `v93`); a small
  2.5D ConvNeXt reader by goodpjw2008.
- **Our changes:**
  1. `v80`: a smaller share of the 224-px CoAtNet in the CoAtNet half (0.35 -> 0.25).
  2. `v89` -> `v90`: **z-logit fusion.** Instead of averaging percentile ranks, each model's probabilities enter as
     standardised logits (mean 0, sd 1 per finding over the test set), so a model's confidence counts; the weights stay the
     same. This was the largest gain of the final phase on the public board and the only change that lifted the private
     score (0.942 -> 0.943).
  3. `v93` (the hedge): the same fusion with uniform per-finding weights plus R7, so the second pick does not depend on the
     per-finding weights, which sat at a sharp public-leaderboard optimum. On private it tied with `v90`.
- **How versions were compared:** inside the crowded 0.958 block, by rank crossings between leaderboard snapshots
  (`scripts/d033/rank_cross.py`): a version is adopted when at least 20 stable teams move from above to below us and none
  move the other way.

Details: [`docs/research/final-pair-2026-10-22.md`](docs/research/final-pair-2026-10-22.md) (final pair and its Codex review),
[`docs/STATUS.md`](docs/STATUS.md) (all versions, settings and lessons), [`docs/experiments.md`](docs/experiments.md) (run log).

## Project history

| Phase | Dates | What happened | Best public LB |
|---|---|---|---|
| Legacy line (archived) | Aug 2026 | In-house EfficientNet 2.5D models on report-derived labels | 0.664 |
| Restart from public code | Sep 30 - Oct 1 | Public stack reproduced as an anchor (D-001) | 0.943 |
| Own models | Oct 1 - Oct 13 | DICOM audit and cache, ConvNeXt-tiny 2.5D models with OOF-teacher targets, local-view legs; best own model alone 0.937, best non-OAI blend 0.944 (`v15`) | 0.944 |
| OAI-based anchor and blends | Oct 8 - Oct 15 | Public CoAtNet + compact models + readers, our leg at small weights | 0.957 |
| Final phase | Oct 16 - Oct 22 | Public 0.958 recipes reproduced, blend probes, z-logit fusion, final pair | 0.958 |

## Credits

The final submissions run public notebooks and checkpoints unchanged apart from the blend; thanks to their authors:

- **[nartaa](https://www.kaggle.com/nartaa)**: CoAtNet-384 and 224-px CoAtNet SWA checkpoints (OAI-trained), all-data S6.
- **[heliosli](https://www.kaggle.com/heliosli)**: compact models S6 / R6 / R7, the flip-TTA worker, per-finding weights, the
  SKM-TEA anatomy anchor and the public blend notebooks.
- **[goodpjw2008](https://www.kaggle.com/goodpjw2008)**: the V25 recipe (R224 mirror, R6 with flip TTA, per-finding weights) and
  the 2.5D ConvNeXt reader.
- **[rostigor](https://www.kaggle.com/rostigor)**: the versioned R6 mirror dataset.
- Earlier anchors: sujanmajhisuzan (apex grandmaster stack), jiweiliu and Mattia Angeli (Speedy Raptors), and the authors of
  the public report-label tables. Each derived notebook keeps a provenance cell with its source, version and license
  (mostly Apache 2.0); analyses of the public notebooks are in [`docs/research/`](docs/research/).

*OAI acknowledgement (the CoAtNet weights were trained with OAI data).* Data and/or research tools used in the preparation of
this work were obtained and analyzed from the controlled access datasets distributed from the Osteoarthritis Initiative
(OAI), a data repository housed within the NIMH Data Archive (NDA). OAI is a collaborative informatics system created by the
National Institute of Mental Health and the National Institute of Arthritis, Musculoskeletal and Skin Diseases (NIAMS) to
provide a worldwide resource to quicken the pace of biomarker identification, scientific investigation and OA drug
development. Dataset identifier(s): 10.15154/0hcg-f676.

## Layout

```text
.
|-- README.md
|-- IMPROVEMENT_PLAN.md      # prioritized directions (as of 2026-10-10; later plans in docs/STATUS.md)
|-- environment.yml          # local conda env for analysis and CPU tests
|-- environment-gpu.yml      # local GPU training env (RTX 3080 Ti, D-016)
|-- docs/
|   |-- STATUS.md            # state, every version's settings and results, lessons L1-L53
|   |-- competition.md       # verified task, metric, rules and data facts
|   |-- experiments.md       # append-only log of Kaggle runs and scores (public and, after the deadline, private)
|   |-- decisions.md         # decision log D-001 to D-036
|   `-- research/            # analyses of public notebooks, design notes, final-pair analysis
|-- notebooks/               # versioned notebooks vNN-<name>.ipynb; submissions vNN-submit.ipynb (v05-v94)
|-- scripts/
|   |-- validate_notebooks.py           # static notebook checks (run after every notebook change)
|   |-- check_notebook_names.py         # notebook naming convention check
|   |-- local_v13.py, local_v23.py      # run notebook cells on the local GPU (D-016)
|   |-- anchor_proxy_gold.py            # gold-58 proxy of the public anchor (diagnostic)
|   |-- audit_v28_cache.py              # cache audit (v28)
|   |-- gold_label_sources.py           # label-source comparison on the 58 gold studies
|   |-- llm_label_pilot.py              # report-label pilot (with llm_label_rubric_v1.md)
|   |-- inspect_kaggle_train_images.py  # read-only DICOM layout audit (runs on Kaggle)
|   `-- d033/                           # final-phase tools: public-copy and weight builders, gate checks,
|                                       # rank_cross.py (leaderboard rank-crossing test)
`-- archive/legacy/          # abandoned V01-V04 notebooks and original README
```

Not tracked: `data/` (official CSVs), `external/` (pulled third-party notebooks, datasets, leaderboard snapshots),
`models/` and `results/` (checkpoints and run outputs by version).

## Reproducing a submission

Every `notebooks/vNN-submit.ipynb` is a self-contained Kaggle notebook (GPU T4 x2, internet off). To rerun one, import it
into Kaggle, attach the competition and the datasets listed in its provenance cell (all public), and submit it to the
competition. Local setup for analysis:

```bash
conda env create -f environment.yml
```

Set a Kaggle API token as the environment variable `KAGGLE_API_TOKEN`, then check access:

```bash
kaggle competitions list -s rsna-knee
```

## Workflow used

1. **Research:** pull public notebooks into `external/kernels/` and write analyses in `docs/research/`.
2. **Build:** create `notebooks/vNN-<name>.ipynb` and validate it with `python scripts/validate_notebooks.py`. Public
   notebooks are reproduced unchanged apart from a provenance cell (and versioned input datasets where needed).
3. **Run:** training runs single fold first, then full cross-validation. Submission notebooks get a commit run whose outputs
   are audited (stage files recomputed offline, receipts, byte equality with the author's run for public copies) before
   submission.
4. **Judge:** take a leaderboard snapshot before each submission and after its score, then run
   `python scripts/d033/rank_cross.py <before> <after>`.
5. **Record:** append the run to `docs/experiments.md`, update `docs/STATUS.md`, and log decisions in `docs/decisions.md`.
