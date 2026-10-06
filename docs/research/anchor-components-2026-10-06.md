# Anchor (v05) components on gold: public member predictions

Date: 2026-10-06. Question (user): what can we learn from the v05 public stack to use in our
own models and blends? Several anchor members publish predictions next to their weights. This
note records the files, whether they are honest (not trained on the scored studies), and what
they show. Script: `scripts/anchor_proxy_gold.py` (inputs in `external/datasets/`, not tracked).

## 1. Files

| Anchor member | Dataset (licence per baseline-selection.md) | File | Coverage | Honest? |
|---|---|---|---|---|
| DINOv2-S x20 (5 folds x 4 seeds, 336 px, 12 slices) | `pilkwang/rsna-knee-weights` (CC0) | `oof.npz`, `manifest.json` | all 4,407 studies, out-of-fold | Very likely: the `pilkwang/rsna-knee-baseline-v1` trainer holds out report-hash group 0 (`md5(report) % 5`) and trains gold studies at weight 3.0 otherwise (verified in that notebook); the weights dataset comes from a separate 5-fold run (`manifest.json`: fold 0-4, 4 seeds each), not traced in code. OOF gold 0.840 matches the members' recorded holdout (mean 0.840) and gold check (mean 0.837), which would be far higher if the OOF were in-sample |
| RadImageNet ResNet-50 heads E9 / E11 | `antoinegg1/rsna-knee-e9-radimagenet-heads-v15`, `...-e11-diverse-heads-v20` (CC BY-NC-SA 4.0) | `v52_oof.csv`, `v52_e11_oof.csv` | all 4,407 studies, 5 folds of about 881 | Assumed (out-of-fold by name and fold column; not traced in code) |
| CoAtNet "resgated" top 3 | `mattiaangeli/rsna-knee-coat-resgated-ep10-top3` (CC0) | `gold58_top3_predictions.npz` | 58 gold studies | Not trained on gold, but checkpoints selected on gold (optimistic) |
| CoAtNet global96 top 3 | `mattiaangeli/rsna-knee-coatnet-global96-top3` (CC0) | `coatnet_global96_gold58_reference.npz` | 58 gold | Trained on the 4,349 report studies; gold used only as the "sole model selector" (top 3 of 24 epochs by gold macro AUC, verified in the manifest and training history) |
| CoAtNet d4 | `mattiaangeli/rsna-knee-coatnet-d4-depthzone-swa3-b2` (CC0) | `d4_gold58_reference.npz` | 58 gold | Same author and package style; selection not traced |

All five files use the official label order and the same gold truth as ours (checked).

## 2. Gold-58 macro AUC

| Model | Gold |
|---|---:|
| DINOv2 x20 (OOF) | 0.840 |
| RadImageNet E11 / E9 (OOF) | 0.826 / 0.854 |
| CoAtNet resgated / global96 / d4 (gold-selected) | 0.912 / 0.931 / 0.930 |
| Our v08 5-fold / v11 5-fold | 0.897 / 0.913 |

The anchor's public DINOv2 and RadImageNet members are weaker than v11 on gold (pilkwang's
DINOv2 baseline scored 0.891 on the public LB), and the CoAtNet members are probably near v11's
level once their gold selection is discounted. Hypothesis (no member ablation): the anchor's
strength comes from combining different families.

## 3. Proxy anchor and what our legs add

Proxy = rank blend of the public members. Main variant (CoAtNet-heavy): DINOv2 0.5,
RadImageNet E9 0.5, CoAtNet resgated 1.0, global96 1.5, d4 1.5; proxy gold 0.930. Paired
bootstrap (2,000 resamples of the 58 studies) of the gain from adding a leg in rank space:

| Leg | w 0.10 | w 0.20 | w 0.30 | w 0.45 |
|---|---:|---:|---:|---:|
| v08 5-fold (gold 0.897) | -0.000 | -0.002 | -0.004 | **-0.010** (CI -0.019 to -0.001) |
| v11 5-fold (gold 0.913) | -0.000 | +0.001 | -0.001 | -0.002 (CI -0.008 to +0.004) |

The v08 row reproduces v09 on the public LB (w 0.45: -0.011). This is one calibration point and
the proxy weights were chosen with it in view. Two further frozen variants (Codex re-review,
2026-10-06) change the verdict on v11 at w 0.30: equal weights for the five members +0.0028,
CoAtNet members only -0.0012. The proxy omits anchor parts without public predictions (A5,
Raptor, other CoAt readers) and the anchor's per-label weights. It is therefore a diagnostic,
reported for all three variants, and never a veto.

## 4. Use for our work

- **Not as a teacher.** The members with training-set OOF are weaker than our own v11 OOF
  (pooled AUC against the soft target 0.851 vs 0.875); the strong CoAtNet members only publish
  gold predictions; distilling the anchor would also raise correlation with it.
- **As a diagnostic before costly submissions:** report a candidate leg's proxy gain on gold for
  the three frozen variants (`scripts/anchor_proxy_gold.py`); no variant can block a submission
  (design v13 revision 3).
- **For diversity:** the anchor's families are ImageNet-DINOv2, RadImageNet ResNet-50 and
  CoAtNet; a second own model should come from a different family or pretraining domain.
