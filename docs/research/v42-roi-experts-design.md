# v42-v44 design: per-finding high-resolution ROI experts on the incumbent (revision 2)

Status: revision 2 after the Codex review of revision 1 (section 10; verdict "proceed with changes", all nine required changes
accepted). Decision D-031 (2026-10-12): Lateral + Medial Meniscus only, fold 0, one fixed submission, pilot gate 10-13, stop
if no end-to-end submission by 10-16. Evidence: `roi-experts-feasibility-2026-10-12.md`, `aggressive-routes-2026-10-12.md`
sections 5-8, `replan-after-v40-2026-10-12.md`; STATUS v07, v28, v32-v40, v36; lessons L19, L21, L25, L26, L29-L33.

## 0. Summary

Our own version of the per-finding ROI-expert idea (another team: public 0.954 S6 + CoAtNet host -> 0.957; their code and
annotations are unlicensed and not used). Localisation, side and geometry come from S6's public code path (SKM-TEA
`anatomy.pt` anchors). Two experts: Lateral Meniscus (LM) and Medial Meniscus (MM). Each is blended into its own column of
the incumbent (v40, or a D-031 anchor-probe winner) by a fixed order-only rule (section 5); every other column is byte-equal
to the incumbent. Versions: `v42-roi-cache` (Kaggle: ROI crops from DICOM), `v43-roi-experts` (local training), `v44-submit`.

## 1. Boundary

Allowed: ideas and published results of `github.com/VaryaStrizhneva/RSNA-project`; heliosli's public S6 code paths accepted
under D-023 and extended by D-031 to generating our own ROI crops: native decoding, `training.geometry_bank`, the side check of
`compact_infer.CStudies._native_and_geometry` (side classifier `side_cls.pt`, `FORCED_SIDE` re-render),
`knee_anchor_bank_v2.AnchorBank`, `anatomy.pt` (SKM-TEA V-Net_E1, Apache-2.0 upstream). Not used: the other team's code,
annotations, coordinates, caches, weights; KneeXNet; the ligament atlas; OrthoFoundation `best.pt`.

## 2. Geometry contract and boxes

- **Per-study path (verified in `compact_infer.py` lines 48-152, 160-205)**: `CStudies(..., views='v4', anchor_weights=anatomy.pt,
  side_model=side_cls.pt, ...)` with the S6 bundle's side parameters; per study `_native_and_geometry(uid, work)` (native render,
  geometry bank, side check, forced re-render when the classifier is confidently negative), then
  `bank.record(uid, study, geo_dir)`; our ROI export runs **before** the per-study cleanup. One worker process per GPU on
  disjoint study lists (the module-level `OneStudySource.current` and `FORCED_SIDE` are process-global).
- **Side**: the side of the (possibly re-rendered) series, `study['series'][*]['side']`, must be a single `L` or `R`; otherwise
  the study is *unusable* for the experts. v07's side is a cross-audit only and never overrides S6's.
- **Axes (DICOM LPS)**: +x patient left, +y posterior, +z superior. Medial = towards the midline: right knee medial = +x,
  left knee medial = -x; lateral is the opposite.
- **Compartment centre prior**: `joint_lps + s * 22 mm * x_hat` (s = +1/-1 by side and compartment). This is a prior, not a
  located compartment (AnchorBank's joint centre is the centroid of cartilage + meniscus on 7 central sagittal slices).
- **Sagittal depth**: for each sagittal slice, the intersection of the left-right line through the compartment centre with
  the slice plane (from the per-slice `(col,row,1) -> LPS` affine of the geometry bank, which already contains the native
  transposes/flips; no extra mirroring); slices with |x_slice - x_centre| <= 14 mm are kept, in physical order; thin stacks
  (< 1.75 mm) averaged to about 3.5 mm slabs as S6 does.
- **Box**: AP 56 x SI 40 mm centred on the projected point, resampled from the native slice through its affine to
  224 x 160 px (0.25 mm/px requested; native spacing recorded; coarser natives are interpolated). Series priority: sagittal
  fluid-sensitive, else sagittal non-FS. Intensity window: 0.5-99.5 percentile over the whole ROI volume, padding excluded.
- PF and ACL boxes are dropped (D-031: no second wave).

## 3. Automatic usability rule (identical in training, pilot and test)

A study's box for one compartment is **usable** if: anchor `method` is `skm_tea_joint*` (any `slab_prior` is rejected); side
is a single `L`/`R`; >= 3 kept slices; on every kept slice >= 80% of the box lies inside the image. Unusable rows keep the
incumbent's value in that column (section 5). AnchorBank's `in_field` (centre only) is recorded but not sufficient.

## 4. v42-roi-cache (Kaggle)

- **Pilot (10-13)**: 150 training studies stratified by side tag/geometry, manufacturer, field strength, 2-D vs 3-D sagittal,
  oblique protocols. Split by a fixed hash into a **tuning half** (box parameters may be adjusted once) and an **acceptance
  half** (frozen parameters; the gate is computed here only). Output: crops, metadata, one montage PNG per study (the slice
  through each compartment centre with both boxes drawn, the anterior horn, body and posterior horn visible, plus crop strips).
  Claude reviews **all** montages and reports by stratum: left/right, side source, oblique, 3-D, anchor method.
- **Gate (acceptance half)**: usable for both menisci >= 80% by the automatic rule; among usable boxes, wrong compartment,
  wrong side or missing horn/body <= 5%; projected full run <= 13 GPU h of quota (decode + anchor about 7.9 s per study
  serially, so two parallel workers are required) and <= 18 GB **total** output per notebook run (crops, montages, metadata).
  Fail: stop the ROI line (D-031).
- **Full run (10-14)**: 4,407 studies (gold included for descriptive use, never trained on); per-slice uint8 crops (no stored
  triplets) with an index (study, compartment, slice order, offsets) in shards of <= 200 studies, stored so that one study can be
  read without decompressing the shard (`.npy` + offsets); SHA-256 manifest for the download; determinism check: 20 studies
  re-rendered in a later session (covering side flips, oblique, thin stacks) must give identical pixels and semantic metadata.

## 5. v44-submit (Kaggle): order-only per-column blend with row fallback

Incumbent cells unchanged, its output saved; then the ROI stage in its own process group (two workers, one per GPU, test
studies split in halves), then the experts. For an expert column c with valid rows V (usable box and finite expert output):

1. `a = rank of incumbent[c] within V`, `e = rank of expert[c] within V` (average ties, both over V only);
2. new order of V by `0.5 * a + 0.5 * e` (ties broken by the incumbent's order);
3. the incumbent's own values on V are sorted and reassigned to V in the new order; rows outside V keep their exact values.

The column's multiset of values is unchanged; with V = all rows this has the same ordering as the fixed rank blend (AUC
depends only on order). Tests before the build passes: all rows invalid, one valid row, partial validity, NaN expert, timeout,
exception, killed workers; the parent process kills the group, restores the saved file and writes `submission.csv` atomically.
Deadline 8.25 h from the notebook start; ROI stage launched only with >= 1.5 x its projected time left (projection from the
pilot: about 7.9 s per study serially, about 1.5 h for 1,300 studies with two workers, plus the incumbent's about 4.5 h).
Commit-run gates: incumbent parts equal to its own commit run; ROI crops of the 3 placeholder studies equal to a local
rendering of the same files; expert outputs equal to local inference on the same crops (1e-3); blend recomputed; non-expert
columns byte-equal.

## 6. v43-roi-experts (local GPU)

A new notebook derived from the v36 trainer (not a configuration of it): rectangular inputs (H, W) = (160, 224); one output;
the study list filtered by the usability rule (counts reported, not the fold totals); windows = up to `min(16, n)` same-series
triplets over the physically ordered kept slices (no repeats of a centre); `convnext_nano.in12k_ft_in1k` with gated attention
pooling; target = P's round-3 target for the finding (`0.5 x 4-source soft + 0.5 x v13 arm-N OOF`; gold excluded); fold 0;
20 epochs max, AdamW 1e-4 / 1e-3, cosine, warm-up 1, effective batch 16 studies, augmentation as v36 without flips, fp16;
checkpoint by validation AUC of the finding against `soft >= 0.5`; 0-2 loader workers (L19, L25). The local runner gains `v43`.
**Diagnostics only** (no gate, no selection): validation AUC of the expert, of `rank-mean(expert, v13 N OOF)` and of N OOF on
the usable validation rows and on all 947 rows with the fallback; the N-OOF teacher makes fold-0 validation leaky (v36 design
section 3).

## 7. Decision rules (D-031)

| Stage | Rule |
|---|---|
| Pilot gate (10-13) | section 4; fail stops the ROI line |
| v44 (by 10-16) | the then-incumbent + LM + MM by section 5; adopted by display or rank crossing (>= 20 stable witnesses, none reversed, persistence); no end-to-end submission by 10-16 stops the line |
| Expansion | only if v44 displays >= 0.956 and beats the incumbent: folds 1-2 of LM and MM, one submission |

## 8. Budgets

Kaggle before the 10-17 refresh: pilot <= 1 h, cache <= 13 h, integration and commit runs <= 2 h (D-031 totals <= 17 h).
Local GPU: two experts <= 6 h (Dense-P runs first). Submissions: one (v44) plus one conditional expansion, inside D-031's
research cap.

## 9. Risks

Localisation (about 17% slab-prior anchors in v34, all rejected by section 3, so coverage may fail the gate); SKM-TEA trained
on qDESS; the compartment prior ignores rotation; S6 already has 0.26 mm/px anchored locals, so a gain must come from
placement and per-finding supervision; the other team's +0.003 was on CoAtNet:S6 0.7:0.3 and without the reader; runtime
tail; the 18 GB output limit; Windows commit limit for local training.

## 10. Codex review of revision 1 (GPT-6 Astra, high, read-only, 2026-10-12) and disposition

Verdict: proceed with changes (bounded pilot worth doing; revision 1 not yet sufficient for the full cache and training).

| # | Required change (severity) | Verified | Disposition |
|---|---|---|---|
| 1 | Side and geometry contract: use S6's tag / IPP rule, side classifier and `FORCED_SIDE` re-render; read the re-rendered series side; LPS axes; v07 only as an audit (high) | Yes (`compact_infer.py` 48-152) | **Accepted** (section 2) |
| 2 | +-22 mm is a prior; depth by line-plane intersection per slice; horn/body QC; PF/ACL need their own QC (high) | Yes (`knee_anchor_bank_v2.py` record; PF fallback differs from S6) | **Accepted** (section 2); PF/ACL dropped by D-031 |
| 3 | QC must be automatic at test time; review all 150 pilot studies; separate tuning and acceptance (high) | Yes | **Accepted** (sections 3-4) |
| 4 | Row fallback conflicts with re-ranking the whole column (v37's output is a weighted mean of ranks) (high) | Yes (v37 cell 9) | **Accepted**: order-only reassignment on valid rows (section 5) with tests |
| 5 | Executable S6 reuse interface; export before cleanup; separate processes for the global state; all planes decoded for the side check (medium) | Yes (`compact_infer.py` 160-205) | **Accepted** (section 2) |
| 6 | Cache as single-slice uint8 + offsets; 18 GB is the total output; determinism on pixels and semantic metadata; decode + anchor about 7.9 s per study (9.7 h train, 2.85 h test serially) (medium) | Yes (v34 timings) | **Accepted** (sections 4-5): two parallel workers |
| 7 | P's target usable but not an honest host proxy; diagnostics only (medium) | Yes | **Accepted** (section 6) |
| 8 | The v36 trainer needs real adaptation (rectangular input, one output, filtering, `min(16, n)`, physical order; runner support) (medium) | Yes (v36 cell 6, `local_v13.py`) | **Accepted** (section 6): new notebook |
| 9 | Decision boundaries: extend D-023, Dense-P inside the new cap, compare with the then-incumbent, no stacking on v40/v41 by default (medium) | Yes | **Accepted** via D-031 (host = the then-incumbent, which may be v40) |
