# Project Status

> Agents: read this file first at the start of every session, and **before changing
> `IMPROVEMENT_PLAN.md` or any strategy** (D-011, D-012): cite the versions and lessons below
> that support or contradict each new direction. Update it before ending a session that
> changed project state and whenever a version gets a new result. Raw run rows live in
> `experiments.md`; decisions in `decisions.md`.

Last updated: 2026-10-09 (shortlist E6/E1/E5/E4: v21 built, v22 and v23 done, v24 fold 0 running)

## Current phase

**Phase 5 - OAI-based public anchor plus our leg** (2026-10-08). Phase 4 (v13 round-2 teacher)
finished: our 5-fold arm-N leg scores 0.936 alone (v13_submit) and 0.944 blended into the old v05
stack (v15). All public notebooks at 0.949-0.950 share one CoAtNet-384 checkpoint trained with OAI
data; the user adopted it despite the unresolved rule risk (D-019). v17 (public 0.950 notebook
unchanged) reproduced **0.950**; v19 (v17 + our leg at w 0.15) also **0.950** (tie at 3 decimals;
ranking uses unrounded scores). v20 (w 0.25) scored 0.949 (rejected).
Our leg adds about nothing to this base (L21). Leaderboard 2026-10-09 01:52 UTC: **rank 268 of 5,543**, inside silver (cut rank 277)
but the 0.950 block spans ranks 186-591 and is growing. Final selection now: **v19 (0.950) + v15
(0.944, non-OAI)**. Deadline 2026-10-22; entry and team-merger deadline 2026-10-15.

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
| v05 | 2026-10-01 | submit | Public stack anchor: jiweiliu v11 unchanged | - | 0.943 | superseded by v17/v19 (OAI-based); base of the non-OAI pick v15 |
| v06 | 2026-10-01 | data (CPU) | DICOM audit, slot selection, targets, folds | all gates pass | - | done |
| v07 | 2026-10-02 | data (CPU) | 320 px JPEG cache, 4,407 studies | 0 errors, 14.56 GB | - | done |
| v08 | 2026-10-02/03 | training | ConvNeXt-tiny 2.5D, 5 folds | CV 0.840; gold 0.897 (ens.) | - | trained; too weak (see v10) |
| v09 | 2026-10-03 | submit | v05 + v08 leg, rank blend w = 0.45 | pipeline checks pass | 0.932 | **worse than v05 (-0.011)**; leg dropped |
| v10 | 2026-10-04 | submit (diagnostic) | v08 leg alone | pipeline checks pass | 0.909 | leg works on test but is weak |
| v11 | 2026-10-04 | training | v08 trainer on `0.5 * soft + 0.5 * v08 OOF`; fold-0 arms A (10 ep) / B (15 ep, 2x LR) | fold 0: val A 0.884 / B 0.898; gold A 0.895 / B 0.911 | - | Gate R1 rule 3, arm B; **5 folds done**: pooled OOF 0.875, gold 5-fold 0.913 (v08 0.897); v12 next |
| v12 | 2026-10-05 | submit (gate) | v11 arm-B 5-fold leg alone (v10 leg code); weights metadata check; end-to-end OOF check | commit run: reference check byte-equal, OOF check pass (max diff 1e-6), 3/3 coverage | 0.931 | +0.022 over v10 but below the 0.935 blend gate: no blend |
| v13 | 2026-10-06 | training | Round-2 teacher (arm N, ConvNeXt-tiny) and MRI-CORE ViT-B/16 (arm M; EfficientNet-B3 fallback E), target `0.5 soft + 0.5 v11 OOF` | F0: N gold 0.920 (+0.009 over v11 fold 0, CI +0.003 to +0.017); M gold 0.881 (below 0.900 floor) | - | Gate F0: C = N-only; step D passed (v14 0.934); folds 1-4 on the local GPU (D-016): fold 1 val 0.872 / gold 0.917 (v11 fold 1 0.910); fold 2 (rerun after a Windows commit-limit failure) val 0.863 / gold 0.915 (v11 0.911); fold 3 val 0.868 / gold 0.918; fold 4 val 0.871 / gold 0.916. **5 folds done: gold 5-fold 0.920 vs v11 0.913 (+0.007, CI +0.002 to +0.013)**; pooled OOF 0.873 (v11 0.875); v13_submit commit run (2026-10-08): reference and OOF checks pass (local-trained folds match on Kaggle to 5.5e-5); submitted 2026-10-08 (ref 56934683): **public LB 0.936** |
| v14 | 2026-10-06 | submit (step D) | v13 arm-N fold-0 leg alone (v12 notebook generalised to a list of (version, arm, fold) models; fold-to-model OOF check) | built; local CPU tests pass (single-model rank, OOF controls, two-model mapping, wrong-checkpoint rejection) | 0.934 | one fold beats v12's 5-fold v11 leg (0.931); passes the 0.933 step-D threshold: N folds 1-4 (commit run: reference and OOF checks pass, OOF diff 0.0) |
| v15 / v16 | 2026-10-08 | submit (blends, D-018) | v05 anchor (cells unchanged from v09) + v13 arm-N 5-fold leg, rank blend at w 0.30 (v15) / 0.45 (v16) | built; local tests of the leg and blend cells pass (fallback keeps the anchor; blend formula) | **0.944** / 0.943 | v15 is the first own submission above v05; final picks v05 + v15 (D-018). Leaderboard moved: on 2026-10-08 bronze needs 0.947 (rank 549 of 5,493), we are rank 844 |
| v17 | 2026-10-08 | public anchor (D-019) | sujanmajhisuzan/rsna-knee-apex-grandmaster-stack v1 unchanged: CoAtNet-384 SWA (OAI-trained, nartaa) + goodpjw2008 ConvNeXt reader, per-finding rank weights | commit run passes (weights hash verified, fusion applied); submitted 2026-10-08 (ref 56958475) | **0.950** | reproduces the source; new anchor (rank 247 of 5,537 on 2026-10-08 together with v19) |
| v18 | 2026-10-08 | audit (gold diagnostic) | the v17 components (CoAtNet-384 inference cell with its data root pointed at a gold-58 tree; ConvNeXt reader infer.py) on the 58 gold studies, for blend analysis with our v13 N leg | built; gold-tree cell tested locally with the real CSVs; run 2026-10-08 (188 s) | gold: CoAtNet 0.923, reader 0.915, v17 0.925, N 0.920 | N-CoAtNet gold noise corr 0.81 (reader 0.79); fusion design v19/v20 under Codex review |
| v19 / v20 | 2026-10-08 | submit (blends, design v19-fusion rev 2) | v17 anchor (cells unchanged) + v13 arm-N 5-fold leg, outer rank blend at w 0.15 (v19) / 0.25 (v20); absolute leg deadline, byte-equal reference, OOF over 5 folds at 1e-3 | built; local tests of the leg and blend cells pass (fallback, blend formula, deadline kill) | - | commit runs pass all three gates (base = v17 byte for byte; reference byte-equal on the v17 image; OOF 5 folds <= 5.5e-5; blend recomputed); **v19 0.950** (= v17; tie keeps v19 per the decision rule); **v20 0.949** (below v19: rejected; v19 stays the pick) |
| v21 | 2026-10-09 | submit (E6, D-020) | v17 CoAtNet cells + v13 arm-N 5-fold leg in place of the public reader, per-finding TW fusion | commit run: all three gates pass (base = v17 CoAtNet byte for byte; leg checks; TW recomputation exact) | 0.949 | rejected (below v19's 0.950); the public reader is the better partner (L26) |
| v22 | 2026-10-09 | training (E1, D-020) | v13 arm N with target T3 (CC0 Gemini report labels as a fifth source), local fold 0 | val 0.8990 (v13 F0 0.8988); gold 0.9182 (v13 F0 0.9200; -0.0020, CI -0.0091 to +0.0050) | - | no gain: predictions match v13 F0 (Spearman 0.98); fold-0 LB check optional |
| v23 | 2026-10-09 | training (E5, D-020) | public OAI CoAtNet through the v07 adapter, adapted 3 epochs on the round-2 target + self-distillation, local | adapter alone gold 0.9255 (v18 exact 0.9228, Spearman 0.984); adapted 0.9230 (-0.0025 vs untouched, CI -0.0088 to +0.0035) | - | not admitted (design 4.3): E5 stopped |
| v24 | 2026-10-09 | training (E4, D-020) | own CoAtNet-rmlp-2 (ImageNet-12k, no OAI), round-2 target, local fold 0 | fold 0: val 0.8943 (N F0 0.8988), gold 0.9166 (N F0 0.9200); Spearman with N 0.95 (gold) / 0.94 (val); N+C rank mean gold 0.9213 | - | v24_submit (fold-0 leg) commit run pushed 2026-10-10; LB gate >= 0.937 for folds 1-4 |
| ref | 2026-10-01 | public notebook | pjmathematician d4-blend (private datasets, not reproducible) | - | 0.946 | reference |
| ref | 2026-10-01 | leaderboard | #1 0.961; #10 0.957; #100 0.949; 1,001 teams >= 0.943 | - | - | reference |
| ref | 2026-10-05 | public notebooks | no public notebook above 0.946; reproducible ceiling still 0.943 (`docs/research/public-landscape-2026-10-05.md`) | - | - | reference |
| ref | 2026-10-05 | leaderboard | 5,184 teams; #1 0.963; #10 0.959; #100 0.951; silver line 0.945; >= 0.944 is inside bronze; 0.943 block ranks 370-1,375; we are #1,278 | - | - | reference |
| ref | 2026-10-08 | public notebooks | twelve at 0.949-0.950, all on the OAI-trained CoAtNet-384 SWA (nartaa); 0.950 = + goodpjw2008 ConvNeXt reader (`public-landscape-2026-10-08.md`) | - | 0.950 | reference |
| ref | 2026-10-08 | leaderboard | 5,537 teams (~23:00 UTC); #1 0.964; 0.950 block ranks 176-554; silver cut rank 276 and bronze cut rank 553 both at 0.950; we are #247 | - | - | reference |
| ref | 2026-10-10 | public notebooks | best verified 0.954 (heliosli: CoAtNet 0.7 + anatomy-anchored compact ConvNeXt-small "S6" using the SKM-TEA segmenter, 0.3); 0.951 forks with an older S6 bundle; S6 files retired 2026-10-09 13:50 UTC, notebooks no longer runnable (`public-landscape-2026-10-10.md`) | - | 0.954 | reference |
| ref | 2026-10-10 | leaderboard | 5,641 teams (05:13 UTC); #1 0.964; 331 teams above 0.950; 0.950 block ranks 332-837; **silver cut rank 282 at 0.951**; bronze cut rank 564 at 0.950; we are #497 | - | - | reference |

### OAI-based anchor (v17; base of v19/v20)

| Item | Value |
|---|---|
| Source | `sujanmajhisuzan/rsna-knee-apex-grandmaster-stack` v1 (Apache 2.0), unchanged |
| Members | nartaa CoAtNet-384 SWA (`coatnet_rmlp_2_rw_384`, 96 slices, 94 windows, native 320 crop, mirror TTA; trained with 2,399 OAI knees; public 0.949 alone) + goodpjw2008 2.5D ConvNeXt-tiny reader (3 folds; 0.929 alone), per-finding rank weights 0.03-0.35 |
| Docker image | `gcr.io/kaggle-private-byod/python@sha256:2757e0c...` (Python 3.13, OpenCV 4.14) |
| Runtime | 73 s commit run on 3 studies; author reports about 26 min turnaround for the CoAtNet entry |
| Gold-58 (v18) | CoAtNet 0.923, reader 0.915, v17 0.925 (gold under-rates the CoAtNet: LB offset +0.026 vs +0.016 for our N) |
| Known gap | the reader's `pylibjpeg-libjpeg` wheel does not install on this image (cp311/cp312 only) |

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

### v11 fold 0 (OOF-teacher targets; Kaggle version 1, 2026-10-04)

Both arms completed (A 5.13 h, B 7.49 h; session 7.5 GPU h; peak 6.6 GB; one K16 evaluation
1,047 s = 685 s validation + 362 s training subset). Training targets reproduced locally
(SHA-256 equal); both arms used the same 500-study training subset.

| Metric (K_infer 16) | v08 fold 0 | v11 A | v11 B |
|---|---:|---:|---:|
| Fold-0 val macro AUC (soft >= 0.5; v11 mildly optimistic, design 3.2) | 0.871 | 0.884 | 0.898 |
| Gold-58 macro AUC | 0.896 | 0.895 | **0.911** (CI 0.881-0.931) |
| Best epoch / epochs | 9 / 10 | 9 / 10 | 13 / 15 |

Paired bootstrap on gold (2,000 resamples): B - A +0.016 (95% CI +0.006 to +0.026); B - v08
fold 0 +0.015 (+0.004 to +0.027); A - v08 fold 0 -0.000 (-0.010 to +0.009); B - teacher mix
(0.917) -0.006 (-0.025 to +0.012). Largest per-label gold gains of B over v08 fold 0: MCL
0.887 -> 0.952, Medial OA 0.947 -> 0.983; ACL 0.952 -> 0.940.

Like-for-like loss (same checkpoint, no augmentation, K16): fold-0 validation targets have lower
entropy than the training subset (0.424 vs 0.451; prevalence 0.237 vs 0.279), so raw validation
loss is below training loss; the comparison uses excess loss (loss minus target entropy). A ends
with validation 0.034 vs training 0.028 (AUC gap +0.003): close, still improving. B ends with
0.032 vs 0.019 (training-subset AUC 0.923 vs validation 0.898); B's validation AUC is flat from
epoch 9 (0.8975) to 14 (0.8977).

Gate R1 (`v11_decision_r1_attempt1.json`): both complete and qualified; B picked (gold 0.911 vs
0.895, beyond the 0.005 tie); rule 3 (gold in [0.905, 0.915)): train folds 1-4 with B if the
quota covers 18.2 h; `kaggle quota` after the run: 22.31 h left until 2026-10-10.

### v11 folds 1-2 (arm B, Kaggle version 2, 2026-10-05)

| Fold | Val macro AUC (v08) | Gold-58 (v08) | Best epoch | Hours |
|---|---:|---:|---:|---:|
| 1 | 0.873 (0.837) | 0.910 (0.883) | 14 / 15 | 6.48 |
| 2 | 0.862 (0.835) | 0.911 (0.885) | 10 / 15 | 6.37 |

Gold 3-fold rank ensemble (folds 0-2): v11 B 0.912 vs v08 same folds 0.894 (paired bootstrap
+0.019, CI +0.009 to +0.030) and v08 5-fold 0.897 (+0.015, CI +0.005 to +0.027); teacher mix
0.917 (-0.005, CI -0.023 to +0.013). Per label vs v08 3-fold: MCL 0.875 -> 0.948, Lateral
Meniscus 0.795 -> 0.855, Fracture 0.907 -> 0.949; ACL 0.955 -> 0.940, PF OA 0.837 -> 0.829.
Fold-to-fold gold Spearman 0.968 (v08 0.918): single folds already give 0.910-0.911, so the
5-fold ensemble is expected to add little. Pooled OOF folds 0-2: 0.879 vs v08 0.846 (mildly
optimistic, design 3.2).

### v11 folds 3-4 and the 5-fold leg (arm B, Kaggle version 5, 2026-10-05)

| Fold | Val macro AUC (v08) | Gold-58 (v08) | Best epoch | Hours |
|---|---:|---:|---:|---:|
| 3 | 0.868 (0.830) | 0.911 (0.892) | 13 / 15 | 6.75 |
| 4 | 0.870 (0.839) | 0.911 (0.892) | 13 / 15 | 6.97 |

Versions 3 and 4 had failed at session start because Kaggle could not mount the v07 cache output
(`ERRORED_MOUNTING_DATASET`, read on the version-4 log page); v07 was rerun unchanged with its
original image (version 3, byte-identical, see `experiments.md`) and version 5 ran normally.

5-fold leg: pooled OOF 0.875 (v08 0.840; mildly optimistic). Gold rank ensemble **0.913** (CI
0.881-0.938) vs v08 0.897: +0.016 (paired CI +0.006 to +0.027); vs teacher mix 0.917: -0.004 (CI
-0.022 to +0.014); vs soft target 0.892: +0.021 (CI -0.005 to +0.048). Single folds all 0.910-0.911;
fold-to-fold gold Spearman 0.969 (v08 0.921), so the ensemble adds about 0.002. Per label vs v08
5-fold: MCL +0.052, Lateral Meniscus +0.048, Fracture +0.031, Lateral OA +0.022; ACL -0.007, PF OA
-0.008, Contusion -0.006. All five checkpoints are in `models/v11/` (git-ignored).

### v13 arm N (round-2 teacher; the leg in v13_submit, v15/v16, v19/v20)

| Setting | Value |
|---|---|
| Recipe | v11-B (ConvNeXt-tiny `fb_in22k_ft_in1k`, 320 px triplets, K_train 4, K_infer 16, 15 epochs, LR 1e-4 / 3e-4, gated per-finding attention) |
| Target | `0.5 * 4-source soft + 0.5 * v11 OOF` (gold excluded) |
| Where trained | fold 0 on Kaggle (v13 version 2, 6.29 h); folds 1-4 locally on the RTX 3080 Ti (D-016, `scripts/local_v13.py`, 6 loader workers, 2.2-2.6 h per fold) |
| Checkpoints | `models/v13/v13/fold<k>_N/v13_fold_<k>_N_best.pt`; Kaggle dataset `lingxd/rsna-knee-v13-weights` version 2 |

| Fold | Val macro AUC (v11) | Gold-58 (v11) | Best epoch |
|---|---:|---:|---:|
| 0 | 0.899 (0.898) | 0.920 (0.911) | 9 |
| 1 | 0.872 (0.873) | 0.917 (0.910) | 11 |
| 2 | 0.863 (0.862) | 0.915 (0.911) | 12 |
| 3 | 0.868 (0.868) | 0.918 (0.911) | 14 |
| 4 | 0.871 (0.870) | 0.916 (0.911) | 13 |
| 5-fold | pooled OOF 0.873 (0.875) | rank ensemble 0.920 (0.913; +0.007, CI +0.002 to +0.013) | - |

Public LB: fold 0 alone 0.934 (v14), 5 folds 0.936 (v13_submit). Arm M (MRI-CORE ViT-B/16) reached
gold 0.881 at fold 0 and was dropped (Gate F0).

## Lessons (evidence-backed)

1. **The public stack is a high floor.** v05 = 0.943 with zero training; any added model must
   be strong on its own to help.
2. **A 0.909 model blended at 0.45 lowers a 0.943 anchor by 0.011** (v09 vs v10). A weak leg
   is not "free diversity"; blend weight must reflect relative strength.
3. **Local metrics map to the public LB roughly as gold 0.897 -> LB 0.909.** A forum report
   puts a 0.950-LB single model at about 0.930 on the same gold set, so the gold-58 gap
   (about 0.03) was a usable early warning that we did not act on. The mapping is model-
   dependent: another participant reports gold about 0.89 -> LB 0.940 (EffNet/ResNet) and gold
   0.915 -> LB 0.926 (CoAtNet) (2026-10-05 note), so treat it as one data point.
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
9. **OOF-teacher targets alone did not move gold** (v11 A 0.895 vs v08 fold 0 0.896, paired CI
   -0.010 to +0.009) although fold-0 validation rose +0.013. That validation gain matches the
   teacher leakage of design 3.2: for teacher experiments, trust gold, not fold validation.
10. **v08-style training was under-optimised; more optimisation is the measured lever.** v11 B
   (15 epochs, 2x LR) beats A by +0.016 on gold (CI +0.006 to +0.026). A's training-subset and
   validation excess loss stay close; B opens a gap and its validation AUC is flat after epoch
   9 of 15, so more epochs at this recipe will not help. B changes epochs and LR together and
   uses teacher targets, so the gain is not attributed to one factor.
11. **Compare excess loss, not raw loss, across sets with different prevalence**: fold-0
   validation loss is below training loss only because its targets have lower entropy.
12. **The timing model holds:** estimated 4.8 / 7.6 h vs measured 5.13 / 7.49 h (v11 fold 0).
13. **The v11 B gain is consistent across folds** (every fold 0.910-0.911 on gold vs v08's
   0.883-0.896); the 5-fold ensemble adds little because the folds agree (Spearman 0.97).
14. **Large notebook outputs used as inputs can become unmountable on Kaggle** (v11 versions 3-4:
   `ERRORED_MOUNTING_DATASET`, empty log, no GPU charged; the exact message is only on the version's
   log page in the browser). Rerunning the source notebook with its pinned image reproduced the
   cache byte-for-byte and fixed it. Keep manifests of large outputs locally so a rerun can be
   verified.
15. **A better own leg is still not enough for the anchor.** v12 (v11 leg alone) scores 0.931,
   +0.022 over v10 (gold +0.016; gold -> LB offset +0.018 vs +0.012 for v08). A binormal blend
   model calibrated on v09 (anchor 0.943, leg 0.909, w 0.45 -> 0.932) implies a noise correlation
   of 0.94 between our leg and the anchor; under it a 0.931 leg blends to 0.940-0.943 at weights up to 0.45,
   the break-even standalone score is 0.935 (w 0.30) / 0.937 (w 0.45), and reaching 0.944 needs
   about 0.939. The pre-registered 0.935 gate matches the break-even. These figures are a
   sensitivity analysis under one fitted parameter, not measured requirements (Codex, design v13).
16. **The anchor's public members are not stronger than v11 on gold** (`anchor-components-2026-10-06.md`):
   DINOv2 and RadImageNet members score 0.840 / 0.854 (OOF) vs v11's 0.913; the CoAtNet members are
   gold-selected (0.912-0.931). Hypothesis, no member ablation: the anchor's strength comes from
   combining families. A gold proxy of the anchor matches v09 (v08 at w 0.45: -0.010 vs -0.011 on
   LB) but its verdict on v11 depends on the proxy weights (-0.001 / +0.003 / -0.001 at w 0.30 for
   three frozen variants): a diagnostic, not a gate.
17. **The round-2 teacher transfers to the public LB.** One fold-0 N model scores 0.934 (v14), above
   v12's 5-fold v11 leg (0.931); on gold N fold 0 is 0.920 vs v11 5-fold 0.913 (gold -> LB offset
   +0.014 vs +0.018 for v12), so a better target did give a better student this time (contrast L9).
   Limits: the margin over the 0.933 threshold is 0.001; the LB gain of fold ensembling is unmeasured
   (on gold it was +0.002 for v11, L13); under L15 a 5-fold N leg near 0.936 would only break even
   in the blend, and 0.944 needs about 0.939.
18. **Fold ensembling shows on the LB, not on gold; the N leg blends a little better than v08 did.**
   v13 N: fold 0 alone 0.934 (v14), 5 folds 0.936 (v13_submit), while gold stayed 0.920 (fold
   Spearman 0.978): gold-58 cannot resolve gains of +0.002. Blends with the v05 anchor: w 0.30
   0.944 (v15), w 0.45 0.943 (v16). Recalibrated binormal model: noise correlation 0.913-0.947
   (median 0.929) vs 0.924-0.963 implied by v09, blend gain at w 0.30 about +0.0007. To reach 0.946
   on top of a 0.943 anchor a leg needs about 0.941-0.945 alone (0.943 at the median).
19. **Local GPU training on Windows is bounded by the commit limit, not GPU memory** (v13 fold 2,
   2026-10-07): each spawned loader worker commits about 2.4 GB (torch/CUDA DLLs) and the trainer
   about 11.8 GB (GPU allocations are charged to host commit under WDDM). 8 workers hit the 47 GB
   limit; 6 workers run at 170 img/s (2.5 h per fold, vs about 6.5 h on a Kaggle T4 pair). A
   blocked trainer needs a log-stall watchdog. Locally trained folds reproduce on Kaggle to 5.5e-5.
20. **The public frontier moved to one OAI-trained model.** All twelve public notebooks at
   0.949-0.950 (2026-10-08) load the same CoAtNet-384 checkpoint; its author reports 0.942 without
   OAI and +0.005 from 2,399 OAI knees. Without OAI the public frontier equals our 0.944 (v15).
   Gold-to-LB offsets differ by model (CoAtNet +0.026, N +0.016, reader +0.014), so gold-58 does not
   rank models of different families (`public-landscape-2026-10-08.md`, v18).
21. **Our leg is about as different from the CoAtNet as the public reader** (gold noise correlation
   N-CoAtNet 0.809, reader-CoAtNet 0.786, N-v17 0.827; LB-consistent reader-CoAtNet 0.80-0.88). Added
   to v17 at w 0.15 it ties at 0.950 (v19); at w 0.25 it drops to 0.949 (v20). Under the scenario model
   that means an N-v17 correlation of about 0.90-0.93 on the LB scale, so the leg adds about nothing to
   this base; the gold correlations (0.81-0.83) understated it. The single-number binormal model cannot
   identify the correlation of a per-finding fusion (Codex, v19 design).
22. **Kaggle ranks on unrounded scores** (display 3 decimals): on 2026-10-08 we ranked 72nd of 379
   teams at 0.950, ahead of 282 earlier submitters. A change in our rank after a new submission shows
   whether it beats our best in the hidden digits.

23. **A fifth label source does not change the student when the teacher half is fixed** (v22, E1): the
   Gemini table raised the round-2 target on gold by +0.0036 as a label, but the N fold-0 student trained
   on it equals v13's (val 0.8990 vs 0.8988, gold -0.002, per-finding Spearman 0.98). With half of the
   target being the v11 OOF teacher, one more report source moves the target too little to change what
   the model learns. Contrast L17, where changing the teacher did change the student. No public report
   table beats our 4-source mean on gold (`external-levers-2026-10-09.md` 2.1).

24. **Our target does not improve the OAI CoAtNet** (v23, E5): three epochs on the round-2 target with a
   0.5 self-distillation term moved gold from 0.9255 to 0.9230 (CI -0.0088 to +0.0035), losing most on
   MCL, Lateral Meniscus and PF OA, the findings where our own models are weak. Our v07 cache feeds the
   public checkpoint almost exactly (adapter: Spearman 0.984 with the exact pipeline, gold 0.9255 vs
   0.9228), so that pipeline route is open for inference; our labels are not better than the ones it was
   trained on.

25. **Local training limits changed and CoAtNet needs care** (v24 smoke, design v21-shortlist 12): the
   Windows commit limit is now 36.5 GB (4.8 GB page file; 47.3 GB in L19) with about 13 GB used at idle,
   so worker counts that fit before now stall the machine (two GPU timeout resets logged). With frozen
   BatchNorm the ImageNet CoAtNet diverges in fp16 after about 27 steps (pretrained running variances down
   to 2e-6); BatchNorm in train mode is stable. Large fp32 evaluations oversubscribe the 12 GB GPU and
   crawl instead of failing. A silent stall is caught only by the log watchdog.

26. **Our N does not help the OAI CoAtNet in any configuration tried**: outside the fusion at w 0.15 a
   tie (v19 0.950), at w 0.25 0.949 (v20), and in place of the public reader with its per-finding weights
   0.949 (v21), although N alone beats the reader (0.936 vs 0.929) and gold predicted +0.0013 for the swap.
   Standalone strength and gold-58 do not predict a partner's value for this base (L20, L21).

## Open hypotheses for why v08 is weak (untested)

Each needs evidence before it drives `IMPROVEMENT_PLAN.md`:

- Too few training tokens per study (K_train 4 x 5 slots = 20) and only 10 epochs; and low
  backbone LR (5e-5): **partly tested** by v11 B (15 epochs, 2x LR: gold +0.016 over A), see
  lessons 10. K_train 8 did not help in v08 (lesson 6).
- Soft targets include the weakest table (lixin, 0.835 on gold); untested single-source runs.
- 140 mm / 320 px geometry versus forum reports of 224-288 px working well; resolution was
  not ablated after design revision 3.
- Attention pooling over all slots versus simpler per-slot pooling; not ablated.

## Next steps

1. **v20** (v17 + N at w 0.25) scored **0.949** (ref 56979496), below v19/v17 (0.950): rejected per the
   decision rule; v19 stays the anchor-family pick (v17 and v19 are a coin flip in the hidden digits).
2. **Leaderboard 2026-10-09 01:52 UTC:** rank 268 of 5,543; 185 teams above 0.950; the 0.950 block spans
   ranks 186-591; silver cut rank 277 and bronze cut rank 554 are both inside it. Our rank is sliding as
   more teams pass 0.950, so a 0.950 entry is unlikely to hold silver, and possibly bronze, by 2026-10-22.
3. **Next direction (needs a design note and Codex review, D-004):** blending our 0.936 leg into the
   0.950 base is at a tie (L21); the remaining lever is a stronger own model. Candidates to compare in
   a design note: train our OOF-teacher target on a CoAtNet / 384 px recipe, or fine-tune the public
   CoAtNet-384 checkpoint with our targets (D-019 already accepts OAI-derived weights), using the
   local RTX 3080 Ti (D-016, about 2.5 h per ConvNeXt fold; CoAtNet-384 will be slower). Gold-58 cannot
   rank families (L20), so plan LB checks. **2026-10-09:** options for external resources by pipeline stage
   (with Codex) in `docs/research/external-levers-2026-10-09.md`: no public report-label table beats our
   4-source mean on gold, but the CC0 Gemini table adds +0.0035 to the round-2 target (CI -0.0007 to
   +0.0079); a synthetic benchmark puts a local CoAtNet fold at about 6 h. **Shortlist running (D-020,
   `v21-shortlist-design.md`):** E6 v21 scored 0.949 (rejected, L26); E1 v22 no gain (L23; no LB check);
   E5 v23 not admitted (L24); E4 v24 fold 0 done locally (val 0.8943, gold 0.9166, close to N), fold-0
   leg `v24_submit` commit run pushed 2026-10-10 (LB gate 0.937 for folds 1-4, start by 10-14 12:00 UTC);
   E7 optional. Leaderboard 2026-10-10 05:13 UTC: rank 497 of 5,641; silver now needs 0.951 and the
   bronze cut (rank 564) is still at 0.950 but the block above us grows by about 150 teams a day.
4. **Team merger** (deadline 2026-10-15): the user's decision; not discussed yet.
5. Final selection until something beats it: **v19 (0.950) + v15 (0.944, non-OAI hedge)**. The OAI
   ruling (topic 743416) could still change the picture; check it before 2026-10-22.

## Open questions

- Is the OAI-trained CoAtNet allowed? No host answer (topic 743416); D-019 accepted the risk.
- Hidden-test DICOM transfer syntaxes are unknown (all training and placeholder test files are
  uncompressed); the v17 image has PIL 12.3 with JPEG 2000 but no pylibjpeg/gdcm, and the reader's
  pylibjpeg-libjpeg wheel does not install there.
- Whether bf16 autocast in the old stack's A5 stage costs AUC on T4 (v05/v15 only).

## Environment

- Local analysis: conda env `kaggle` (Python 3.11, CPU torch) on PATH; recipe `environment.yml`.
- Local GPU training (D-016): RTX 3080 Ti 12 GB, i7-12700K, 32 GB RAM; conda env `kaggle-gpu`
  (`E:\Anaconda\envs\kaggle-gpu`, Python 3.13, torch 2.11.0+cu128, timm 1.0.29; recipe
  `environment-gpu.yml`; conda needs `E:\Anaconda\Library\bin` on PATH). Runner `scripts/local_v13.py`;
  6 loader workers at most (L19). The v07 cache is at `results/v07/full3/`.
- Kaggle access: `KAGGLE_API_TOKEN` user environment variable (never print it); Kaggle CLI plus the
  `nvidia-kaggle` and `kaggle@shepsci` Claude Code plugins. The built-in browser is not signed in to
  Kaggle (the public `ListKernels` API works without sign-in).
- GPU quota: `kaggle quota`; 30 h windows reset on Saturdays at 00:00 UTC; scoring reruns do not
  count. 1.80 h left on 2026-10-08 until the 2026-10-10 reset.
- Submissions: 5 per day, reset at 00:00 UTC.
