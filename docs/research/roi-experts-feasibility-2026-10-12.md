# Feasibility: per-finding high-resolution ROI experts on v37 (2026-10-12)

Status: feasibility report for the user's decision (not a design note; no decision yet). Written by Claude and Codex (GPT-6
Astra, high, read-only, web search on) after the GitHub finding in `aggressive-routes-2026-10-12.md` section 8; each
investigated independently, then the claims below were cross-checked (verifier named). Evidence cited from STATUS: v07,
v28, v32-v39, v36; lessons L19, L21, L25, L26, L29-L31.

## 1. Why this route now

A top-100 team (rank 89, public 0.957) logs, on the same base as ours (heliosli S6 + nartaa CoAtNet, 0.954): eight
per-finding ROI experts blended per column at 0.5 gave 0.953 with resnet18 and **0.957 with convnext_nano** (one-variable
change). Their other levers (label tables, fusions, weight schemes, more epochs) were measured zero, like ours (L23). Their
host was CoAtNet:S6 0.7:0.3; v37 is 0.5:0.5, so neither the +0.003 nor their per-column ranking transfers automatically.
Their landmarks came from about 170 manually annotated studies (no licence: ideas only).

## 2. What we can build on (verified)

| Fact | Verified by |
|---|---|
| `anatomy.pt` is a 2-D V-Net with four sigmoid channels: patellar, femoral, tibial cartilage, meniscus (`training/anatomy.py` lines 18, 46); no ACL, MCL, bone or cyst classes; menisci not split medial/lateral | Claude, Codex |
| S6's `knee_anchor_bank_v2.py` segments 7 sagittal slices about 4 mm apart, returns **joint centre and patella centre in patient LPS mm** projected into every series; tissue probabilities are not kept | Claude, Codex |
| S6 v4 views are 100 mm locals at 384 px (0.26 mm/px, centre crop 352): joint, patellofemoral, posterior (sagittal/axial), medial/lateral 30 mm either side (coronal) | Claude, Codex |
| Anchor fallback to the geometric slab prior in v34: about **17% of 150 studies** (worker0: 15 of 75) | Codex, Claude (logs) |
| `compact_infer.py` deletes each study's native volume, geometry and anchors in `finally` (`shutil.rmtree(work)`), so nothing is reusable after S6 without a hook | Codex, Claude |
| Measured S6 per-study means (v34): decode 5.6 s, render 2.6 s, four classifiers 16.7 s; anchors about 2.3 s (worker logs) | Codex, Claude |
| Sampling: v07 0.4375 mm/px, v28 0.3125 mm/px, DICOM render at 0.25 mm/px; only 37.1% of SAG_FS series are natively finer than 0.3125 mm; 31.7% of SAG_FS are thinned by the v07 32-slice cap | Codex (v06/v07 indexes) |
| `anatomy.pt` SHA-256 equals the official SKM-TEA V-Net_E1 checkpoint, listed under Apache-2.0 upstream | Codex (web); not re-checked by Claude |

Consequence: S6 already sees 0.26 mm/px anchored 100 mm views, so new experts must gain from **precise placement,
per-finding supervision and small context**, not from resolution alone. Upscaling our JPEG caches recovers nothing; ROI crops
must be rendered from DICOM on Kaggle.

## 3. Feasibility by component

| Component | Plan | Cost (estimate unless measured) | Main risk |
|---|---|---|---|
| Localisation | S6 anchor code (joint, patella LPS) + mm offsets per finding; optional wider sagittal sampling keeping the meniscus channel | anchors ~2.3 s/study (measured) | 17% slab-prior fallback; qDESS -> clinical PD/T2 transfer unvalidated; side errors swap menisci |
| Boxes, first wave | Lateral and Medial Meniscus (about 56 x 40 mm -> 224 x 160 px, physical-depth sampling), then PF OA (patella-centred), then ACL (notch box) | - | ACL is geometric only; MCL / Baker's not this week |
| Cache | Kaggle: decode -> S6 geometry -> anchors + QC -> crop from native -> uint8 + geometry metadata, sharded <= 18 GB per output | 5-6 h wall for 4,407 studies (9 h with wider sampling); 2 experts ~7 GB, 4 ~14 GB uncompressed (16 windows, 224^2) | output limit 20 GB; quota; download 0.5-2 h |
| Training | one ConvNeXt-nano per finding, rectangular input, same-series triplets, light attention pooling, report-soft labels, gold excluded, fold 0 (3,402 / 947 / 58), <= 20 epochs | 1.5-3 h per expert per fold locally (estimate from v36 P 158 img/s) | Windows commit limit: 0-2 loader workers (L19, L25) |
| Inference | v37 cells unchanged; then a separate ROI stage (re-decode test DICOMs, same anchor + crop code as the cache) and the experts; per-column rank blend 0.5 on the expert columns only; bad localisation / empty / unknown side / non-finite rows keep v37's value; exception or 8.25 h deadline restores the saved v37 file | +0.4-1.5 h on ~1,300 studies (Codex 0.4-1.0 h with an export hook inside S6; Claude prefers re-decoding to leave S6 untouched, about 1-1.5 h); total about 5-5.5 h | runtime tail; train/test rendering parity |

## 4. Plan and gates (consensus; Codex's schedule with Claude's inference choice)

| Date | Work | Go / no-go |
|---|---|---|
| 10-12 | ROI design note + Codex gate; Dense-P smoke and fold 0 start locally (the one kept item of the section-5 plan); D-030 unchanged | Dense-P stops if a fold projects > 8 h |
| 10-13 | Kaggle pilot: 150 training studies (left/right, vendors, oblique, 3-D), anchors + meniscus boxes + timing + quota charged; montages of >= 40 studies inspected, failures included | >= 80% of studies with both meniscus boxes usable; <= 5% wrong box or side among usable; full cache <= 13 GPU h and <= 18 GB per output; else **stop ROI** |
| 10-14 | Full cache (4,407), download, parity check against live rendering; Lateral Meniscus expert end to end, then Medial Meniscus | first expert <= 3 h per fold |
| 10-15 | Submission: v37 + two meniscus experts (fixed 0.5 per column); Dense-P alone | adopt by D-030 rules (display or rank crossing) |
| 10-16 | If ROI wins: predeclared PF OA + ACL package. If ROI fails and Dense-P >= 0.944: fixed v37 : Dense-P 0.75 : 0.25 instead (mutually exclusive) | no post-hoc column picking or weight search |
| 10-17/18 | Quota refresh: verification; folds 1-2 for a winning package only if its blend displays >= 0.956 and beats the incumbent (local <= 12 h) | no automatic expansion (L31) |
| 10-19 | Last conditional scoring; freeze; 10-20/21 verify final artifacts | - |

Budgets: Kaggle before 10-17 <= 20 h (pilot 1, cache 13, integration / commit runs 2, D-030 2, margin 2); after the refresh
<= 18 h (verification 6, Kaggle training fallback 12); local <= 46 h (Dense-P 9, four first-fold experts 12, conditional
folds 12, D-030 conditional work 11, verification 2); **new line at most four submissions** (Dense-P alone; two-expert
blend; four-expert package or Dense-P blend; conditional expansion); D-030's five stay separate and non-renewable; at most
five per day in total; submissions that can change the team's best are scored one at a time.

Dropped or deferred: the S6 held-out teacher (its 10 h goes to the ROI cache; resumable only if the 10-13 gate fails and
quota remains); eight experts; manual annotation and a new landmark model; MCL and Baker's experts; label fusions;
multi-plane and architecture searches.

## 5. Probabilities (subjective, including engineering failure)

| Route | Usable version by 10-19 | Fixed blend displays >= 0.956 | >= 0.957 |
|---|---:|---:|---:|
| Two to four ROI experts (Codex) | 65-75% | 15-25% | about 10% |
| Section-5 Dense-P + Dense-S6 (Codex) | 80-90% | 10-20% | - |
| Claude's estimate for ROI | 60-70% | 15-20% | about 10% |

Scale: +0.002 macro from two columns needs +0.012 blended AUC on each; from four columns +0.006 each.

## 6. Rules

`anatomy.pt` is a public Apache-2.0 model (upstream SKM-TEA), already in the v37 picks under D-023; using its anchors to
train **our own** ROI experts extends D-023's scope and needs a new decision (D-031). heliosli's code dataset is licence
"other" with "no new open-source license granted": reuse only the code paths already accepted with S6 (anchor bank,
geometry, rendering), credit the source, no redistribution. KneeXNet, the ligament atlas and OrthoFoundation `best.pt` stay
excluded. The rank-89 repository has no licence: ideas and published results only; no code, annotations, coordinates,
caches or weights.

## 7. Remaining differences between the reviewers

| Point | Claude | Codex |
|---|---|---|
| Test-time ROI rendering | separate stage after v37 (re-decode; S6 code path untouched) | export hook inside S6 before cleanup (cheaper, but edits the author's stage) |
| Probability of a usable version | 60-70% | 65-75% |
