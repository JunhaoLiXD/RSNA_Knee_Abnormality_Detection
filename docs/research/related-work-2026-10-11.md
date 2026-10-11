# Related work: past RSNA Kaggle winners and knee MRI papers (2026-10-11)

Status: survey for discussion (user request 2026-10-11: look for related papers and past Kaggle gold solutions for
inspiration, no full reproduction required). No decision; any idea below that needs GPU training gets a design note
and a Codex review first (D-004). Evidence cited from STATUS: L6, L10, L17, L20, L21, L23, L26, L27, L30; earlier
surveys `external-pretrained-2026-10-06.md` (external datasets and weights, rules) and `external-levers-2026-10-09.md`
(E12 "past recipes" listed there, not pursued).

Claims about other solutions are the authors' text (not verified in their code). Writeups were fetched with the
nvidia-kaggle writeups workflow into `external/writeups/<competition>/` (not tracked).

## 1. Sources read

| Competition (task) | Writeups read | Why similar |
|---|---|---|
| [RSNA 2024 Lumbar Spine Degenerative Classification](https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification) (multiplanar MRI, per-level severity) | [1st](https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/writeups/avengers-1st-place-solution), [2nd](https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/writeups/ianpan-kevin-yuji-bartley-2nd-place-solution), [3rd](https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/writeups/sonyspine-s-tkmn-moyashii-3rd-place-solution), [4th](https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/writeups/spine-chart-4th-place-solution), [5th](https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/writeups/two-people-5th-place-solution) | Same modality and structure: sagittal T1/T2 + axial series, several findings per study, left/right structures, noisy labels |
| [RSNA 2025 Intracranial Aneurysm Detection](https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection) (CTA/MRA/MRI, 13 locations + presence, AUC) | [1st](https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/writeups/1st-place-solution), [2nd](https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/writeups/2nd-place-solution), [3rd](https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/writeups/3rd-place-solution), [4th](https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/writeups/4th-place-solution), [6th](https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/writeups/6th-place-solution) | Multilabel AUC metric, heterogeneous series, left/right paired labels, 2 x T4 runtime limits |
| [RSNA 2023 Abdominal Trauma Detection](https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection) (CT, organ injuries) | [1st](https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection/writeups/team-oxygen-1st-place-solution-team-oxygen), [2nd](https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection/writeups/on-strike-2nd-place-solution) | Study-level labels from volumes, 2.5D + sequence models |
| [RSNA 2022 Cervical Spine Fracture Detection](https://www.kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection) (CT, per-vertebra) | [1st](https://www.kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection/writeups/qishen-ha-1st-place-solution), [2nd](https://www.kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection/writeups/rawe-2nd-place-solution-segmentation-2-5d-cnn-gru-) | Localise -> crop -> 2.5D + RNN |

## 2. Recurring patterns in the winning solutions and where we stand

| Pattern | Who (authors' claims) | Our status |
|---|---|---|
| **Localise, then crop the region of interest**, classify the crop | Lumbar 1st-5th (keypoints / instance number, crops per level); aneurysm 1st-3rd (vessel ROI); abdominal 1st-2nd (organ crops); cervical 1st-2nd (vertebra crops) | Only in the public **S6** (SKM-TEA anatomy-anchored views; our anchor v32/v33). Our legs use a fixed field (140 mm) plus a fixed central 100 mm view (v26 crop, v29 native) |
| **2.5D CNN + aggregation over slices** (attention MIL, BiLSTM/GRU, transformer) | Lumbar 1st (attention MIL: LB loss 0.37 -> 0.35; + BiLSTM, aux losses and ensembling 0.33), 4th, 5th; abdominal 1st-2nd (GRU/LSTM); cervical 1st-2nd | We have 2.5D triplets with gated per-finding attention over unordered tokens (v08 design). Lumbar 3rd found 2D CNN + LSTM and 3D CNN worse than slice attention |
| **Share one model across paired structures, flip to align** (data x2 to x10) | Lumbar 3rd: one "side classifier" for left and right, right side flipped, plus level-agnostic training; aneurysm 2nd: left-right flip with label swap (with 8x TTA +0.0097 public over 4x TTA in their ablation); aneurysm 6th: flip that also flips targets (about +0.01 CV) | **Not used**: our trainer has no flips (v08 augmentation list). Four of our 12 labels are medial/lateral pairs (Medial/Lateral Meniscus, Medial/Lateral OA); Lateral Meniscus and Lateral OA are among our weakest findings (v08 OOF 0.813 / 0.783; v26 vs N on gold -0.039 / -0.037) |
| **Mixing regularisers** (CutMix p up to 1.0, Mixup) | Lumbar 5th (largest augmentation gain); abdominal 2nd (CutMix p 0.5-1.0); aneurysm 6th (about +0.01 CV) | **Not used**. v11 B shows a train/validation gap (L10) |
| **Label-noise handling with OOF** | Lumbar 2nd: drop samples with abs(label - ensemble OOF) >= 0.8, about +1% LB; lumbar 3rd: manual relabelling, soft pseudo-labels | N's target is `0.5 soft + 0.5 OOF teacher` (L17: +0.007 gold); v26/v29 report-only. LLM audit (llm-labels section 9): disagreements are mostly definitions, gold is image-read |
| **Auxiliary segmentation / location losses** | Abdominal 1st (+0.01-0.03); aneurysm 1st (aux sphere loss, ablation 0.876 -> 0.902) | None (no masks); S6 uses anatomy for views, not as a loss |
| **Small backbones, short training** | Lumbar 1st (ConvNeXt-small > base > large; 7-14 epochs); lumbar 3rd (long epochs did not help) | Consistent with ours: ConvNeXt-tiny; own CoAtNet no better (L27); 15 epochs flat after 9 (L10) |
| **Stacking** across models / labels | Lumbar 4th (MLP and LightGBM stacking) | Not feasible for the anchor: CoAtNet and S6 have no honest training-set OOF (CoAtNet trained on all data and gold-selected) |
| **Robust fallbacks** under 2 x T4 limits | Aneurysm 1st (OOF-mean fallback), 2nd (cut ensemble to fit 9 h) | v33/v35: any leg failure keeps the anchor (v32 design section 8) |

## 3. Papers

| Paper | What | Relevance to us |
|---|---|---|
| [MRNet](https://doi.org/10.1371/journal.pmed.1002699) (Bien et al., PLOS Med 2018) | 1,370 knee exams; per-plane AlexNet, max pooling over slices, logistic-regression late fusion; ACL, meniscus, abnormal | Baseline only; our design (all planes jointly, attention per finding) is beyond it |
| [ELNet](https://arxiv.org/abs/2005.02706) (Tsai et al., MIDL 2020) | Lightweight CNN from scratch, single stack | Not useful now |
| [MRPyrNet](https://github.com/matteo-dunnhofer/MRPyrNet) (Dunnhofer et al., MIDL 2021 / CMIG 2022) | Feature pyramid + pyramidal detail pooling around the image centre for small structures (ACL, meniscus) | Same motivation as our local views (v26/v29): small structures need more resolution near the joint |
| [Astuto et al.](https://pubs.rsna.org/doi/10.1148/ryai.2021200165) (Radiology: AI 2021) | Hierarchical 3D CNNs: localise, then detect and grade cartilage, bone marrow, meniscus and ACL lesions | Localise-then-classify again; bone marrow oedema hardest (sensitivity 43-54%), consistent with our Contusion difficulty |
| [fastMRI+](https://arxiv.org/abs/2109.03812) (Zhao et al., Sci Data 2022) | 16,154 bounding boxes, 22 knee pathology categories on fastMRI | Could supervise localisation; images under the fastMRI agreement, no host ruling (external-pretrained 2026-10-06) |
| [OrthoDiffusion](https://arxiv.org/abs/2602.20752) (2026), KneePreM (arXiv 2609.31461), [OrthoFoundation](https://arxiv.org/abs/2601.18250) (2026), [SB-SSL](https://arxiv.org/abs/2208.13923), [SKID](https://arxiv.org/abs/2104.10481) | Knee / MSK self-supervised foundation models; OrthoDiffusion: 3 orientation-specific models, 15,948 scans, 8 abnormalities | No usable public weights established; OrthoFoundation `best.pt` excluded (D-023); our MRI-CORE test was weak (arm M gold 0.881, STATUS v13) |
| [Rep-GLS](https://arxiv.org/abs/2508.02495) (2025), [Liu et al.](https://arxiv.org/abs/2103.04053) (2021) | Label smoothing driven by report uncertainty; noisy-label training for NLP-extracted multilabel CXR | Our soft targets already encode report uncertainty; the LLM label branch is stopped (D-025 follow-up) |

Paper-level work on knee MRI is mostly two or three labels on MRNet-sized data; the Kaggle writeups are the more
useful source for a 12-label, multiplanar, AUC-scored setting.

## 4. Candidate ideas for us, ranked

All are changes to our own leg, which enters the anchor at weight 0.15. STATUS L20, L21, L26 and L30: our legs add
at most about +0.001 to the public anchor, and gold-58 has misranked legs three times, so each idea needs an LB test
and the planning expectation stays small. Time: large experiments stop 2026-10-19 (D-021); one B2 fold takes about
4.7 h on the local GPU; v35 and the D-026 probes compete for submission slots.

| # | Idea | Source | For | Against | Cost |
|---|---|---|---|---|---|
| R1 | **Medial/lateral flip with label swap** in the B2 trainer: with p 0.5 flip coronal and axial tokens horizontally, reverse the sagittal slice order, swap Medial<->Lateral Meniscus and OA targets, mask MCL (no lateral twin) on flipped samples; optional flip TTA at inference | Lumbar 3rd, aneurysm 2nd and 6th | Doubles the evidence for 4 of 12 labels, two of them our weakest; v07 is canonical (verified in its code: coronal/axial columns point medial, sagittal slices are ordered towards medial), so the flip is an index operation | Knees are not mirror-symmetric (fibula, LCL, meniscus shapes): flipped knees are anatomically impossible, unlike roughly symmetric brain vessels or spine sides; MCL masked on half the samples; leg-value ceiling (L21, L26) | trainer change, fold 0 about 4.7 h, one LB slot |
| R2 | **Study-level Mixup / CutMix** of token sets with mixed soft targets | Lumbar 5th, abdominal 2nd, aneurysm 6th | Most-cited regulariser among winners; v11 B over-fits after epoch 9 (L10) | Generic gains are usually small (E12 note); MIL over slices makes CutMix label areas ill-defined (Mixup is cleaner) | trainer change, fold 0 |
| R3 | **OOF-guided down-weighting** of report-target cells where the soft label and our OOF ensemble disagree strongly (e.g. >= 0.8) | Lumbar 2nd | Cheap target change; teacher signal helped once (L17) | L23: target edits barely move the student; the LLM audit found definition differences, not errors; overlaps the queued dread ablation | target change, fold 0 |
| R4 | **Ordered slice aggregation** (BiGRU over each slot's slices before attention pooling) | Lumbar 1st/5th, abdominal, cervical | Uses slice order, which our pooling ignores | Lumbar 3rd: LSTM variants worse; architecture change, new failure modes | model change, fold 0 |
| R5 | **Anatomy masks** (SKM-TEA `anatomy.pt`) for compartment crops or an auxiliary loss | Aneurysm 1st, abdominal 1st, S6 | Strongest pattern overall | Our version would be close to S6, already in the anchor (redundancy, L21); D-023 accepted `anatomy.pt` for S6 only; mask generation for 4,407 studies; too large for the time left | days |
| - | Not recommended: 3D CNNs, larger backbones, longer training, cross-label stacking of the anchor | Lumbar 1st/3rd, cervical 1st; our L10, L27 | - | - | - |

## 5. Suggested next step (for discussion)

R1 is the only idea that is specific to this dataset's label structure and cheap to test. If the user wants it, the
order would be: write a design note (exact flip mapping per plane, MCL masking, TTA, frozen comparison against v29
fold 0 and a single LB test as a leg on the incumbent), Codex review, then one B2 fold 0 run after v35 (in place of,
or after, the dread ablation, whose expectation is near zero). R2 could be folded into the same run only by giving up
attribution; one factor at a time is the house rule for single-fold tests.
