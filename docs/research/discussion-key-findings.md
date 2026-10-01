# Discussion digest: key findings and pitfalls

Read 2026-10-01 from the competition forum (about 25 topics, sorted by votes and by
recency) plus the competition overview pages. Forum text is participants' claims unless
marked as a host statement or as verified by us.

## Leaderboard state (verified, leaderboard download 2026-10-01)

| Rank | Public LB |
|---:|---:|
| 1 | 0.961 |
| 10 | 0.957 |
| 50 | 0.953 |
| 100 | 0.949 |
| 200 | 0.945 |
| 300-1000 | 0.943 |

4,730 teams. **1,001 teams are at >= 0.943**, i.e. the public stack is a plateau shared by
hundreds of teams; 167 teams are at >= 0.946 and 88 at >= 0.95. With the usual Kaggle medal
rules for this size (bronze top 10%, silver top 5%, gold top 10 + 0.2%), bronze is inside
the 0.943 tie block, silver needs about 0.945+, gold about 0.956+ on public.

## Rules and host statements

- **LLM APIs for labels are allowed.** Host (Po-Hao Chen, topic 733965): commercial LLM APIs
  may be used to read reports and generate labels; LLM-derived labels or embeddings may be
  used for training. Reports are not available at inference.
- **Labels are image-based, reports are not ground truth.** Host (topic 733826): gold labels
  were assigned from the images, independently of the reports; when report and image
  disagree, the image label is authoritative. Hence report-derived labels are noisy by
  design.
- **External data.** Host (733965, 2026-08-27): non-commercial licences alone do not exclude
  a dataset; datasets behind a click-through agreement are "generally" acceptable;
  institution approvals, IRB or lengthy credentialing may not be. A newer request for an
  explicit list (743416, 52 votes) is still unanswered as of 2026-10-01. Using MRNet, OAI,
  fastMRI etc. is therefore a grey zone that matters only for prize audits.
- **Prize eligibility with others' public weights** (744056): open question, no host answer.
  Not relevant unless we aim for prizes.
- **Efficiency Prize** (overview page, verified): a second track ranks
  `AUC / (Benchmark - maxAUC) + RuntimeSeconds / 32400` on the private set; the submissions
  you select for the main board are the ones evaluated. A daily public efficiency
  leaderboard is in `ryanholbrook/rsna-knee-abnormalities-efficiency-lb`.
- **Test set** (data page, verified): about 1,300 hidden test studies; images live in
  `test_series/`; the `Report` column is absent; prevalence may differ between train,
  public and private.
- **Private test composition** (744519): participants asked whether every hidden study has
  all three planes and a fluid-sensitive series; no answer yet. Keep missing-plane handling.

## Modelling findings (participants' claims)

- **Single models are strong.** Topic 735304 ("Best single-model score", 112 comments):
  single 2.5D models at 224-288 px report public 0.94-0.954 (CoAtNet 224 px single fold
  0.950; 5-fold ResNet 224 px 0.954; single-fold model 0.949 in about 5 min; Qwen-VL
  fine-tune 0.950). Resolution above 288 px "barely" helps; 140-160 mm field of view is
  reported better than 100 mm.
- **Labels and pseudo-labels are the main lever**, not encoder size ("Scaling the encoder
  bought us nothing (+0.0011)", 735154). Repeated recipe from several high scorers:
  train teachers on soft weak labels, then blend **out-of-fold** teacher predictions with
  the extracted label (about 50/50, kept soft) and retrain. In-fold predictions only
  "parrot the labels back". Masking uncertain label cells did not help anyone who reported.
- **Synovitis, Lateral OA and PF OA are the weak targets**; synovitis is under-reported in
  reports, so most report negatives are silence (733932, 737566, 735304).
- **"Not addressed" is a label too** (733932): treat silent findings differently from
  explicit negatives in the extracted labels.
- **Validation is noisy.** Gold 58 is too small to rank models; CV on extracted labels
  usually sits 0.02-0.04 below public LB but correlates with it (736635, 735304). Some
  report CV gains from bootstrapped labels that do not transfer to LB.
- **Window/slice density** (Raptor author, 737696): for the Raptor CoAtNet, more eval
  windows helped (42 -> 62 windows +0.003; 44 -> 80 slices +0.006), but others saw the
  gain saturate around 31 windows. Density, not span, is the lever.
- **Slice ordering** (735154, pilkwang): filenames are SOP Instance UIDs with no anatomical
  order; sort by `ImagePositionPatient` projected on the slice normal.
- **Fluid-sensitive and fat-suppression columns are identical** (verified by us: 100% row
  agreement in train and test CSVs), so they carry one axis, not two.
- **bf16 on T4/P100** (744230): silent AUC drop reported (0.851 -> 0.710). Use fp16 or fp32
  on T4. The public stack uses bf16 in its A5 stage.

## Leaderboard reliability and shake-up

- Public notebooks are widely viewed as public-LB-overfit blends; 0.941 -> 0.943 came from
  weight retuning on the public LB (see versia-5 history). Shake-up is expected around the
  bronze/silver lines (742327, 735767).
- Site split unknown (734681): participants could not get an answer whether public/private
  hold out whole sites. The maverick notebook claims scanner/site fingerprints leak across
  random folds; scanner-grouped CV is discussed in 734004.
- Top teams claim own models above 0.95 (742327), consistent with the leaderboard.

## Practical pitfalls

- Kaggle T4 queue waits of hours were reported (743746); submission runs over 2 h are
  common for heavy stacks (738129). Plan submissions early in the day.
- Some DICOMs are corrupt or use JPEG 2000 / JPEG Lossless transfer syntaxes (737163, data
  page); decoding must not crash on one bad file.
