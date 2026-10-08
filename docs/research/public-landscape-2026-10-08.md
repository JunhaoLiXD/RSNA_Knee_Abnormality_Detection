# Public notebooks and leaderboard: update 2026-10-08

Follow-up to `public-landscape-2026-10-05.md`. Sources: Kaggle web API `ListKernels`
(`bestPublicScore`, competition 154281, top 50 notebooks), ten notebooks pulled to
`external/kernels/` with metadata (2026-10-08), dataset metadata and the README and checkpoint
manifest of `nartaa/rsna-knee-publication-swa-weights-20261007`, the public leaderboard download
(`external/datasets/lb/2026-10-08/`), and forum topics 743416 and 746792. Forum statements are
participants' claims, not verified.

## 1. Leaderboard (2026-10-08)

5,493 teams. #1 0.964, #10 0.961, #100 0.953. Bronze (top 10%, rank 549) **0.947**, silver (top 5%,
rank 274) **0.950**. Teams at or above: 0.950 401, 0.946 613, 0.945 753, 0.944 954, 0.943 1,749.
Our best (v15, 0.944) is rank 844 (the 0.944 block spans ranks 754-954). On 2026-10-05 a 0.944 was
inside bronze (top 369); the bronze line rose by 0.003 in three days.

## 2. Public notebooks: a new 0.949-0.950 lineage

| Public LB | Notebook | Inputs | Core |
|---:|---|---|---|
| 0.950 | matterhorn3838/rsna-knee-v2-velciraptor-dinosaur-speed (86 votes), matterhorn3838/rsna-knee-d4 | 2 public datasets | CoAtNet-384 SWA + ConvNeXt reader, per-finding rank weights |
| 0.950 | sujanmajhisuzan/rsna-knee-apex-grandmaster-stack (122 votes) and forks: hitarthjain0 (V5), rabari9999 (V5), haideptry (comparative study) | 2-3 public datasets | same |
| 0.950 | kozykappa/rsna-knee-gold-gated-triple-reader | 2 public datasets | CoAtNet-384 + CoAtNet-224 + ConvNeXt reader |
| 0.949 | nartaa/rsna-knee-0949-anatomical-mirror (60 votes; the source), xianhan fork | 1 public dataset | CoAtNet-384 SWA alone, native 320 crop, anatomical mirror TTA |
| 0.949 | prvsiyan/the-bee-s-knees-final-rsna-push, goodpjw2008/rsna-knee-0-949-coatnet-stack-blend-lb-0-949 | 13-15 datasets | old community stack (our v05 anchor's inputs) + the CoAtNet-384 SWA |
| 0.946-0.945 | pjmathematician d4-blend / d4-lite, aastikrajan15 s75 (2026-09-26..28) | private legs | old lineage |
| 0.944-0.945 | sujanmajhisuzan tri-specialist superstack, nartaa 0945 efficient 224crop, goodpjw2008 stack + ConvNeXt MIL, others | public | old stack + a leg, or the 224-crop CoAtNet |

Verified in code (all twelve notebooks at 0.949-0.950): every one loads
`raptor_ft_alldata_t16_blendjev_oai_d96_r384_swa.pt` and pins its SHA-256 `7e5315dad125...`
(dataset `nartaa/rsna-knee-publication-swa-weights-20261007`). The 0.950 variants add
`goodpjw2008/rsna-knee-2-5d-convnext-reader` (3 ConvNeXt-tiny folds, Apache 2.0) with hand-set
per-finding rank weights from 0.03 (Synovitis) to 0.35 (Baker's) in a guarded fusion cell that
falls back to the CoAtNet alone. Blending the old stack into the CoAtNet (prvsiyan, goodpjw2008)
scores 0.949, not higher.

Author's text (topic 746792, dataset README): one CoAtNet with finding-specific MIL attention,
trained on 4,349 report-labelled studies plus **2,399 OAI knees** (masked external supervision for
PF OA, Lateral OA and Synovitis), 16 epochs, three-epoch SWA; 96 slices, 94 windows, native 320
crop of a 384 cache, mirror TTA. Recipe history: 0.942 without OAI, **0.945 after adding OAI
(+0.005)**, 0.948 at 384 px, 0.949 with mirroring. Gold-58 was reused for selection. Scoring
turnaround about 26 minutes for the accuracy entry.

## 3. The OAI question (unresolved)

- Competition rule: freely and publicly available external data is allowed, including pretrained
  models (`competition.md`). Host principles (Aug 27, topics 733652 / 733965): click-through
  registration is generally acceptable; institution-specific approvals, IRB or long credentialing
  may not be; KneeCoT was ruled out for unequal access; the host phrase is "generally accessible to
  all participants".
- OAI is distributed by the NIMH Data Archive under a Data Use Certification; the weights' README
  says access to OAI data "remains governed by NDA's terms". Forum (746792): some participants
  registered with only an email; others report sign-in failures and that NIH bars some countries
  (China, Russia). The explicit per-dataset question (743416, 76 votes, OAI listed) has had no
  host answer since 2026-09-26.
- The weights themselves are public on Kaggle (licence "other": research and educational use,
  "including the RSNA Knee competition"). Whether a model trained on OAI counts as allowed external
  data is the open point; winners must release code and weights.
- Precedent cited in 743416: two prize-place teams were removed in the Deepfake Detection
  Challenge over external data. Detailed audits usually focus on prize teams, but a ruling against
  OAI could remove any team that used it.

## 4. What this means for us (STATUS L15, L17, L18)

- **Without OAI** the public frontier is about where we are: our v15 0.944 equals the
  goodpjw2008 stack + ConvNeXt MIL notebook (0.944); the 0.945-0.946 entries of 2026-09-26..28 use
  private legs; the 0.945 "tri-specialist superstack" (2026-10-06) was not inspected. Our 5-fold N leg (0.936 alone) is stronger than the public ConvNeXt reader
  (0.929 alone with 3 folds).
- **With OAI** a public base of 0.949-0.950 exists. Bronze is 0.947 today, but more than 400 teams
  are already at 0.950 and the line will keep rising as forks spread; the 0.950 forks differ only
  in fusion weights, so 0.950 alone is unlikely to hold a medal by 2026-10-22.
- A leg is worth adding to a stronger base only if it is strong and different (L18: for a 0.949
  base and our 0.936 leg the binormal model gives at most about +0.0003). The public ConvNeXt reader
  added +0.001 to the CoAtNet with per-finding weights; our N leg is a ConvNeXt-tiny 2.5D model of
  the same family, so it is likely redundant with that reader.

## 5. Options

| Option | Expected public LB | Risk |
|---|---|---|
| A. Stay non-OAI: keep v05 + v15 (0.944) | 0.944 now; medal only after a shake-up or an OAI ruling that removes OAI users | none from rules; no medal on the current board |
| B. Adopt the OAI-based CoAtNet as anchor (new version), optionally blend our N leg and/or the ConvNeXt reader | about 0.949-0.950 | rules: depends on an unresolved host ruling; medal line likely to move above 0.950 |
| C. Hedge by final selection: one non-OAI pick (v15) and one OAI-based pick | best of both on the private board | a ruling against OAI may remove the team, not only the pick |
| D. Ask the host first (comment in 743416 / 746792), decide after an answer | - | the answer may not come before 2026-10-15 (team merger) or 2026-10-22 |

Not decided here: the choice between A, B/C and D is the user's (rules and risk appetite).
Independent of it, any own-model work should target the non-OAI frontier gap (a leg near
0.943-0.945 alone, L18) and goes through a design note and Codex review (D-004).
