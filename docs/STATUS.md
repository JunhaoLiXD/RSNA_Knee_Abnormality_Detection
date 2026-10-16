# Project Status

> Agents: read this file first at the start of every session, and **before changing
> `IMPROVEMENT_PLAN.md` or any strategy** (D-011, D-012): cite the versions and lessons below
> that support or contradict each new direction. Update it before ending a session that
> changed project state and whenever a version gets a new result. Raw run rows live in
> `experiments.md`; decisions in `decisions.md`.

Last updated: 2026-10-15 ~14:20 UTC (v55 0.956 not above v54, rank 392, silver cut 0.957; v61 submitted; handover doc; v57 not above v54; v55 scoring; rank 293; v56 0.956, not 0.957; v54 still best; v54 rank 273, inside silver; public 0.957 recipe reproduced as v56; v57 queued; v53 incumbent, rank 323; v54 scoring; v49 0.955 rejected; v53 flip+R224 next; D-033 probes: v48 scoring, v49/v50 ready; v44 0.955 rejected, ROI line closed; v44 submitted; v47 0.956 above v46: rank 332, 191 witnesses; v45 0.954 above v40 by 6 witnesses: incumbent; Dense-P 0.934 ends the dense line; v42 full cache complete; rank 636 after 310 teams copied the public R7 0.956; v46 0.956 rank 522; v47 submitted 16:04 UTC)

## Current phase

**Phase 5 - OAI-based public anchor plus our leg** (2026-10-08). Phase 4 (v13 round-2 teacher)
finished: our 5-fold arm-N leg scores 0.936 alone (v13_submit) and 0.944 blended into the old v05
stack (v15). All public notebooks at 0.949-0.950 share one CoAtNet-384 checkpoint trained with OAI
data; the user adopted it despite the unresolved rule risk (D-019). v17 (public 0.950 notebook
unchanged) reproduced **0.950**; v19 (v17 + our leg at w 0.15) also **0.950** (tie at 3 decimals;
ranking uses unrounded scores). v20 (w 0.25) scored 0.949 (rejected).
Our leg adds about nothing to this base (L21). Leaderboard 2026-10-09 01:52 UTC: **rank 268 of 5,543**, inside silver (cut rank 277)
but the 0.950 block spans ranks 186-591 and is growing. Final selection then: v19 + v15; **now provisionally v27 + v15**
(D-022). Deadline 2026-10-22; entry and team-merger deadline 2026-10-15.

**2026-10-10:** the external-levers shortlist (D-020) gave no gain (v21 0.949; v22 and v23 no gain; v24
fold 0 0.934 = N fold 0; L23-L27). After the verified 0.954 template (public CoAtNet + an anatomy-anchored local-view
model), the local-views plan runs (D-021): I1 `v25_submit`, B1 `v26`/`v27_submit`, B2 `v28`-`v30_submit`.

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
| v24 | 2026-10-09 | training (E4, D-020) | own CoAtNet-rmlp-2 (ImageNet-12k, no OAI), round-2 target, local fold 0 | fold 0: val 0.8943 (N F0 0.8988), gold 0.9166 (N F0 0.9200); Spearman with N 0.95 (gold) / 0.94 (val); N+C rank mean gold 0.9213 | 0.934 | v24_submit (fold-0 leg alone, ref 57045065) = N fold 0 (v14 0.934): below the 0.937 gate, **E4 stopped** (folds 1-4 not trained; L27) |
| v25 | 2026-10-10 | submit (I1, D-021) | v17 cells unchanged + the same public CoAtNet through a second input path (v19 leg preprocessing + v23 adapter), combined CoAtNet = rank mean of exact and adapter, then v17's reader fusion; gated (else v17's output) | gold: I1 0.9269 vs v17 0.9245 (+0.0024, CI -0.0014 to +0.0064); local port (310 studies), parity (fp16 7e-5) and fusion tests pass | 0.949 | **rejected** (below v19/v17 0.950; gold had predicted +0.0024; L28). Commit run: all gates pass (exact = v17 byte for byte, reference byte-equal, T4/RTX parity max 2.0e-4, coverage 1.0, recomputed locally); submitted 2026-10-10 16:11 UTC (ref 57047189); adoption over v19 at >= 0.952 |
| v26 | 2026-10-10 | training (B1, D-021) | N recipe + a second view per slot (central 100 mm crop of the v07 140 mm field, own slot ids), report-only target (v06 4-source soft), local fold 0 | fold 0: val 0.8921 (N F0 0.8988), gold 0.9091 (N F0 0.9200); Spearman on gold with the CoAtNet 0.864 (N 0.899), with N 0.941; gold screen v17 + v26 at 0.15: +0.0029 (CI +0.0001 to +0.0063) | - | weaker alone, less redundant; `v27_submit` (v17 + v26 F0 at 0.15) next |
| v27 | 2026-10-10 | submit (B1, D-021) | v17 anchor (cells unchanged) + v26 arm-L fold-0 leg at w 0.15 (v19 leg code with the v26 two-view dataset and model, built from the checkpoint cfg, strict load) | local GPU leg test: reference study vs v26 OOF max diff 1.4e-4; commit run: all gates pass (base = v17 byte for byte, reference byte-equal, OOF 7.8e-5 on T4, coverage 1.0, blend recomputed) | **0.950** | displayed tie with v19, but **above v19 in the hidden digits**: team rank 616 -> 458 (158 teams that did not submit moved below us, none passed us; L29); our best public submission now; paired gold vs v19 +0.0010 (CI -0.0021 to +0.0040). **Provisional pick with v15 (D-022)**; B1 expansion to three folds (`v31_submit`) |
| v30 | 2026-10-11 | submit (B2, D-021/D-022) | v17 anchor (cells unchanged) + v29 fold-0 leg at w 0.15; the leg renders each study twice from DICOM (v07 code at 140 and 100 mm) with reference checks of both renderings | local flow test (cache-backed rendering, real fingerprints): reference 6/6 byte-equal, OOF 2.6e-5, 3/3 predicted | **0.951** | first displayed step above 0.950; rank 405 of 5,710 (03:35 UTC); gold had predicted -0.0013 vs v27 (L30). Best public submission until v32 scores. B2 qualifies for three total folds by the D-022 table (displayed 0.951) |
| v32 | 2026-10-11 | public anchor (D-023) | heliosli/rsna-knee-blend-gold-dataset-restored unchanged: CoAtNet-384 (as v17) 0.7 + heliosli S6 (ConvNeXt-small, knee-anchored views via SKM-TEA `anatomy.pt`) 0.3; public 0.954 | commit run: S6 and final submission equal the author's (diff 0.0), CoAtNet ranks byte-equal; CoAtNet raw probabilities differ by up to 5.3e-5 (gate tolerance 1e-6 failed; ranks identical) | **0.954** | reproduces the public 0.954; our best public submission (D-024: v34 then v33). Rerun (version 2): our two runs differ by 5.8e-5 in raw probabilities, outputs byte-equal: run-to-run variation; submitted 2026-10-11 02:32 UTC (ref 57059710) before v30 was scored (user decision), so v30 is judged by display only |
| v33 | 2026-10-11 | submit (D-024) | v32 + combined v26/v29 fold-0 leg at w 0.15 (leg after S6) | commit run: all gates pass, branch probabilities identical to v27/v30 legs; v34 projection about 5.3 h hidden runtime | **0.954** | above v32 in the hidden digits (rank 239 -> 201, 52 stable witnesses, none reverse; persistence confirmed 12:31 UTC): **best public submission, provisional pick with v15**; v35 eligible under D-024 after v29 folds 1-2 |
| v35 | 2026-10-11 | submit (D-024) | v32 + six-model leg (v26 + v29 folds 0-2, hierarchical rank aggregation) at w 0.15; launch allowance 115 min (v34 v4) | commit run: 11 gates pass | 0.953 | **rejected** (below v33's 0.954; gold had described +0.0008, L31) |
| v37 | 2026-10-11 | public anchor (D-028) | heliosli blend-mine-in version 2 reproduced: old S6 bundle, CoAtNet:S6 0.5:0.5, new S6 execution path; S6 files from compact-v1 (the author's slug is non-versioned) | commit runs: outputs byte-equal to the author's | 0.954 | the 0.956 was the author's version 1 with an unavailable R6 S6 (L32); **above v33 in the hidden digits** (50 witnesses, persistence confirmed): **best public submission, provisional pick with v15** |
| v38 | 2026-10-11 | submit candidate (D-028) | v37 + v35's six-model leg at w 0.15 | commit run: 12 gates pass | - | not submitted; prior lowered by v35 (L31) |
| v39 | 2026-10-12 | submit (D-029) | v37 + v33's fold-0 leg at w 0.15 (replaces v38) | commit run: 11 gates pass | 0.954 | no demonstrated improvement over v37 (0 witnesses); the leg line stops |
| v40 | 2026-10-12 | submit (D-030 R1) | v37 cells unchanged + public goodpjw2008 2.5D ConvNeXt reader (3 folds) at a uniform outer rank weight 0.10; any reader failure keeps v37 | commit run: 11 gates pass (reader output equal to v17's reader run, 0.0) | 0.954 | **above v37 in the hidden digits: rank 524 -> 235, 211 stable witnesses, none reversed; persistence confirmed 10-13 01:40 UTC (146 still below, none reversed)**: the incumbent |
| v41 | 2026-10-12 | submit (D-030 A1) | original v37 with CoAtNet:S6 0.4:0.6 for all 12 findings | commit run: 8 gates pass | 0.953 | **rejected** (below v40) |
| v45 | 2026-10-13 | submit (D-031 probe 1) | v40 with the reader at 0.15 | commit run: 11 gates pass | 0.954 | **above v40 in the hidden digits, small margin** (6 stable witnesses, none reversed; `2026-10-13a` -> `13b`): the old-S6 incumbent and the second pick candidate |
| v46 | 2026-10-13 | public anchor (D-032) | heliosli R7 one-click notebook (public 0.956) reproduced: v37 with the R7 ConvNeXt-small bundle `8c7b666e27dc0e8f` (fluid/state stackers, fastMRI auxiliary training per the author) | commit run: R7 output and submission byte-equal to the author's | **0.956** | **reproduces the public 0.956: rank 642 -> 522 of 5,926, 144 stable witnesses, none reversed (`2026-10-13c` -> `13d`)**; lower part of the 0.956 block (ranks 144-662; bronze cut rank 592 and silver cut rank 296 both at 0.956): **best public submission** |
| v61 | 2026-10-15 | submit (D-033) | v54 + nartaa's all-data S6 (S6F0) at 0.35 of the ConvNeXt slot | commit run: other stages byte-equal to v54; S6F used | pending | submitted 14:16 UTC |
| v55 | 2026-10-15 | submit (D-033) | v54 + heliosli's old S6 at 0.35 of the ConvNeXt slot | commit run: S6 used | 0.956 | not above v54 (0 witnesses); rejected |
| v47 | 2026-10-13 | submit (D-032) | v46 + goodpjw2008 reader at outer weight 0.10 | commit run: 11 gates pass | **0.956** | **above v46 in the hidden digits: rank 522 -> 332 of 5,938, 191 stable witnesses (all 0.956), none reversed** (`2026-10-13d` -> `13e`); 36 places below the silver cut (rank 296): **best public submission, first-pick candidate and v44's host** |
| v44 | 2026-10-13 | submit (D-031) | v47 (host, unchanged) + v43 LM/MM experts by the order-only per-column blend (w 0.5, row fallback); test crops through the same S6 path as v42 | commit runs 1-2: all gates pass; 7 training studies re-cut inside v44 pixel-identical to the v42 cache; Codex code review: no blocker, 2 fixes accepted (design section 13) | 0.955 | **rejected**: one display step below v47; the experts lowered the two meniscus columns (a fallback would have scored v47's 0.956); ROI line ends (D-031, L38) |
| v43 | 2026-10-13 | ROI experts, local (D-031) | LM and MM single-finding experts on the v42 crops (convnext_nano, P target), fold 0 | val (usable, leaky) LM 0.872 / MM 0.899 vs N 0.887 / 0.919; order-only blend into N OOF: LM +0.0046 (CI -0.007 to +0.016), MM +0.0012 (CI -0.005 to +0.007); gold blend -0.002 for both | - | weak positive signal for LM, none shown for MM; v44 next on the then-incumbent |
| v42 | 2026-10-12/13 | ROI cache (D-031) | meniscus ROI crops for per-finding experts, all 4,407 training studies | 0 errors; both compartments usable 84.4%; 3.14 GB in 24 shards | - | done (`results/v42/full2`); v43 trained on it |
| v36 | 2026-10-11/12 | training + LB test (D-027) | fold-0 diagnostics: C control, W unit weights (Kaggle), G 224 px + K8, P round-3 target | local val vs C: G -0.0005, P +0.0025 (leaky); gold C 0.918, G 0.911, P 0.920 | P 0.937, W 0.936 | P and W pass 0.936 (v14 0.934), both below 0.940: no expansion; X by D-030 unless amended (Codex: cancel X, keep a v15-hedge option only at W >= 0.940); **arm D (Dense-P) 0.934 alone (2026-10-13): below P and W, the dense line ends (D-031)** |
| v28 | 2026-10-10 | cache (B2, D-021) | v07 cache notebook with a 100 mm field at 320 px (JPEG quality 92 from a 120-study pilot) | 4,407 studies, 0 errors, 14.44 GB, 0.88 h CPU; audit: index facts and slice arrays equal v07, v28 vs central v07 crop correlation median 0.979 (min 0.82), no systematic clipping | - | done (downloaded to `results/v28/full1`) |
| v29 | 2026-10-10 | training (B2, D-021) | v26 with the local view read from the v28 cache (v07/v28 alignment checked) | fold 0: val 0.8875 (v26 0.8921), gold 0.9028 (v26 0.9091); Spearman with v26 0.968; paired gold v17 + v29 vs v27 -0.0013 (CI -0.0037 to +0.0009) | - | weaker than v26 and nearly the same model; `v30_submit` decides by the D-022 table |
| ref | 2026-10-01 | public notebook | pjmathematician d4-blend (private datasets, not reproducible) | - | 0.946 | reference |
| ref | 2026-10-01 | leaderboard | #1 0.961; #10 0.957; #100 0.949; 1,001 teams >= 0.943 | - | - | reference |
| ref | 2026-10-05 | public notebooks | no public notebook above 0.946; reproducible ceiling still 0.943 (`docs/research/public-landscape-2026-10-05.md`) | - | - | reference |
| ref | 2026-10-05 | leaderboard | 5,184 teams; #1 0.963; #10 0.959; #100 0.951; silver line 0.945; >= 0.944 is inside bronze; 0.943 block ranks 370-1,375; we are #1,278 | - | - | reference |
| ref | 2026-10-08 | public notebooks | twelve at 0.949-0.950, all on the OAI-trained CoAtNet-384 SWA (nartaa); 0.950 = + goodpjw2008 ConvNeXt reader (`public-landscape-2026-10-08.md`) | - | 0.950 | reference |
| ref | 2026-10-08 | leaderboard | 5,537 teams (~23:00 UTC); #1 0.964; 0.950 block ranks 176-554; silver cut rank 276 and bronze cut rank 553 both at 0.950; we are #247 | - | - | reference |
| ref | 2026-10-10 | public notebooks | best verified 0.954 (heliosli: CoAtNet 0.7 + anatomy-anchored compact ConvNeXt-small "S6" using the SKM-TEA segmenter, 0.3); 0.951 forks with an older S6 bundle; S6 files retired 2026-10-09 13:50 UTC, notebooks no longer runnable (`public-landscape-2026-10-10.md`) | - | 0.954 | reference |
| ref | 2026-10-10 | leaderboard | 5,641 teams (05:13 UTC); #1 0.964; 331 teams above 0.950; 0.950 block ranks 332-837; **silver cut rank 282 at 0.951**; bronze cut rank 564 at 0.950; we are #497 | - | - | reference |
| ref | 2026-10-10 | leaderboard | 5,691 teams (18:10 UTC); #1 0.964; #100 0.955; 361 teams >= 0.951; 0.950 block ranks 362-971; silver cut rank 284 at 0.951; **bronze cut rank 569 at 0.950, we are #616** (outside bronze at the same displayed score) | - | - | reference |
| ref | 2026-10-10 | leaderboard | 5,706 teams (22:04 UTC); 380 teams >= 0.951; 0.950 block ranks 381-1004; silver cut rank 285 at 0.951; bronze cut rank 570 at 0.950; **we are #458** (v27), inside bronze | - | - | reference |
| ref | 2026-10-11 | leaderboard | 5,710 teams (03:35 UTC); 199 teams >= 0.954, 288 >= 0.952, 440 >= 0.951; **silver cut rank 285 at 0.952**; bronze cut rank 571 at 0.950; we are #405 (v30, 0.951) | - | - | reference |
| ref | 2026-10-11 | leaderboard | 5,733 teams (11:45 UTC); **silver cut rank 286 at 0.954**; gold cut (rank 21) 0.961; we are #201 (v33, 0.954) | - | - | reference |

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

27. **Our own CoAtNet without OAI data is only as good as N** (v24, E4): CoAtNet-rmlp-2 (ImageNet-12k) in
   our trainer on the round-2 target scores 0.934 on fold 0 alone, the same as N fold 0 (v14 0.934); locally
   val 0.8943 vs 0.8988, gold 0.9166 vs 0.9200, per-finding Spearman with N 0.95. The public CoAtNet's 0.949
   therefore does not come from the architecture; what remains (OAI training data, all-data SWA, 384 px,
   96-slice volumes with 94 windows) is not separated. With L23-L26: changing only the backbone or only the
   target leaves our model redundant with N, so the next legs change the views and the supervision (D-021).

28. **A second input path for the same CoAtNet does not help, and gold over-predicted it** (v25, I1): the
   rank mean of the exact pipeline and our v07 adapter path, then v17's reader fusion, scored 0.949 against
   v17/v19's 0.950, although gold-58 predicted +0.0024 (CI -0.0014 to +0.0064). With v21 (gold +0.0013,
   LB 0.949) this is the second gold-positive change to the CoAtNet side of v17 that lost on the LB.
   Every change to the v17 fusion tried so far (v20, v21, v25) scored 0.949; gold gains of this size are
   not evidence (L20). Displayed scores have 3 decimals, so the true loss may be small.

29. **v27 is above v19 in the hidden digits; the cause is not established** (v27, B1): v17 + the v26 fold-0
   two-view report-only leg at w 0.15 displays 0.950 like v19, but our rank went 616 -> 458 while 158 stable
   teams (count, time, score and membership unchanged) crossed below us and none above, so its unrounded
   public score is higher (L22), by less than 0.001. Paired gold vs v19 +0.0010 (CI -0.0021 to +0.0040). The
   leg is weaker alone than N (gold 0.9091 vs 0.9200) and less correlated with the CoAtNet (0.864 vs 0.899),
   but the data show a higher public score for this configuration, not that lower correlation caused it.
   First LB-positive change since v17, from one fold, within public-LB noise; selection among related variants
   of one base inflates such wins (D-022 caps what they fund).

30. **The native 100 mm view beat the crop on the LB although both local screens said the opposite** (v30 vs
   v27): v17 + the v29 fold-0 leg (local view rendered from DICOM at 100 mm) displays 0.951, v17 + the v26 leg
   (central crop of the 140 mm field) 0.950, while gold (v30 vs v27 -0.0013, CI -0.0037 to +0.0009) and
   validation AUC (v29 0.8875 vs v26 0.8921) favoured v26. One fold each, one display step, public-LB noise;
   with L20 and L28 this is the third case where gold ranked two legs the wrong way round on the LB.

31. **More folds made our leg worse on the LB; gold said the opposite** (v35 vs v33): the leg with three folds per branch on
   the v32 anchor displayed 0.953, v33's fold-0 leg 0.954 (and above v32 in the hidden digits), while gold-58 described the
   six-model blend +0.0008 over the v33 type (0.9321 vs 0.9313). Fourth gold misranking (L20, L28, L30). Contrast L18, where N's
   five folds raised the leg alone by 0.002: in a 0.15 leg, fold averaging may remove the specific disagreements that helped.
   One display step, public-LB noise; the cause is not established.

32. **A Code-page score may belong to an older notebook version** (v37): "Best Score 0.956 V1" was version 1 with a different,
   now unavailable S6 (R6, fastMRI+ aux); the pulled latest version reverts to the old S6 and scores 0.954 for us. Check the
   version of a public score before reproducing. The old S6 at 0.5:0.5 is above v33 in the hidden digits (rank crossing).

33. **A small public third component gave the largest hidden-digit gain so far** (v40 vs v37): the goodpjw2008 reader (0.929
   alone) at a uniform outer weight 0.10 on CoAtNet + S6 moved us from rank 524 to 235 (211 stable witnesses, none reversed),
   while our own legs on the same family of anchors gave 50 (v33 over v32), 0 (v39) or a loss (v35). The reader is a different
   public model family that already helped the CoAtNet alone (v17 0.950 vs 0.949). Still one display step: no change in the
   displayed 0.954.
34. **The reader weight curve is flat near 0.10-0.15** (v45 vs v40): 0.15 moved us above v40 by only 6 stable witnesses
   (v40 over v37: 211). A further step to 0.20 is unlikely to be worth a submission; the reader's value is mostly captured.
35. **Denser training tokens with frozen early stages did not lift our own model** (Dense-P 0.934 vs P 0.937, W 0.936): with
   v13 0.936, v14 0.934 and v24 0.934, five variants of our single-model recipe sit within 0.934-0.937 on the LB. Our own
   training recipe is not the lever at this stage; the public anchors are.
36. **A public notebook at the next display step moves the cut lines within hours** (2026-10-13): after heliosli's R7 0.956
   one-click notebook, 310 teams rose to 0.956 in ten hours (the 0.956 block grew from 122 to 434 teams); bronze moved to
   0.955 and silver to 0.956, and we fell from rank 328 to 636 at an unchanged score. The new 0.956 notebooks (Jenil Langaliya,
   mercurydust RSNA-V3) are code-identical copies of it. Where a late copy lands inside the 0.956 block (ranks 130-563 at
   12:01 UTC) is not predictable: the block is not ordered by last-submission time, so the copies' hidden digits differ.
37. **The public reader's gain carried over to the stronger R7 host** (v47 vs v46): the same goodpjw2008 reader at a
   uniform outer weight 0.10 moved us above 191 stable teams at 0.956 (rank 522 -> 332), about as much as on the old S6 host
   (v40 over v37: 211). A third, different model family keeps adding hidden-digit gains on top of CoAtNet + S6/R7; the
   display stays at 0.956.

38. **Single-finding experts weaker than the host column lowered the score, even with an order-only blend** (v44 vs v47):
   the v43 LM/MM experts (val 0.872/0.899 vs our own N 0.887/0.919) blended at rank weight 0.5 into two columns of the
   0.956 stack dropped the display to 0.955. The fold-0 diagnostic against N (LM +0.0046, CI crossing zero) pointed the wrong
   way; the gold diagnostic (both columns slightly down) pointed the right way. A blend partner must be judged against the
   host it joins, not against a weaker stand-in; a new model needs to be at least as good as the host column, or a much
   smaller weight, unless it is a different family like the reader (L33, L37).

39. **A second public reader-like model hurt where the first helped** (v49 vs v47/v48): hengck23's MaViT-288 (0.935 alone)
   at outer 0.10 dropped the display to 0.955, while goodpjw2008's reader (0.929) at the same weight gained 211 and 191
   witnesses (L33, L37). "Different family at 0.10" is not a rule by itself; each addition needs its own test.

40. **The same-family R224 helped on the strong host, unlike the weaker experts** (v53 vs v48): nartaa's 224-px CoAtNet (0.945
   alone) at 0.35 of the Raptor slot (final weight 0.175) moved us above 187 stable teams. Unlike L38, it covers all 12
   findings, is only slightly weaker than the R384 it joins, and differs in input resolution and crop. L38 is about weak
   single-finding models at a large weight, not about every same-family addition.

41. **Matching a component's TTA to its sibling helped** (v54 vs v53): the anatomical mirror the CoAtNet-384 already used,
   applied to the 224-px CoAtNet as well, moved us above 44 stable teams; a public notebook claimed the same on the R7 + R224 host.

42. **A displayed public score can depend on inputs a copy cannot load** (v56): heliosli's "=0.9573" notebook, reproduced
   byte-equal on the placeholder studies with the same R7 bundle read from the versioned dataset (its own dataset is
   non-versioned and refused in submissions), scored 0.956. As in L32, check that a displayed score is reproducible before
   building on it or drawing conclusions from it.

43. **A second ConvNeXt of the same S6 lineage did not help on v54** (v55): heliosli's old S6 at 0.35 of the ConvNeXt slot
   (final weight 0.175) moved no stable team either way. Unlike R224 (L40), the old S6 is weaker than R7 and close to it;
   whether the all-data S6F0 (v61) differs is being tested.

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

0t. **Codex takeover verification, 2026-10-15 20:14 EDT (2026-10-16 00:14 UTC).** The handover's first two actions had
   already advanced in commits `245697b` and `a1c8074`; do not repeat the v61 submission. Kaggle confirms v55 ref
   `57214581` COMPLETE at 0.956. Re-running the requested `15b` -> `15c` comparison gives 4,959 stable teams, 0 positive
   crossings, 0 reverse crossings and 0 stable-order differences: v55 does not qualify for adoption. Preserve the existing
   `15c` snapshot (2026-10-15 14:15:56 UTC); overwriting it now would mix in v61's later result. v61 result audit follows.

**Handover state (2026-10-12 ~12:30 UTC).** Best public: **v37 0.954** (old S6 at CoAtNet:S6 0.5:0.5; above v33 by rank
crossing, 50 witnesses, confirmed). Provisional picks **v37 + v15**; v30 (0.951) operational non-S6 backup. Rank 506 of 5,819
(11:53 UTC), sliding inside the 0.954 block (687 teams; 196 at >= 0.955; silver cut rank 290 and bronze cut rank 581 both at
0.954). Submissions on 2026-10-12: 2 used (v39, v36 P), 3 left (reset 00:00 UTC). Team merger: not considered (user).

0s. **Update 2026-10-15 14:20 UTC.** **v55 (v54 + old S6 at 0.35) = 0.956, not above v54** (`15b` -> `15c`, 0 witnesses):
   rejected (L43). Other teams moved: we are **rank 392 of 6,042; the silver cut is now rank 302 at 0.957** (bronze 604 at
   0.956, gold 22 at 0.963), so silver now needs a displayed 0.957, not hidden-digit gains. v61 commit run checked (other
   stages byte-equal to v54, S6F used, reader used) and **submitted 14:16 UTC** (ref 57233540; before-snapshot `15d`); the
   nartaa dataset was accepted. Submissions on 10-15: 3 used, 2 left. v54 stays the best.
0r. **Update 2026-10-15 04:30 UTC: handover to Codex**, see `docs/HANDOVER-2026-10-15.md` (architecture, in-flight items,
   plan). v61 (v54 + nartaa's all-data S6 at 0.35) built, commit run started; v55 scoring. Tools in `scripts/d033/`.
0q. **Update 2026-10-15 03:30 UTC.** v57 (v56 + R224 mirror) = 0.956, not above v54: flip-TTA and the reader stay. **v55 (v54
   + old S6 at 0.35 of the ConvNeXt slot) submitted 03:25 UTC** (ref 57214581). Rank 293 of 6,015, silver cut 300: **7 places
   of margin**. Submissions on 10-15: 2 used, 3 left.
0p. **Update 2026-10-15 00:45 UTC.** **v56 (the public "0.9573" recipe, reproduced byte-equal with the versioned R7 bundle) =
   0.956** and not above v54 (0 witnesses): our v54 stays the best (rank 279 of 6,014; silver cut 300; 0.957 block ranks
   116-241, 126 teams; 908 teams at 0.956). The inference that flip-TTA or the reader hurt on that base is withdrawn (L42).
   **Plan change: the base is v54 again.** Public check 01:00 UTC: the only 0.957 notebooks are not reproducible (bliverrigpdoge:
   private input; heliosli: L42); goodpjw2008's new version (0.956) blends CoAtNet + R7 + old S6 + reader (a v55-like recipe).
   Automation: when v57 (v56 + R224 mirror) has scored, rank crossing; if it does not beat v54 (< 20 witnesses), **v55 = v54 +
   old S6** (commit run passed) is submitted automatically; otherwise stop and decide. v58/v59/v60 (built on v57) shelved.
0o. **Update 2026-10-14 22:40 UTC.** **v54 (v53 + mirror TTA on R224) = 0.956, above v53 by 44 witnesses: rank 323 -> 273 of
   6,010, inside silver** (cut rank 300 at 0.956; bronze 601). The mirror on R224 helps (L41); v57 applies it to the 0.957 base
   (auto-submit after 00:00 UTC). v56 (public 0.957 recipe) submitted 21:13 UTC, scoring.
0n. **Update 2026-10-14 21:10 UTC.** New public notebook heliosli "=0.9573 Latest public dataset score in one click!"
   (18:13 UTC, displays **0.957**): R7 (no flip-TTA) + R384 + R224 at 0.35 of the Raptor half, no reader: our v53's components
   without flip and reader, yet one display step higher (so flip and/or the reader do not add on top of R224; to be tested).
   **v56** = that notebook reproduced (outputs byte-equal to the author's run); its R7 dataset `rsna-knee-r6-frozen-fe055406` is
   **non-versioned and Kaggle refuses submissions with it** (as D-028), so v56 version 2 reads the same bundle from the versioned
   `compact-r7cnxfsss` (bundle id and file sha256 asserted). Auto-submit scripts: v56 v2 after its commit run equals the author's
   outputs (today's last submission); **v57** = v56 + mirror TTA on R224 after 00:00 UTC (user's instruction: do not wait for
   v56's score). Next probes on the 0.957 base, one at a time: + reader 0.10, + R7 flip-TTA, + old S6 (v55 logic). v54 still
   scoring (submitted 17:11 UTC).
0m. **Update 2026-10-14 17:15 UTC.** **v53 (v47 + flip-TTA + R224) = 0.956, above v48 by 187 witnesses: rank 567 -> 323 of
   5,990** (silver cut rank 299, 24 places above; bronze 599): **the incumbent** (L40). **v54 = v53 + mirror TTA on R224**
   submitted 17:11 UTC (ref 57189966; before-snapshot `2026-10-14f`). Submissions on 10-14: 4 used, 1 left.
0l. **Update 2026-10-14 11:40 UTC.** v48 (flip-TTA) 0.956, above v47 by 6 witnesses (our best now). **v49 (MaViT) 0.955:
   rejected** (L39). Rank 565 of 5,968 (bronze cut 596, silver 298, all 0.956): the public "One Free Flip, 68 Ranks Up"
   (varshithakolupuri, 10-14) and R224 notebooks are being copied. Codex review recorded in D-033 (v50 failure-path fix,
   combination rules). **v53 = v47 + flip-TTA + R224** (fixed) built, commit run started; to be submitted as "R224 on top of
   v48". v52 (B+C) is moot.
0k. **Update 2026-10-14 02:40 UTC (D-033 running; the agent has full control).** Probe A **v48 submitted 02:01 UTC** (ref
   57163377, R7 flip-TTA; before-snapshot `2026-10-14b`, rank 422). Probes B **v49** (MaViT, outer 0.10) and C **v50** (R224 in
   the Raptor slot) built and commit runs pass all gates (`results/v49/run1`, `results/v50/run1`); submitted one at a time after
   the previous is judged. Then the winners are combined.
0j. **Update 2026-10-14 02:30 UTC (silver push proposal, `docs/research/silver-push-2026-10-14.md`).** Claude's and
   Codex's independent proposals converge on three inference-only probes on v47, each judged alone by rank crossing: A = R7
   flip-TTA (label-safe, matches R7's training mirror, verified), B = hengck23 MaViT-288 at outer 0.10, C = R224 in the
   Raptor slot; then combine the winners. Runtime headroom: v47 scores within 3.4 h. Awaiting the user's go-ahead (D-033).
0i. **Update 2026-10-14 01:30 UTC.** **v44 = 0.955: rejected** (v47 0.956 stays the incumbent and first-pick candidate;
   rank 417 of 5,952 after other teams' gains; silver cut rank 297, bronze cut rank 595, both 0.956). The ROI line ends
   (D-031: no expansion). L38. Open: the v48 probe (incumbent v47 + R224, section 0h), awaiting the user's go-ahead.
0h. **Update 2026-10-13 20:30 UTC (public check, `docs/research/public-landscape-2026-10-13.md`).** No public notebook
   above 0.956; every R7-based 0.956 notebook is a code copy. The only new public component we can use: nartaa's 224-px
   CoAtNet (R224, in the dataset v47 already attaches; public recipe 0.35 of the Raptor slot; its author claims a rank gain
   inside the 0.956 block). jingshuifu's R7 flip-TTA is unscored. OAI host statement found (Open questions). A v48 probe
   (v47 + R224) needs a decision and a runtime guard; it would score after v44.
0g. **Update 2026-10-13 19:30 UTC.** **v47 = 0.956, above v46**: rank 522 -> **332 of 5,938**, 191 stable witnesses
   (all 0.956), none reversed (L37). Position 178 of 595 in the 0.956 block (ranks 155-749); silver cut rank 296 (36 places
   above), bronze cut rank 593. v47 is the incumbent, the first-pick candidate and **v44's host**; the second pick stays the
   old-S6 winner v45 (D-032 hedge). **Persistence confirmed** (`13d` -> `13f`: 185 witnesses still below, none reversed).
   **v44 submitted 19:59 UTC** (ref 57155006; v47 + v43 experts; commit runs pass all gates, Codex review without blocker;
   before-snapshot `2026-10-13f`, rank 346). Submissions on 10-13: 5 of 5 used. If v44 does not beat v47 by rank crossing,
   the ROI line ends (D-031: expansion only if v44 displays >= 0.956 and beats the incumbent).
0f. **Update 2026-10-13 16:10 UTC.** **v46 = 0.956** (public R7 reproduced): rank 642 -> **522 of 5,926**, 144 stable
   witnesses, none reversed; inside bronze (cut rank 592 at 0.956; silver cut rank 296 at 0.956; the 0.956 block spans
   ranks 144-662). **v47 submitted 16:04 UTC** (ref 57149295; R7 + reader 0.10; before-snapshot `2026-10-13d`); judged
   against v46 by rank crossing. Submissions on 10-13: 4 used, 1 left. v43 trained locally (LM, MM; diagnostics in the
   v42 design section 12: weak, uncertain signal for LM, none shown for MM); v44 is built on the v46/v47 winner.
0e. **Update 2026-10-13 12:30 UTC.** Scores: **v45 0.954, above v40 by 6 stable witnesses** (none reversed; `2026-10-13a` ->
   `2026-10-13b`): v45 is the old-S6 incumbent (L34); **Dense-P 0.934**: the dense line ends (L35). Rank 328 -> **636 of 5,909**
   at an unchanged 0.954: 310 teams rose to 0.956 after heliosli's public R7 notebook (L36); bronze cut rank 590 at 0.955,
   silver rank 295 at 0.956, 129 teams >= 0.957; top public notebook score still 0.956 (Jenil Langaliya and mercurydust
   0.956 notebooks are code copies of R7; varshithakolupuri's "one unused checkpoint" adds nartaa's 224-px 0.8-crop CoAtNet
   at 0.35 of the Raptor slot, not scored; **corrected 10-13 20:30**: the checkpoint is in the CoAtNet dataset we already
   attach, so that notebook does run it). **v46 submitted 12:09 UTC**
   (ref 57143117, D-032; before-snapshot `2026-10-13c`, rank 642); v47 follows after v46 is judged. Submissions on 10-13: 3 used, 2 left.
   v42 full cache (version 5) complete and verified: 4,407 studies, 0 errors, 84.4% usable in both compartments (pilot 3:
   80.0%), 3.14 GB (`results/v42/full2`). Next on the ROI line: `v43-roi-experts` (D-031: submit by 10-15, stop by 10-16).
0d. **Update 2026-10-13 02:05 UTC (D-032).** Cause of the slide: heliosli's public R7 one-click notebook (0.956, version 1;
   88 teams rose to >= 0.955 within hours). D-032 (user accepted the fastMRI rule risk): **v46** = that notebook reproduced
   (= v37 with the R7 bundle `8c7b666e27dc0e8f`); commit run: all gates pass, R7 output and submission byte-equal to the
   author's (`results/v46/run1`, `check_v46_gates.py`); **submit only after v45 has scored and its crossing is read**. **v47** =
   v46 + reader 0.10, commit run passes all 11 gates (`results/v47/run1`, `check_v47_gates.py`); submit after v46 is judged. Remaining D-031 probes dropped. Picks on 10-20: best of
   v46/v47 + the old-S6 winner (v40/v45). v42 full cache (version 5) running since 01:42 UTC (version 4 failed at launch:
   Errno 7, arguments now passed as a file).
0c. **Update 2026-10-13 01:45 UTC.** v41 = 0.953 (rejected); v40 persistence confirmed (incumbent). **Silver cut moved to 0.955**
   (310 teams >= 0.955; we are rank 328 at 0.954, inside bronze). Submitted 01:41 UTC: v45 (reader 0.15) and Dense-P alone.
   The fourth anchor probe (v41 + reader) is void; the per-finding reader vector is the next probe if v45 does not win.
0b. **Update 2026-10-12 20:45 UTC (handover).** D-031 approved (re-plan after v40; X cancelled; closed anchor-probe set;
   shrunk ROI line; Dense-P follow-up; v15 no longer automatic). **Ready to submit on 10-13 after the v40 persistence
   snapshot** (`external/lb/2026-10-13a` vs `2026-10-12e/f`): (1) **v45** = v40 with reader 0.15 (commit run: 11 gates pass,
   `results/v45/run1`, `check_v45_gates.py` in the session scratchpad); (2) **Dense-P alone** = `v36-submit` version 3, arm D
   (commit run passes: reference byte-equal, OOF 5.6e-5; local val 0.8998 = P, gold 0.911; expect about P's 0.937; < 0.944
   ends the dense line). v41 (0.4:0.6) scoring since 19:01 UTC, judged against v40 (before-snapshot `2026-10-12f`). Probe
   order (D-031): reader 0.15 -> 0.20 only if 0.15 wins; one shrunk per-finding reader vector; fourth = v41 + reader 0.10 if
   v41 beats v40. **ROI line**: design `v42-roi-experts-design.md` rev 2 + section 11; pilot gate failed once (anterior horns,
   medial misses), user approved one extra tuning round (D-031 amendment) and pilot 3 **passed** (80.0% usable on 75 fresh
   studies, no missing boxes; offset 18 mm, AP 72 x SI 40 mm, 10 mm inferior). **v42 full cache running on Kaggle since
   20:40 UTC (version 4, ~5.4 h)**; then download (`--page-size 200`), build `v43-roi-experts` (local trainer: rectangular
   160 x 288 crops, one output, convnext_nano, P target, fold 0; LM then MM), then `v44-submit` (incumbent + experts,
   order-only per-column blend, design section 5) by 10-15, stop if not submitted by 10-16. Session scripts (scratchpad):
   build_v42.py, v42_roi_core.py, v42_roi_worker.py, test_v42_roi_core.py, mock_s6/, build_reader_probe.py.
0a. **Update 2026-10-12 19:05 UTC.** **v40 = 0.954 and above v37 in the hidden digits: rank 524 -> 235 of 5,853 (211 stable
   witnesses, none reversed; inside the silver cut, rank 292 at 0.954)**; adopt over v37 after the persistence check (D-030),
   then picks v40 + v15. W = 0.936 (passes 0.936; X pending the user's decision on Codex's proposal to cancel X and keep a
   v15-hedge option only at W >= 0.940, D-030 cap 5 -> 4). v41 submitted 19:01 UTC (ref 57116493; before-snapshot
   `external/lb/2026-10-12f`), judged against v40. Submissions on 2026-10-12: 5 of 5 used. Dense-P (v36 arm D) training locally.
   Next: v42 design revision 2 (Codex review of revision 1 in hand: proceed with changes, 9 points), then D-031.
0. **Update 2026-10-12 ~15:15 UTC.** D-030 approved and running: v40 (R1) and v36 W submitted 13:05 UTC (refs 57107964,
   57107968; commit runs pass all gates; scores pending, user reports them); v41 commit run passes all 8 gates, submit after
   v40's rank-crossing comparison; Codex code review of v40/v41 recorded (design section 7; failure-path fixes for future
   builds only). Leaderboard snapshot `external/lb/2026-10-12e` (rank 524). New aggressive line under discussion (not yet a
   decision): `aggressive-routes-2026-10-12.md` (independent Claude/Codex proposals, cross-review, GitHub search: rank-89 team
   reached 0.957 on the S6 host with per-finding ROI experts; unlicensed, ideas only), `roi-experts-feasibility-2026-10-12.md`,
   and design `v42-roi-experts-design.md` revision 1 (Codex review running; record D-031 after it). User go-ahead: step 0
   (design + review) and **Dense-P = v36 arm D running locally** (commit 591a717: P target, K_train 16, head LR 1e-3, stem +
   stages 0-1 frozen; 216 img/s, ~6 h; log `results/v36/local_f0/v36/v36_log_fold0_D.txt`). Next: Codex verdict -> D-031 ->
   v42 pilot on Kaggle (150 studies) on 10-13. Team merger: the user is contacting a solo team (their own step).
1. **Next (awaiting the user's go-ahead):** `docs/research/v40-anchor-probes-design.md` revision 2 (Codex-reviewed, uncommitted
   until approved; record as D-030 when approved): R1 = `v40_submit` = v37 + public goodpjw2008 2.5D ConvNeXt reader (3 folds)
   at a uniform outer weight 0.10; A1 = `v41_submit` = original v37 with CoAtNet:S6 0.4:0.6 for all 12 findings (including the
   three OA overrides in `W_RAPTOR_C`); v36 W fold-0 test; conditional X. Whole-sequence cap: at most five further
   submissions; no A2, no combinations; anchor probing closes 2026-10-17.
2. **Closed lines:** our v26/v29 leg (D-029: v35 0.953 rejected, v39 0.954 no crossing; no more leg variants); v38 retired;
   the public 0.956 is not reproducible (author's version 1 used an unavailable R6 S6, L32). "D-026" was never recorded.
3. **v36 (D-027):** local C/G/P and Kaggle C/W done (`results/v36/`); P alone 0.937 (passes 0.936 vs v14 0.934, below 0.940);
   W +0.0010 vs C (not flagged): W fold-0 LB test is next (`v36-submit` notebook, add W to `lingxd/rsna-knee-v36-weights`).
4. Kaggle facts: at most two GPU batch sessions at once; submissions refuse non-versioned datasets (use
   `rsna-knee-compact-v1` for S6); status checks of short commit runs are handed over to the agent, scoring is not polled.
   GPU quota 20.4 h left until 2026-10-17 (12:30 UTC). The previous window (local_bd917ada) must not be used.

## Open questions

- Is the OAI-trained CoAtNet allowed? D-019 accepted the risk. **Host statement found 2026-10-13** (topic 741819, 09-21,
  Po-Hao "Howard" Chen): OAI does not violate the rules if generally accessible to all without institutional review or a
  legal team, and free; participants report individual Login.gov access ("Institutional Approval Required: No") but also
  country blocks (China). No explicit yes/no (topic 743416). Lower risk than assumed, not settled. fastMRI (R7) unchanged.
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
