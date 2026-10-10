# v25-v30 design: CoAtNet two-path inference (I1) and local-view models (B1, B2)

Status: revision 2 after the Codex review (section 7; required changes accepted, the separate cache pilot
replaced by a local audit of the full cache). Plan: `plan-2026-10-10-local-views.md`, approved by
the user on 2026-10-10. Evidence: `public-landscape-2026-10-10.md` (S6), STATUS L20-L26.

## 0. Summary

| Item | Version | GPU | Kaggle | Rule (pre-registered) |
|---|---|---:|---|---|
| I1: public CoAtNet through the exact pipeline and the v07 adapter, rank mean, then v17's reader fusion | `v25_submit` | 0 | commit run + 1 submission | adoption over v19 at >= 0.952 |
| B1: N recipe + a central 100 mm local view cropped from the v07 cache, report-only target, fold 0 | `v26` (training), `v27_submit` (v17 + v26 at 0.15) | about 4.5 h local | 1 submission | B2 continues regardless (B1 is a cheap early read) |
| B2: same model with the local view rendered from DICOM at 100 mm (new cache) | `v28` (cache, CPU), `v29` (training), `v30_submit` (v17 + v29 at 0.15) | about 4.5 h per fold local | cache 1-2 CPU h; 1 submission per gate | v30 >= 0.951: one more fold; >= 0.952: 3-4 folds |

## 1. Common rules

- New legs are tested in one fixed form: `final = rank(0.85 * rank(v17 output) + 0.15 * rank(leg))`, v17
  cells unchanged (as v19, w 0.15). No other weights are submitted from this design.
- Adoption over the current OAI pick (v19, 0.950) needs a displayed 0.952; 0.951 funds limited expansion
  only. Gold-58 is a screen.
- Large experiments stop 2026-10-19. Local GPU per D-016 and L25 (2 loader workers, evaluation in the main
  process where needed, stall watchdog).
- No SKM-TEA, KneeXNet or OrthoFoundation assets: localisation is the acquisition centre (the image
  centre, S6's own fallback). Code reused from the heliosli notebook (Apache 2.0) is credited.

## 2. I1 - `v25_submit`

**Composition.** v17's CoAtNet cells unchanged write the exact CoAtNet ranks (`_sota_0949.csv`). A leg (two
processes, one per GPU) prepares each test study with the v13 leg preprocessing (v06 slot selection, v07
cache rendering; byte-equal reference check on three training studies), builds the 96-slice adapter volume
(v23 core: slot mapping, original-index slice picks, flips undone, 267 px crop resized to 320, intensity
'restretch'), and runs the same CoAtNet checkpoint (strict load, SHA-256 checked) with K94 and the mirror
view, fp16. Combined CoAtNet = `rank(0.5 * rank(exact) + 0.5 * rank(adapter probabilities))`, written as the
CoAtNet output (`submission.csv` and `_sota_0949.csv`) before v17's reader fusion cell runs unchanged.

**Evidence.** Gold: adapter 0.9256 vs exact 0.9228, Spearman 0.984; exact + adapter 0.9246; with the reader
(TW) 0.9269 vs v17 0.9245 (+0.0024, CI -0.0014 to +0.0064, P(<= 0) 0.11). Against: the two paths are 98%
correlated; gold is reused.

**Gates (commit run).** (1) The exact CoAtNet output equals v17's `_sota_0949.csv` byte for byte. (2) Leg:
both shards done, reference check byte-equal, coverage 1.0, and an **adapter parity check**: the three
reference training studies run through the full leg path reproduce the local v23 teacher probabilities
(`v23_teacher_probs.csv`) within 2e-3 (fp16 on T4 vs RTX). (3) The reader fusion is applied (as v17) and
the combined ranks are recomputed locally from the saved exact ranks and adapter probabilities. A commit run
that falls back blocks the submission; on the hidden test a failed leg leaves v17's output.

**Runtime.** Adapter leg on about 1,300 studies: preprocessing about 0.3 h (v07 measurement) plus about
244 k CoAtNet images on two T4s (estimate 30-40 min); total with v17 under 2.5 h.

**Implementation (2026-10-10, `notebooks/v25-submit.ipynb`).** v17 cells 2-11 byte-identical; the leg
script is the v19 leg preprocessing verbatim (reference check included) plus a `pack` that stores the
per-slot series UID, series length and flips in the leg cache, and the v23 core `build_volume` reading them.
Local checks before the push:

- Port test (CPU): rebuilding leg cache entries from 310 v07 studies (the 10 parity studies + 300 random)
  gives the v07 arrays back, and the leg adapter volume, mask and evaluation centres equal the v23 core
  output on all 310 (0 failures).
- Parity tolerance, measured on the local GPU on the 10 parity studies against `v23_teacher_probs.csv`:
  fp16 rerun max error 7e-5 (6-decimal storage plus cuDNN), fp32 vs fp16 max 4.8e-4 (a proxy for
  cross-GPU fp16 differences). The 2e-3 tolerance is kept (4x the proxy); a wrong flip or slice pick moves
  probabilities by far more. The adapter-volume SHA-256 is reported but not gated (a JPEG decoder or
  resize difference on Kaggle would change bytes without changing the model input materially).
- Control flow (CPU, DICOM replaced by the v07 cache, CoAtNet by a stub): prepare, pack, parity check,
  prediction, shard CSV and receipt run end to end.
- Fusion cell on the v17 commit-run outputs: recomputing v17's fusion from the saved parts reproduces v17's
  submission exactly (max difference 0.0); with all gates the I1 output equals an independent computation;
  a failed parity check, a missing shard or a missing reader output each keep v17's submission.

Deviation from the gate list: on the hidden test the leg is used at coverage >= 0.98 of the unique test
studies, a missing study taking its exact rank (as v19); the commit run must still show coverage 1.0.
The commit run (`lingxd/v25-submit` version 1, pushed 2026-10-10 ~15:08 UTC) is checked against gates 1-3
before the submission.

## 3. B1 - `v26` (local view from the v07 cache)

**Model.** The v13 trainer (arm N recipe: ConvNeXt-tiny `fb_in22k_ft_in1k`, 320 px triplets, 15 epochs, LR
1e-4 / 3e-4, gated per-finding attention) with a second view per slot: for every sampled centre, the same
three slices centre-cropped to 229 px (100 mm of the 140 mm field) and resized to 320 px (`INTER_LINEAR`).
Local tokens get their own slot ids (5-9), so the slot embedding has 10 entries. K_train 4 and K_infer 16
per slot and view (40 training tokens, 160 evaluation tokens per study); the same augmentation is applied
to both views of a centre. **Target: report-only** (`OOF_WEIGHT = 0`: the v06 4-source soft target, cell
weights unchanged), following the reader and S6 (no image teacher; STATUS L26 and the gold trend in
`new-models-2026-10-10.md`).

**Run.** `notebooks/v26-local-views.ipynb`, fold 0, local (runner `scripts/local_v13.py --version v26`).
Smoke run first (L25). Reported: fold-0 validation and gold, Spearman with N fold 0 and with the public
CoAtNet on gold (diagnostic only).

**Submission `v27_submit`.** v19 notebook with the v26 fold-0 leg (two views, K_infer 16) at w 0.15; leg
checks as v19 (reference byte-equal, OOF of the fold-0 reference study at 1e-3, coverage). Confound: B1
changes both the views and the target against N; the blend score is what decides.

**Implementation (2026-10-10, `notebooks/v27-submit.ipynb`).** Built from v19 by `build_v27` logic: v17 cells
unchanged; the leg keeps v19's preprocessing, reference check, deadline and fallbacks, with the data and model
sections of the v26 trainer; the model is built from the checkpoint cfg (asserting two views, crop source,
ImageNet normalisation, 320 px) and loaded strictly. The checkpoint stores `timm_kwargs: None`, which the first
draft would have passed as `**None`; fixed before the push. Local GPU test of the leg's own model code on the
fold-0 reference study: max difference to the v26 OOF 1.4e-4 (tolerance 1e-3).

## 4. B2 - `v28` cache and `v29` model (local view from DICOM)

**Cache `v28`.** The v07 notebook with one change: the field is a **100 mm** centre crop (instead of 140 mm)
rendered at 320 px from the DICOM pixels (0.31 mm per pixel, about the native spacing). Everything else as
v07: same studies, slot series, stored slice indices (`raw_index` equal to v07, checked), geometry sort,
canonical orientation and laterality, percentile window computed on the cropped field, JPEG q92. Expected
size about 14 GB (one Kaggle output), CPU about 1-1.5 h. Gate: every study present; per slot the stored
`raw_index` lists equal v07's; 10 preview montages look sane.

**Cache result (2026-10-10, `lingxd/v28-local-cache-100mm` version 1).** 4,407 studies, 0 errors, 14.44 GB
(JPEG quality 92 chosen by the pilot: 14.28 GB projected), 0.88 h CPU. Audit (`scripts/audit_v28_cache.py`,
outputs in `results/v28/audit/`): every (study, slot) matches v07 in presence, series, series length, stored
count, flips, reversal and sort method (22,035 rows), and the stored slot and raw-index arrays match in all
4,407 studies. On 800 random studies (4,000 middle slices) the v28 slice correlates with the matching central
crop of the v07 slice at median 0.979 (5th percentile 0.941, minimum 0.82; the lowest are noisy Siemens
coronal fat-suppressed series at 180 mm, where the finer v28 sampling keeps more noise), with no difference
by side, field of view or vendor; zero pixels in v28 slices: 95th percentile 3.4% (air around axial
sections). The foreground share inside the central 100 mm is a median 0.64 of the v07 field (it measures
field size, not clipping). The 44 montage pairs (random per slot, smallest foreground share, lowest
correlation, smallest field of view) and the notebook previews show the femorotibial joint inside the 100 mm
field in every case; the patella and the popliteal region are at or beyond its edge in some sagittal slices,
which the full view keeps. No systematic clipping: the stop/revise rule is not triggered. The v29 notebook's
own alignment check and a dataset check (local token equal to the v28 slice at the full token's index) pass on
the downloaded cache.

**Model `v29`.** B1 with the local tokens read from the v28 cache at the same slice indices instead of
cropping v07. Fold 0 first; folds 1-4 only per the gate in section 0.

**Submission `v30_submit`.** v19 notebook with a leg that renders both caches from DICOM (v07 code and the
v28 variant; byte-equal reference checks for both) and the v29 models at w 0.15.

## 5. Risks

1. I1's paths are 98% correlated; any gain may be below the 0.001 display step.
2. B1/B2 change views and target together; a failure does not say which part failed, a success does not
   say which part worked.
3. The acquisition centre is not the joint centre in off-centre scans (S6 used SKM-TEA anchors; we do
   not, for rule risk). A 100 mm field around the image centre still covers the joint in most series
   (the median field of view is 160 mm, `competition.md`).
4. Report-only targets made v08 weaker alone (0.909) than N (0.936); a weaker but different leg can still
   add at w 0.15 (the reader is 0.929 alone), or it can lose as v09 did.
5. Time: B2 needs the v28 cache by 10-12 and one local fold by 10-13 to leave room for expansion.

## 6. Review questions

1. Are the gates sufficient, in particular I1's adapter parity check across platforms?
2. Is report-only supervision the right choice for B1/B2, or should B1 keep N's target to isolate the view?
3. Is the 100 mm image-centre crop at 320 px a reasonable stand-in for S6's anchored local views?
4. Anything to cut to fit by 2026-10-19?

## 7. Codex review (GPT-6 Astra, high, read-only, 2026-10-10) and disposition

Verdict: proceed with changes. Findings checked against the files.

| # | Finding (severity) | Verified | Disposition |
|---|---|---|---|
| 1 | I1: injecting before v17's reader cell works only if both `submission.csv` and `_sota_0949.csv` are replaced, and then the fallback is combined-CoAtNet alone, not v17 (high) | Yes (v17 cell 11 reads `_sota_0949.csv`, restores `_sota_backup.csv` on error) | **Accepted**: v17 runs unchanged to completion; its submission, exact ranks and reader output are saved; the adapter leg runs after; the I1 fusion is recomputed from the saved parts and replaces the submission only when all gates pass, otherwise v17's output stays |
| 2 | I1: three probability comparisons do not validate the adapter port; it needs series identity, original length and flip flags that the v19 leg's pack drops; coverage check is weak (high) | Yes | **Accepted**: the leg carries the v07 per-slot metadata to the adapter; two gates: CPU equality of the adapter volume, mask and centres with the v23 implementation on the reference studies, and T4/RTX probability parity on 10 training studies chosen across planes, laterality, duplicate slots and series lengths (per-label max error reported, tolerance 2e-3 to be checked empirically); coverage = unique test IDs, finite probabilities in [0, 1] |
| 3 | B1/B2: 80 training images per micro-step and 160-token evaluation in one batch; v13's fp32 reload check repeats the L25 stall (high) | Yes | **Accepted**: micro-batch 1 x 8 accumulation, evaluation chunks of 40, fp32 reload chunk 8, evaluation in the main process; smoke run admits the configuration with measured memory, commit and time |
| 4 | B1: augmentation is sampled per call, so two views do not share it; `N_SLOTS` is both the cache slot count and the embedding size (medium) | Yes | **Accepted**: 5 physical slots and 10 token types; each centre sampled once; both views built from the same three slices, cropped and resized before one shared augmentation (translations as image fractions); the submission leg mirrors the contract |
| 5 | Report-only: `OOF_WEIGHT = 0` gives the soft target but still requires the v11 files; runner lacks v26/v29 (medium) | Yes (4,349 studies, weights intact) | **Accepted**: explicit report-only branch without teacher inputs, independent target check, runner support |
| 6 | B2: raw-index equality does not prove the same series or orientation; padding below a 100 mm field is windowed raw zero (medium) | Yes | **Accepted**: join v28 to v07 per (study, slot) on series UID, presence, series length, raw indices, flip and reversal flags, image count; mismatches fail training; padding behaviour recorded (one selected series below 100 mm) |
| 7 | A single central crop is a weak stand-in for S6 (which keeps offset patellofemoral, posterior and +-30 mm coronal views); 30.6% of slot entries are subsampled to 32 slices; restore a stratified 100-study pilot (high) | Partly | **Accepted in framing**: B2 is a *central magnification* experiment, S6 is motivation only. The full view (v07, 140 mm) keeps patella and posterior structures; the local view targets the joint. **Pilot run rejected**: the full v28 cache costs about 1.5 CPU hours and no GPU quota, so it runs directly; the stratified visual audit (planes, laterality, field of view, spacing, off-centre series, patella and compartments) is done locally on the downloaded cache before training, with a stop/revise rule for systematic clipping |
| 8 | Budgets need measurement; B1 has weak decision value; decision table incomplete (medium) | Yes | **Accepted**: T4 throughput and runtime measured in the commit runs; B1 is cut first if it delays B2 and doubles as the loader/model smoke test. Decision table: below 0.951 stop the line; folds mean total folds (2 at 0.951, 4 at >= 0.952); a second-fold blend that does not improve stops expansion; runtime over 2.5 h of hidden scoring for the leg stops deployment; a verified 0.951 candidate is kept for final comparison |
