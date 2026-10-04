# Project Status

> Agents: read this file first at the start of every session, and **before changing
> `IMPROVEMENT_PLAN.md` or any strategy** (D-011, D-012): cite the versions and lessons below
> that support or contradict each new direction. Update it before ending a session that
> changed project state and whenever a version gets a new result. Raw run rows live in
> `experiments.md`; decisions in `decisions.md`.

Last updated: 2026-10-04

## Current phase

**Phase 3 - OOF-teacher retraining (v11)**, per `docs/research/v11-strategy-revision-design.md`
revision 2.1 (D-014, approved 2026-10-04). Phase 2 ended with the own-model leg too weak (v09
0.932 and v10 0.909, both below v05 0.943). Final selection until something beats it:
**v05 (0.943)**. Budget: 30 Kaggle GPU hours per week; goal: a medal; deadline 2026-10-22.

## Versions and results

Public LB = public leaderboard (macro ROC-AUC). CV = scanner-grouped 5-fold OOF macro AUC
against the 4-source soft targets rounded at 0.5. Gold = macro AUC on the 58 gold studies
(never trained on in v08).

| Version | Date | Type | What it is | Local result | Public LB | Verdict |
|---|---|---|---|---|---:|---|
| v01 | 2026-08-06 | legacy model | EfficientNet-B0 2.5D, rule weak labels, 1 fold | - | 0.613 | archived (D-001) |
| v02 | 2026-08 | legacy model | v01 + calibrated soft labels | OOF collapsed to base rate | - | archived |
| v03 | 2026-08-09 | legacy model | v02 + hierarchical label priors, 5 folds | gold 0.632 | 0.664 | archived; best legacy result |
| v04 | 2026-08 | legacy model | DINOv2-small, laterality norm, attention head | never trained | - | archived |
| v05 | 2026-10-01 | submit | Public stack anchor: jiweiliu v11 unchanged | - | **0.943** | **current best; only safe final pick** |
| v06 | 2026-10-01 | data (CPU) | DICOM audit, slot selection, targets, folds | all gates pass | - | done |
| v07 | 2026-10-02 | data (CPU) | 320 px JPEG cache, 4,407 studies | 0 errors, 14.56 GB | - | done |
| v08 | 2026-10-02/03 | training | ConvNeXt-tiny 2.5D, 5 folds | CV 0.840; gold 0.897 (ens.) | - | trained; too weak (see v10) |
| v09 | 2026-10-03 | submit | v05 + v08 leg, rank blend w = 0.45 | pipeline checks pass | 0.932 | **worse than v05 (-0.011)**; leg dropped |
| v10 | 2026-10-04 | submit (diagnostic) | v08 leg alone | pipeline checks pass | 0.909 | leg works on test but is weak |
| v11 | 2026-10-04 | training | v08 trainer on `0.5 * soft + 0.5 * v08 OOF`; fold-0 arms A (10 ep) / B (15 ep, higher LR); Gate R1 | local CPU checks pass (synthetic DICOM); Codex implementation review resolved | - | fold-0 run pushed 2026-10-04 (`lingxd/v11-oof-teacher` version 1); results pending |
| ref | 2026-10-01 | public notebook | pjmathematician d4-blend (private datasets, not reproducible) | - | 0.946 | reference |
| ref | 2026-10-01 | leaderboard | #1 0.961; #10 0.957; #100 0.949; 1,001 teams >= 0.943 | - | - | reference |

### Public-stack anchor (v05)

| Item | Value |
|---|---|
| Source | `jiweiliu/rsna-knee-fast-2xt4-inference` v11 (Apache 2.0), recipe of Mattia Angeli's Speedy Raptors v34 |
| Members | DINOv2-S x20, A5 x5, RadImageNet ResNet-50 heads, Raptor CoAtNet x3 (4 views), 4 Mattia CoAt readers |
| Our changes | provenance, version and receipt cells only |
| Runtime | 233 s commit run on 3 studies; hidden-test scoring more than 5 h |

## Own-model line (v06-v10): settings ledger

Design: `docs/research/v06-own-model-design.md` revision 3.3 (D-006 to D-009).

### Data and cache (v06, v07)

| Setting | Value | Evidence |
|---|---|---|
| Slots | SAG_FS, SAG_NFS, COR_FS, COR_OTHER, AX_FS (one series each; duplicate only if the plane has one series) | v06; COR_OTHER duplicates COR_FS in 25.5% of studies |
| Slice order | `ImagePositionPatient` projected on slice normal (100% of train series) | v06 audit |
| Slices stored per slot | all if N <= 32, else `linspace(0, N-1, 32)` (median 30) | v07, after the decoded 0.945 private leg |
| Crop / size | 140 mm centre crop, zero pad if smaller, 320 x 320 | design rev. 3 |
| Intensity | one 0.5-99.5 percentile window per series over the cropped field | v07 |
| Orientation | canonical from geometry; side from `Laterality` tag (49%) else image-centre x with 20 mm dead zone | v07: 98.6% tag/geometry agreement; 1.7% unresolved |
| Storage | JPEG quality 92 per slice, 14.56 GB | v07 |
| Targets | mean of 4 public LLM label tables (pilkwang, steven v2, lixin, dread); weight 0.3 where pilkwang verdict is UNK | v06; the target itself scores 0.892 on gold |
| Folds | 5, scanner-grouped (manufacturer + model + field strength; 45 groups, 94.7% coverage); gold excluded | v06; strong prevalence differences between folds |

### Model and training (v08)

| Setting | Tried | Chosen | Evidence |
|---|---|---|---|
| Backbone | ConvNeXt-tiny `fb_in22k_ft_in1k` | same | only one tried |
| Token | adjacent-slice triplet (c-1, c, c+1) of one slot, 320 px | same | - |
| Pooling | slot embedding + gated per-finding attention over all tokens | same | only one tried |
| `K_train` (centres per slot per step) | 4 vs 8 (fold 0, parallel) | **4** | 8 hit the 6 h limit; at K_infer 16: 0.869 (8, epoch 8) vs 0.871 (4) |
| `K_infer` (centres per slot at eval) | 4 / 8 / 16 / 24 | **16** | 0.850 / 0.868 / 0.871 / 0.872 (fold 0); D-009 |
| Epochs, LR | 10; AdamW 5e-5 backbone, 2e-4 head, cosine, 1 warm-up epoch | same | val AUC still rising slowly at epoch 10 (fold 0: 0.866 -> 0.868) |
| Batch | effective 8 studies (micro 2 x accum 4), fp16 | same | peak 5.8 GB of 16 GB: memory not a constraint |
| Augmentation | rotation +-10, scale 0.9-1.1, shift 5%, gamma/brightness; no flip | same | not ablated |
| Throughput | 67.5 img/s per arm (two arms sharing 4 CPUs), data share 0.28-0.37 | - | CPU-bound decoding/augmentation |
| Fold time | 3.7-4.1 h on one T4 | - | v08 runs 1 and 2 |

### v08 results per fold (K_infer 16)

| Fold | Val macro AUC | Gold-58 |
|---|---:|---:|
| 0 | 0.871 | 0.896 |
| 1 | 0.837 | 0.883 |
| 2 | 0.835 | 0.885 |
| 3 | 0.830 | 0.892 |
| 4 | 0.839 | 0.892 |
| 5-fold | pooled OOF 0.840 | rank ensemble 0.897 (CI 0.864-0.924) |

Weakest pooled OOF labels: MCL 0.750, Lateral OA 0.783, PF OA 0.783, Lateral Meniscus
0.813. Strongest: Baker's 0.909, Medial Meniscus 0.901, Fracture 0.886. Fold-to-fold
Spearman on gold 0.92 (little ensemble diversity).

### Submissions built on v08

| Version | Blend | Inference | Public LB | Delta vs v05 |
|---|---|---|---:|---:|
| v09 | rank(0.55 anchor + 0.45 v08) | 5 folds, K_infer 16; reference check byte-equal | 0.932 | -0.011 |
| v10 | v08 alone (mean of fold ranks) | same | 0.909 | -0.034 |

## Lessons (evidence-backed)

1. **The public stack is a high floor.** v05 = 0.943 with zero training; any added model must
   be strong on its own to help.
2. **A 0.909 model blended at 0.45 lowers a 0.943 anchor by 0.011** (v09 vs v10). A weak leg
   is not "free diversity"; blend weight must reflect relative strength.
3. **Local metrics map to the public LB roughly as gold 0.897 -> LB 0.909.** A forum report
   puts a 0.950-LB single model at about 0.930 on the same gold set, so the gold-58 gap
   (about 0.03) was a usable early warning that we did not act on.
4. **The model did not exceed its labels on gold** (0.897 vs the 4-source target's 0.892,
   inside the CI). Label quality and how the model learns beyond it are the bottleneck
   candidates, consistent with the forum.
5. **Engineering is sound:** test-time preprocessing reproduces the training cache
   byte-for-byte on Kaggle; 100% coverage on placeholder tests; Pillow with JPEG 2000 is in
   the image. The 0.909 is a modelling result, not a pipeline bug (v10 band 0.88-0.92).
6. **Coverage at inference matters:** K_infer 4 -> 16 gave +0.021 val AUC (fold 0).
   K_train 8 did not beat 4.
7. **Scanner-grouped folds are harder and uneven:** fold 0 0.871 vs folds 1-4 0.830-0.839,
   driven by prevalence and scanner mix.
8. **Process costs:** a full own-model cycle (audit, cache, 5 folds, two submissions) took
   about 3 days and roughly 14 GPU hours (v08 runs 6.5 h + 7.6 h) plus about 6 h of scoring.

## Open hypotheses for why v08 is weak (untested)

Each needs evidence before it drives `IMPROVEMENT_PLAN.md`:

- Too few training tokens per study (K_train 4 x 5 slots = 20) and only 10 epochs.
- Low backbone LR (5e-5) with a small effective batch; untested alternatives.
- Soft targets include the weakest table (lixin, 0.835 on gold); untested single-source runs.
- 140 mm / 320 px geometry versus forum reports of 224-288 px working well; resolution was
  not ablated after design revision 3.
- Attention pooling over all slots versus simpler per-slot pooling; not ablated.

## Next steps

1. v11 is built (`notebooks/v11-oof-teacher.ipynb`; v08 OOF in the private dataset
   `lingxd/rsna-knee-v08-oof`): v08 trainer with targets
   `0.5 * soft + 0.5 * v08 OOF`, fold-0 arms A and B, like-for-like train/val loss, Gate R1
   (design 4.1-4.2).
2. v11 fold 0 is running (version 1, about 7.7 h; pushed 2026-10-04). When it finishes: download
   receipts and `v11_decision_r1_attempt1.json`, record in `experiments.md`, apply Gate R1; folds 1-4 only if R1 says so; then v12_submit
   (leg alone) and the blend gate (design 4.4).
3. Keep v05 (0.943) as the final selection until something beats it.

## Open questions

- Hidden-test DICOM transfer syntaxes are unknown (training and the sampled placeholder test
  files are uncompressed); the pinned Kaggle image has Pillow 11.3.0 with JPEG 2000 (v10).
- Whether bf16 autocast in the stack's A5 stage costs AUC on T4.
- External knee MRI datasets: postponed by the user.

## Environment

- Local Python: conda env `kaggle` (Python 3.11) on PATH; recipe in `environment.yml`.
- Kaggle access: `KAGGLE_API_TOKEN` user environment variable (never print it); Kaggle
  CLI plus the `nvidia-kaggle` and `kaggle@shepsci` Claude Code plugins.
- Training and submission run on Kaggle GPUs only.
- GPU quota: `kaggle quota` shows hours used and left. Windows of 30 h reset on Saturdays at
  00:00 UTC; submission scoring reruns do not count (2026-10-04: 0.18 h used, 29.82 h left
  until 2026-10-10).
