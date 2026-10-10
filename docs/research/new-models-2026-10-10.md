# New models, methods and pretrained transfer after the shortlist (2026-10-10)

Question (user, 2026-10-10): with the new Kaggle quota (30 GPU h until 2026-10-17), which new models
or methods could we try, and which pretrained models could we transfer from? Prepared with Codex
(GPT-6 Astra, high, read-only; independent proposal) and checked against data. Options note for
discussion; any GPU training still needs a design note and Codex review (D-004).

## 1. What the shortlist taught (STATUS L23-L26)

- Every own model built on our pipeline is redundant with the public base: N ties or loses in three
  fusion configurations (v19 0.950, v20 0.949, v21 0.949), an own CoAtNet in the same pipeline is a
  near copy of N (v24: Spearman 0.95 on gold, 0.94 on validation), a fifth label source leaves the
  student unchanged (v22), adapting the public CoAtNet to our target lowers gold (v23).
- Standalone strength and gold-58 do not predict a partner's value for this base (L20, L26). The only
  decisive test is the public score of the complete ensemble.
- The public reader (0.929 alone) does add to the CoAtNet; our N (0.936 alone) does not.

## 2. Verified facts behind the options

**The public reader is a different pipeline, not just a different ConvNeXt** (code read: v17 cells
and `goodpjw2008/rsna-knee-2-5d-convnext-reader`, Apache 2.0, training code included):

| Component | Public CoAtNet | Public reader | Our N |
|---|---|---|---|
| Field of view | 116.7 mm (384 raster, 320 crop) | about 141 mm (0.4 mm/px, 153.6 mm cache, 0.92 crop) | 140 mm at 320 px |
| Series slots | 5, first unused match | 6: three planes x fat-suppressed or not; random series per slot in training | 5 |
| Study aggregation | per-finding attention MIL | slot + slice-position embeddings, **2-layer transformer over all windows**, per-finding attention | slot embedding + gated per-finding attention |
| Training target | own report labels + JEV/steven/pilkwang + OAI masked labels | **mean of 4 public report tables (steven v4, pilkwang, lixin, qwen); no image teacher** | 0.5 x 4 report tables + 0.5 x v11 OOF (teacher) |
| Other | SWA, mirror TTA | EMA, 3 of 5 folds released | 5 folds |

**Gold similarity to the public CoAtNet** (residual correlation of probit ranks within class, gold-58):
reader 0.791, v08 (report labels only) 0.799, v11 (one teacher round) 0.809, N (two rounds) 0.820,
v24 C 0.805. Each teacher round moves our model slightly towards the CoAtNet. Weak evidence (gold
understated the LB correlation, L21), but it is consistent with the hypothesis that the image-teacher
half of our target is what makes N redundant.

**Pretrained weights checked on the Hugging Face hub (2026-10-10):**

| Model | Access | Licence |
|---|---|---|
| DINOv3 via timm (`convnext_tiny/small/base.dinov3_lvd1689m`, `vit_base_patch16_dinov3.lvd1689m`) | **not gated** (the `facebook/dinov3-*` repos are gated) | DINOv3 licence ("other") |
| DINOv2 (`metaresearch/dinov2` on Kaggle Models, timm) | public | Apache 2.0 |
| MedSigLIP-448 | gated (HAI-DEF terms); 878 M parameters with the text tower | other |
| BiomedCLIP ViT-B/16 | public | MIT |
| VideoMAE-B | public | CC BY-NC 4.0 |
| ConvNeXt-V2 (timm FCMAE) | public | CC BY-NC 4.0 |
| MaxViT-T, EfficientNet-V2 (timm) | public | Apache 2.0 |

Codex additionally lists torchvision video models (R(2+1)D, MViT-V2), X3D (PyTorchVideo), MedicalNet
(MIT), SAM-Med3D (Apache 2.0) and MARS (Apache 2.0 per its current repository; weight terms and data
ancestry not audited). Codex stated that DINOv3 needs an access agreement; that holds for the
`facebook/` repos only, not for the timm copies (checked).

## 3. Options

| ID | Option | Why it could complement the base | Cost | Rule / licence | First decisive test |
|---|---|---|---|---|---|
| I1 | **Public CoAtNet through two preprocessing paths**: exact pipeline + our v07 adapter, probability mean, reader and TW unchanged | adapter output is a different view of the same strong model (gold 0.9255 vs 0.9228, Spearman 0.984) | no training; leg engineering about half a day; extra hidden-test inference about 0.5-1 h | inherits D-019 | gold diagnostic of the fused output, then one LB check |
| I2 | **Public CoAtNet-224 checkpoint** added at a fixed small weight (90/10 with the 384 model) | separately trained (224 crop, own SWA epochs; 0.945 alone) | no training; download 293 MB; extra inference about 0.1-0.4 h | same OAI terms | one LB check; a public triple-reader at 0.950 is not an ablation |
| T1 | **N recipe on a report-only target** (no image teacher; the reader's 4 tables or ours) | tests the teacher-redundancy hypothesis above; reader-like supervision | local fold 0 about 2.5 h | none new | v17 + T1 at a fixed small weight (one LB check) |
| T2 | **Ordered slice-sequence head** (GRU or small transformer with slice positions) on cached N fold-0 features, then a short fine-tune | the reader's main architectural difference; N has no inter-window context | local 1-2 h screen, 2-4 h fine-tune | none | same blend check |
| T3 | **Self-supervised ViT probe**: DINOv3-S/B (timm, ungated) or DINOv2-S on 2.5D windows with the sequence head | different pretraining objective | Kaggle 4-5 h probe, 8-10 h bounded fold | DINOv3 licence or Apache 2.0 | frozen-feature probe, then one fold and a blend check |
| T4 | **3D / video model per series** (X3D-S or R(2+1)D-18; MedicalNet) | through-plane modelling, a genuinely different bias | Kaggle 8-20 h per fold plus 1-2 days of engineering | Kinetics / MIT weights | memory and throughput pilot first; reserve option only |
| R1 | **Reproduce the reader recipe** (its public training code) for its missing folds 3-4 or with another backbone | the component known to help | needs its 0.4 mm/px cache of every series (about 100 GB uint8) rebuilt from DICOM on Kaggle; about 1 day of engineering | Apache 2.0 | not proposed now: cost; and the reader already supplies this diversity |

Not proposed (agreed with Codex): more N seeds or folds, plain backbone swaps (v24), more label voters
(v22), more adaptation of the public CoAtNet (v23), MedSigLIP / VideoMAE / SAM-Med3D / MARS full
adaptation before a cheap viability test, test-time training or pseudo-labelling inside the
submission (rule not verified), LB weight sweeps.

## 4. Proposed order and budget

1. **I1 and I2** first: no training, about 1-2 local GPU h for diagnostics, two submissions.
2. In parallel, **T1** (local, 2.5 h) and **T2** (local, up to 2 h for the screen) as cheap tests of the
   two hypotheses that distinguish the reader from N (supervision, sequence context).
3. **T3** on Kaggle only if a cheap test shows any partner value, within about 15 h of this week's
   quota; keep 10-15 h in reserve (commit runs, a possible T4 pilot).
4. No new architecture after 2026-10-17; large experiments stop 2026-10-19.

Decision rule to settle with the user: the shortlist kept final adoption at +0.002 (0.952). With the
silver line at 0.951 (rank 282 on 2026-10-10) and the 0.950 block growing about 150 teams a day, a
displayed 0.951 would justify further work but is not proof of a private-set gain.

## 5. Codex's overall view

Codex (and this note) consider a team merger before 2026-10-15 with a team whose models come from a
different pipeline the most likely way to gain +0.001-0.002 now; no option above has evidence strong
enough to promise that. The merger is the user's decision.
