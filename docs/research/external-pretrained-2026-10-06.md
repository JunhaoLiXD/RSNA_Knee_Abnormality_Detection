# External knee MRI data and MRI-pretrained models: survey 2026-10-06

Question (user, 2026-10-06): can we transfer from similar external datasets or pretrained
models and then adapt with the competition data? Follow-up to `v11-strategy-revision-design.md`
section 3.1 (datasets, 2026-10-04). Sources: Hugging Face Hub search, Kaggle dataset search,
web search, arXiv pages, competition forum. Claims from papers and forum posts are not
verified by running anything.

## 1. Rules (unchanged since 2026-10-04)

- Freely and publicly available external data, including pretrained models, is allowed
  (`competition.md`). Non-commercial licences alone do not exclude a resource; straightforward
  registration is generally acceptable; institutional approvals may not be (host, topic 733965).
- The host ruled **KneeCoT not allowed** (formal institutional agreement). The request for a
  yes/no per dataset (topic 743416: MRNet, SKM-TEA, fastMRI/fastMRI+, OAI, KneeMRI,
  KneeXNet-2.5D) has **no host answer** as of 2026-10-06. Participants note that MRNet's
  agreement forbids derivative works and cite a past competition where prize teams were
  removed for external data the host had not cleared. One participant reports no gain from
  external data (unverified).

## 2. Pretrained models

| Model | What | Knee in pretraining | Weights and licence | Fit for our 2.5D pipeline |
|---|---|---|---|---|
| **MRI-CORE** (Duke; arXiv 2506.12186) | 2D ViT-B (SAM image-encoder init), DINOv2 self-supervised on more than 6 M slices from 110 k MRI volumes, 18 body locations | Yes (knee listed among the regions; counts not given) | Public, `github.com/mazurowski-lab/mri_foundation`, **CC BY 4.0** (per the paper) | Good conceptually (2D slices); costly: ViT-B at nominal 1024 px, single channel; at our 320 px it is several times the compute of ConvNeXt-tiny (to be measured) |
| **MARS** (HKUST; Nature Biomedical Engineering 2026) | 3D Swin encoder with anatomy/sequence disentanglement, 336 k volumes from 64 datasets | Yes; reports ACL and meniscal tear classification | Code `github.com/zqiuak/MARS`, weights on Google Drive; licence not stated | Poor: 3D volumes per series, a new input pipeline |
| RadImageNet (ResNet-50, DenseNet-121, Inception) | Supervised on 1.35 M radiology images including MSK MRI | Yes | Public mirrors on Kaggle (for example `shigechan/radimagenet-resnet50-official`); the anchor already uses ResNet-50 heads | Good (2D CNN); ResNet-50 overlaps with the anchor, DenseNet-121 does not |
| KneePreM (arXiv 2609.31461) | 3D U-Net MAE on 19,011 OAI series | Knee only | No public weights found | - |
| OrthoFoundation (arXiv 2601.18250) | DINOv3 backbone, 1.2 M knee X-ray and MRI images | Knee | Not released ("code upon publication") | - |
| Public weights trained on this competition's data (pilkwang DINOv2, Mattia CoAtNet, Raptor) | Knee-specific | This dataset | CC0 mostly | Fine-tuning them makes our leg more like the anchor (wrong direction for the blend) and leaks fold labels |

## 3. External datasets

| Dataset | Overlap with our 12 labels | Access | Practical cost |
|---|---|---|---|
| MRNet (1,370 exams) | ACL, meniscus (side not given), abnormal | Registration, research-use agreement (no derivatives per participants); Kaggle mirrors exist but redistribution is likely not permitted | 6 GB; preprocessed 256 px stacks without DICOM geometry; no host clearance |
| fastMRI+ (1,172 knee exams) | Meniscus, ACL, MCL, effusion, contusion/fracture, cartilage loss | Annotations CC BY 4.0; images under the fastMRI data-sharing agreement (mirrors on Kaggle of unclear status) | Single coronal plane; tens to hundreds of GB; new pipeline; no host clearance |
| OAI (MOAKS: effusion-synovitis, Baker's, BML, meniscus, ligaments) | Broadest overlap | Data Use Certification with institutional requirements (host: may be a barrier); a gated Hugging Face mirror (`charwisreno/OAI-Knee-MRI`) is of unclear status | Large; likely not allowed |
| KneeMRI (Rijeka, 917 exams) | ACL only | CC BY-NC-ND 4.0 (no derivatives) | Not usable for training under its licence |
| SKM-TEA (155 scans) | Few pathology boxes | Registration | Too small to matter |

## 4. Assessment

- **External datasets: not recommended now.** None has host clearance; the two with the
  broadest overlap (OAI, fastMRI+) are either institution-gated or need a new single-plane
  pipeline and large downloads; MRNet covers mainly ACL and meniscus and its agreement is
  read as forbidding derivatives. The expected gain is unknown and the disqualification risk
  is real. Revisit only if the host answers topic 743416 with a yes.
- **MRI-pretrained backbones: feasible and within the rules** (public, CC BY 4.0 for
  MRI-CORE). They replace the ImageNet initialisation inside our existing trainer, so no new
  data pipeline is needed. Candidate uses: arm M of the v13 design (second model) with an
  MRI-pretrained backbone instead of an ImageNet EfficientNet, which also differs from the
  anchor's ImageNet-DINOv2 members. Open points: MRI-CORE compute at 320 px with 80 tokens
  per study (throughput must be measured before any fold run), single-channel input versus our
  3-slice triplets, and weight packaging as a Kaggle dataset for offline submission.
- Distilling or fine-tuning the anchor's own public weights is not recommended (raises
  correlation with the anchor, STATUS L15).

## Sources

- MRI-CORE: https://arxiv.org/abs/2506.12186 (HTML v2: https://arxiv.org/html/2506.12186v2)
- MARS: https://smartx.cse.ust.hk/2026/07/15/mars/
- KneePreM: https://arxiv.org/abs/2609.31461
- OrthoFoundation: https://arxiv.org/abs/2601.18250
- MSK MRI foundation models (fine-tuned segmenters): https://www.nature.com/articles/s41746-026-02520-w
- fastMRI+: https://arxiv.org/pdf/2109.03812
- Competition forum topics 733965 and 743416 (read 2026-10-06)
