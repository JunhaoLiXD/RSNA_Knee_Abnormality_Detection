# External resources by pipeline stage: options (2026-10-09)

Question (user, 2026-10-09): our model N already uses external weights as its initialisation
(ImageNet-22k ConvNeXt-tiny). At which other stages of our pipeline could external data, models,
labels or methods improve our results? This note merges two independent proposals: Claude's, and
Codex's (GPT-6 Astra, reasoning effort high, read-only, prompted without Claude's list), then checks
both against data. It is an options note for discussion, not a design: whichever option is chosen
gets its own design note and Codex review before GPU training (D-004).

Sources: `docs/STATUS.md` (versions, L1-L22), `competition.md`, `external-pretrained-2026-10-06.md`,
`public-landscape-2026-10-08.md`, `anchor-components-2026-10-06.md`; Kaggle dataset search
(2026-10-09); six public label datasets downloaded unchanged to `external/datasets/`; forum topic
743416 read in the browser (2026-10-09); `scripts/gold_label_sources.py` (new, analysis only); a
synthetic throughput benchmark on the local RTX 3080 Ti (random weights and inputs, no data).

## 1. Where external resources enter our pipeline today

| Stage | Now | External part |
|---|---|---|
| Labels / targets | `0.5 * mean(pilkwang, steven v2, lixin, dread) + 0.5 * v11 OOF` (N's target) | four public LLM label tables |
| Backbone initialisation | ConvNeXt-tiny `fb_in22k_ft_in1k` | ImageNet weights; MRI-CORE tried in v13 arm M (gold 0.881 vs N 0.920, dropped) |
| Base model (OAI pick) | v17: public CoAtNet-384 (OAI) + public ConvNeXt reader | both public checkpoints (D-019) |
| Training images | competition only | none |
| Preprocessing | own rules (140 mm centre crop, 320 px, laterality canonicalised) | none |
| Inference | K_infer 16, no TTA | none |

## 2. New facts checked today

### 2.1 Public report-label tables on gold-58 (`scripts/gold_label_sources.py`)

Paired bootstrap over the 58 studies (1,000 resamples) of each table against our 4-source soft target.

| Source (licence per dataset card or inventory) | Gold macro AUC | Gain vs 4-source soft (95% CI) |
|---|---:|---|
| Our round-2 target `0.5 soft + 0.5 v11` | 0.9235 | +0.032 (+0.017 to +0.046) |
| Our model N, 5 folds (image only) | 0.9198 | +0.028 (+0.003 to +0.056) |
| steven v4 blend (CC0) | 0.8927 | +0.001 (-0.005 to +0.007) |
| **Our 4-source soft target** | **0.8919** | - |
| karttikjangid05 consensus of public tables | 0.8886 | -0.003 (-0.014 to +0.007) |
| nartaa, Gemini 3 Flash re-read (CC0) | 0.8876 | -0.004 (-0.023 to +0.015) |
| steven v2 (CC0) | 0.8873 | -0.005 |
| Local open LLMs: Qwen-32B / Qwen3-8B / Mistral / MedGemma-27B | 0.886 / 0.880 / 0.879 / 0.879 | -0.007 to -0.013 |
| pilkwang (CC0, 57 rows) | 0.8700 | -0.023 (-0.038 to -0.007) |
| lixin, GPT-5.6-Sol (CC0) | 0.8352 | -0.056 (-0.076 to -0.036) |

Findings:

- **No single report-label table beats our 4-source mean** on gold. They all sit at 0.88-0.89, among them
  four open LLMs run locally by other participants (Qwen, Mistral, MedGemma). The gains come from mixing labels with
  an image model's out-of-fold predictions (round-2 target 0.9235), which is STATUS L4 and L9-L17 again.
  So running our own LLM over the reports, or adding more voters, is unlikely to move the target on its
  own.
- **The Gemini table is complementary per finding**: it is better than our mean on PF OA (0.934 vs 0.903),
  Fracture (0.903 vs 0.815), Lateral OA, MCL, ACL; worse on Medial Meniscus, Effusion, Contusion, Baker's.
  Added as a fifth equal-weight source (weight 0.2, the pre-specified variant), the round-2-style target
  goes from 0.9235 to **0.9269 (+0.0035, CI -0.0007 to +0.0079, P(gain <= 0) 0.048)**; weights 0.33 / 0.5
  give +0.0045 / +0.0052 with wider intervals (post hoc, not to be selected on gold).
- Author's text (nartaa dataset card, not verified): with the same CoAtNet recipe on fold 0, gold
  0.888 when trained on steven v4 labels and 0.904 when trained on the Gemini labels or their blend.
- Gold has now been used for selection many times (STATUS L3, L13); these are screens, not proofs.
- Not evaluable on gold: JEV labels (`riadmohamed42/jev-knee-labels`, CC0) are tuned on gold per the
  karttikjangid05 inventory; dread has no gold rows.

### 2.2 Public training assets for the CoAtNet recipe (non-OAI)

- `nartaa/rsna-knee-hpo-assets` (CC0): `train_knee.py` (the CoAtNet/ResNet trainer with per-finding
  attention pooling over three-slice windows; fold or all-data training, fp16/bf16), 5 folds, the Gemini
  label tables. Read as data only; the script has not been run or reviewed in detail.
- `dreaddevelopment/knee-raptor-corpus` + `-ext` (CC0): preprocessed stacks for all 4,407 studies, but in
  the older layout (44 slices at 336 px, 15.9 + 6.0 GB), not the 96-slice 384 px layout of the 0.949
  checkpoint.

### 2.3 External-data rule status (forum topic 743416, read 2026-10-09)

Still **no host answer**. About 14 hours before reading, a participant posted a reply from the NIMH Data
Archive about OAI's intended accessibility, and the topic author (ranked 10th) wrote that OAI now seems
"reasonable to consider" permissible. A participant reports that fastMRI requires an application with
institutional affiliation; another quotes MRNet's no-derivative-works clause; earlier posts report NIH
country restrictions for OAI. These are participants' claims, not rulings. KneeCoT stays prohibited
(host).

### 2.4 Local cost of a CoAtNet (synthetic benchmark, fp16, one study per step)

| Backbone at 320 px | Windows per step | Train img/s | Peak GPU memory |
|---|---:|---:|---:|
| ConvNeXt-tiny | 20 | 279 | 2.9 GB |
| CoAtNet-rmlp-2-rw, gradient checkpointing | 16 / 24 | 56 / 59 | 4.7 / 6.8 GB |
| CoAtNet-rmlp-2-rw, no checkpointing | 16 | 68 | 8.5 GB |

Inference about 265 img/s. Estimates: one CoAtNet fold in our v13 pipeline (about 1.04 M training images)
about 6 h including evaluation; a 3-epoch all-data fine-tune of the public checkpoint about 1 h. Kaggle
T4s are too slow for CoAtNet training; training stays local (D-016).

## 3. Options, stage by stage

C = proposed by Claude, X = proposed by Codex. Costs are planning estimates. "Pick" = which final
selection it can help: OAI (v19 line) or hedge (v15 line, non-OAI).

| ID | Stage | What | Evidence for / against | Rule risk | Cost | Pick | First check |
|---|---|---|---|---|---|---|---|
| E1 (C) | Labels | Add the Gemini table (CC0) to the round-2 target as a fifth source (T3 = `0.5 * mean(5 sources) + 0.5 * v11 OOF`) | For: +0.0035 on gold (2.1), complementary findings, author's +0.016 student result. Against: gold reused; the public CoAtNet trained on Gemini-derived labels, so our student moves towards the base (correlation up) | none (CC0, LLM labels allowed by host) | CPU minutes; then one N fold, 2.5 h local | hedge mainly; OAI pick only if it also decorrelates | one N fold 0 on T3 vs N fold 0 (gold 0.920, LB 0.934 as v14), then a fold-0 LB check |
| E2 (X) | Labels | Targeted LLM adjudication of cells where the tables and v11 OOF disagree (evidence span, compartment, status), freeze the spec on non-gold reports, change only unreliable cells or their weights | For: label noise is the measured bottleneck (L4). Against: 2.1 shows single LLM tables (API or local) cap at 0.88-0.89; a new read must beat a 4-6-table mean; the user declined option L on 2026-10-06 (API spend) | none | 1-2.5 days + API cost or local-LLM GPU time | both | audit 100-200 non-gold disagreements first; stop if no systematic error |
| E3 (X) | Auxiliary supervision | Extra report-derived targets (tear location, severity, compartment) or a report-embedding prediction loss as training-only heads | For: richer supervision without test-time reports (ConVIRT-style precedent). Against: untested here; small data; may learn report style | none | 2-3 days, 15-25 GPU h | both | one fold with vs without auxiliary loss, same primary target |
| E4 (C, X) | Backbone / recipe | Our own CoAtNet-rmlp-2 (ImageNet-12k init, no OAI) on our target, single-factor swap in the v13 pipeline; the public CC0 trainer and corpus (2.2) are a fallback recipe | For: the CoAtNet family leads this competition; the author reports 0.942 without OAI. Against: same family as the base (correlation); 6 h per fold | none | fold 0: 6 h local; 5 folds about 30 h | hedge; small leg for OAI pick | fold 0 alone on LB (threshold to set in the design, e.g. >= 0.940) |
| E5 (C, X) | Public weights | Short low-LR adaptation of the public OAI CoAtNet on our target (keep its input pipeline; protect the OAI-supervised findings by self-distillation), used as a replacement, not a leg | For: starts from 0.949; high correlation is acceptable for a replacement. Against: no honest validation (it was trained on all studies), may erase OAI signal (L21: our target's extra information may be small) | inherits D-019 risk | Stage 0 compatibility check about 1 h; 1-2 h per run | OAI | gold paired vs the untouched checkpoint on the same pipeline, then one frozen LB comparison |
| E6 (X) | Ensembling | Replace the public ConvNeXt reader by N inside the v17 fusion (v19/v20 added N outside the fusion) | For: N alone 0.936 vs reader 0.929; one frozen test. Against: L21 (gold understates redundancy); expected gain below 0.001-0.002 | none beyond D-019 | v18 gold diagnostic, 1 submission | OAI | v18 gold diagnostic, then one submission |
| E7 (X) | Inference | Anatomical mirror TTA for N (method of the public notebook) and denser coverage | For: mirror gave the author +0.001; K4 -> K16 +0.021 (L6). Against: K16 -> K24 +0.001; N was trained without flips | none | 0.5-1 day | both | paired gold check of N with and without the mirror view |
| E8 (X) | Preprocessing | ROI recentring or a local crop from an external knee segmenter (e.g. SKM-TEA models) | For: 28% of series oblique, crop position never ablated. Against: no observed crop failure; laterality agrees 98.6% (L5); segmenter provenance and qDESS-to-clinical transfer unclear | depends on the segmenter's training data | 2-4 days | both | visual audit of 50-100 studies first |
| E9 (X) | Distillation | Use public models' predictions as a teacher | Against: the strong teacher has no honest training-set OOF; public OOF teachers are weaker than ours (anchor-components 4); OAI teacher makes the student OAI-derived | OAI-derived if the CoAtNet is the teacher | 1-2 days | - | not proposed |
| E10 (C, X) | Extra labelled images | OAI, fastMRI+, MRNet, SKM-TEA, KneeMRI with masked per-dataset labels | For: external data helped in other RSNA competitions (forum). Against: no host ruling (2.3); fastMRI needs an institutional application, MRNet forbids derivatives, KneeMRI is ND, SKM-TEA is small, OAI is gated and reported as blocked in some countries; ACL-only data barely moves macro AUC (+0.01 on one label = +0.0008) | high / unresolved | 3-6 days plus access delays | - | only after a host ruling |
| E11 (X) | Self-supervised | SSL continuation on knee MRI (competition images first) | Against: deadline; MRI-CORE did not help (arm M) | none for competition images | 50-150 GPU h | - | not proposed |
| E12 (X) | Past recipes | Single changes from RSNA 2024 Lumbar Spine solutions (sequence pooling, augmentation, weight averaging), one at a time | For: similar task structure. Against: generic gains are usually below noise; a detector + specialist rebuild does not fit | none (licences of copied code) | 1-2 days each | both | one change vs N fold 0 |

## 4. Ranking and where the two proposals differ

Codex's top five by value per day: E6, E5, E2, E4, E7; one substantial training direction at a time;
stop large experiments by about 2026-10-18/19.

Claude's view after the data in 2.1:

- **E1 moves ahead of E2.** E2 assumed systematic extraction errors that a new LLM read could fix; the
  table shows that the strongest available reads (Gemini 3 Flash, GPT-5.6, local 8-32B models) each score
  below our existing mean, so a new read is unlikely to help unless it targets specific cells. E1 already
  has a measured, if borderline, signal at no labelling cost. E2 stays as a later option.
- **E1 is a target change, so it should be used by whatever model is trained next** (N fold 0 as the
  single-factor test, then E4 and E5 if it holds). Caveat: the public CoAtNet's training labels include a
  Gemini blend, so E1 may increase correlation with the base; it is primarily a hedge-pick lever.
- Agreed with Codex: E6 is a cheap check (sub-noise expected); E5 is the only option that can raise the
  OAI pick directly; E4 is the main route to a better non-OAI hedge; E8-E11 are not worth the time now.

Proposed shortlist for discussion (each needs a design note and Codex review before GPU use):

| Order | Option | GPU (local) | Submissions | Decision it informs |
|---:|---|---:|---:|---|
| 1 | E6 reader substitution | 0 | 1 | whether N has any use in the OAI pick |
| 2 | E1 target T3, N fold 0 | 2.5 h | 1 | whether T3 replaces the round-2 target for all later models |
| 3 | E5 public CoAtNet adaptation (after Stage 0) | 2-4 h | 1 | whether the OAI pick can rise above 0.950 |
| 4 | E4 own CoAtNet fold 0 (target per item 2) | 6 h | 1 | whether a non-OAI CoAtNet beats N (go / no-go for folds 1-4, about 24 h) |
| 5 | E7 mirror TTA for N | < 1 h | 0-1 | small gain for both picks |

Total about 12 h of local GPU and five submissions over two days before any five-fold run.

## 5. Not recommended now

- Own LLM relabelling by voting more models (2.1), unless E2's audit finds systematic errors.
- Training on OAI or other gated or ND-licensed knee datasets ourselves (2.3; no ruling, access delays).
- Another foundation-model backbone search (MRI-CORE result, v13 arm M).
- Distilling public models (E9), blend-weight or calibration sweeps on the public LB, more N folds or seeds
  (L13, L18, L21).
- Per-finding source selection on gold (nartaa reports that its per-label pick did not beat the blend).

## 6. Codex input: claims checked

| # | Codex claim | Verified? | Outcome |
|---|---|---|---|
| 1 | v19/v20 add N outside the v17 fusion, so replacing the reader is an untested question | Yes (v19 design: outer rank blend) | Accepted as E6 |
| 2 | K16 -> K24 gave only about +0.001; N was trained without flips | Yes (STATUS ledger: 0.871 -> 0.872; augmentation "no flip") | Accepted (E7 expectation below 0.001) |
| 3 | Adding more label voters is likely below 0.001-0.002 in the final ensemble; targeted adjudication has a better rationale | Partly: 2.1 confirms single tables do not beat the mean; the Gemini table still adds +0.0035 to the round-2 target on gold | Accepted with change: E1 (one complementary table) ahead of E2 |
| 4 | Fine-tuning the all-data public checkpoint cannot be validated on our folds; gold is selected, LB is the external check | Yes (checkpoint name `alldata`; author: gold used for selection) | Accepted (E5 gates) |
| 5 | A 0.01 gain on one label adds 0.00083 to macro AUC | Yes (0.01 / 12) | Accepted (argues against ACL-only datasets) |
| 6 | "About 1,300 test studies" refers to the hidden test set, not the public split | Yes (`competition.md`) | Accepted: the 0.001-0.002 noise band is a working assumption |
| 7 | fastMRI+ repository is MIT-licensed; images need a separate agreement (earlier survey said CC BY) | Not verified | Open; irrelevant while E10 is not pursued |
| 8 | SKM-TEA publishes segmentation models usable for localisation | Not verified | Open; only relevant if E8 is chosen |

## 7. Decisions for the user

1. Which options to take into a design note (shortlist in section 4, or a subset).
2. E2 / option L: still declined, or reopen (API key and spend, or local LLM time on the GPU)?
3. E10: keep external image datasets out until the host rules (recommended), given the forum status.
