# Public notebooks: update 2026-10-10

Follow-up to `public-landscape-2026-10-08.md`. Sources: `kaggle kernels list --sort-by scoreDescending`,
the competition Code page sorted by public score (read in the browser, 2026-10-10 ~13:00 UTC; it shows
each notebook's best public score), nine notebooks pulled to `external/kernels/` with metadata, dataset
metadata, README and receipt files of the heliosli datasets. Authors' text is marked as such.

## 1. Verified scores (Code page, sorted by public score)

| Public LB | Notebook | Components |
|---:|---|---|
| **0.954** | heliosli/blend-mine-in-private-lb-luck-to-all-upvoters (2026-10-08) | public OAI CoAtNet-384 (0.7) + heliosli "S6" compact ConvNeXt-small, 4 folds, arm `E_lrprior`, bundle `209a32c8b50a6b1c` (0.3); per-finding rank blend, weights fixed |
| 0.951 | evgendvorkin/rsna-versia-7, heliosli/rsna-knee-blend-gold, jenillangaliya dual-stage, kiyoshiohno template, samanyu1808 blend3 | the same CoAtNet + S6 at 0.7 / 0.3 with the older bundle `c7ebab1eb953f1a6`; blend3 adds the goodpjw2008 reader |
| 0.950 | many (v17-type CoAtNet + reader, DINOsaur V5, D4, triple reader, ...) | unchanged since 2026-10-08 |

Notebooks titled "0.954" by rabari9999 and two copies (emresariduman, sameerk2004) combine CoAtNet-384,
CoAtNet-224 and the reader; none appears among the scored notebooks at 0.950 or above, so the title
claim is not supported (kozykappa's triple reader with the same parts scores 0.950).

## 2. The new component: heliosli's anatomy-anchored compact model (S6)

Read in the notebook code (worker sources embedded in the notebook):

- A ConvNeXt-small fine-tuned on report-derived targets with a per-slice native cache and
  **knee-centred views**: the joint centre is found by the **SKM-TEA V-Net segmentation model**
  (`anatomy.pt`) on sagittal series and projected through each series' DICOM geometry; the v4 views add
  the full field of view of every series. Four fold models; fixed 0.7 / 0.3 rank blend with the CoAtNet.
- This is exactly the "anatomical ROI" direction of `external-levers-2026-10-09.md` E8 (not pursued by
  us for cost), and it is the first public component that lifts the CoAtNet base by more than 0.001.

**Not usable any more.** The model files lived in `heliosli/rsna-knee-compact-v1`; its current version
(2026-10-09 13:50 UTC) contains only a README: "This dataset no longer ships model files. The earlier
versions have been retired and are not accessible. Notebooks that relied on them will not run." The
0.951-0.954 notebooks therefore cannot be re-run or forked now; teams that submitted them before the
retirement keep their scores.

## 3. What remains public from heliosli

`heliosli/rsna-orthofoundation-fold0-epoch7-20261004` (1.34 GB, licence "other": "Upstream weights retain
their original licensing; no new open-source license is granted"):

| File | What (receipt.json) |
|---|---|
| `best.pt` (1.22 GB) | OrthoFoundation-L fine-tuned on this competition, fold 0, epoch 7, EMA; author's weak-label validation macro AUC 0.932 (not comparable with our metrics) |
| `cloud_code.zip` | the author's training and inference code (anatomy, caches, probes, compact model) |
| `anatomy.pt` | SKM-TEA V-Net segmentation checkpoint (knee anchors) |
| `kneexnet/localizer.pt`, `kneexnet/best_model_256_noise_notebook_5_0.15.pth` | KneeXNet auxiliary weights (OAI-derived) |

No public notebook scores `best.pt` on its own or in a blend (checked the author's notebooks and the
`orthofoundation` search). Rule risk is higher than for the OAI CoAtNet (D-019): SKM-TEA (registration
and research-use agreement) and KneeXNet (OAI-derived, no explicit licence) are both among the datasets
of forum topic 743416 that the host has not ruled on; the OrthoFoundation pretraining data are not
documented here.

## 4. Consequences for us

- The 0.951 silver line of 2026-10-10 (STATUS) is explained by this cohort; new teams cannot join it
  through these notebooks, so its growth should slow, but the line itself stays at 0.951 or higher.
- The evidence for the anatomical-ROI idea is now direct: an anatomy-anchored ConvNeXt-small adds about
  +0.004-0.005 on top of the CoAtNet (0.949 -> 0.954 for bundle `209a32c8`, -> 0.951 for `c7ebab1e`).
  Rebuilding it ourselves needs a knee localiser (the public SKM-TEA checkpoint in the heliosli bundle or
  another one), a new cache of knee-centred views from DICOM (Kaggle) and training; a rough 2-3 days of
  engineering plus training, with the SKM-TEA rule risk if that checkpoint is used.
- `best.pt` (OrthoFoundation-L fold 0) could be tested as a partner without training, using the author's
  inference code; untested, heavy (ViT-L, 1.2 GB), and with the rule risk above.
