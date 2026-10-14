# Public landscape check, 2026-10-13 evening

Status: findings for the user's request "is there new or different public code?" (after v47 = 0.956, rank 332-346).
Sources: Kaggle's public notebook API (317 competition notebooks, fetched about 20:00 UTC), notebooks pulled into
`external/kernels/*_20261013/`, forum threads 741819, 743416 and 746792 (Kaggle CLI), and a Codex web search (GPT-6 Astra,
read-only, `--search`) that ran out of its usage quota before writing its final answer; its log
(`codex_new_pub.out` in the session scratchpad) gave the forum and GitHub leads checked below. Verified in code or in the
forum text unless marked as a claim.

## 1. Notebooks

| Item | Displayed score | What it is (verified in code) | Usable by us | Verdict |
|---|---|---|---|---|
| Best public score | 0.956 | 15 notebooks at 0.956, none above; every R7-based one shares heliosli's R7 code | - | no public notebook above our display step |
| varshithakolupuri "One unused checkpoint lifts the 0.956", karttikjangid05 "Extra checkpoint explained", yuvrajlamba01 "Multiscale" | 0.956 | R7 + nartaa's second CoAtNet (`raptor_ft_alldata_t16_blendjev_oai_d96_c08_r224_swa.pt`, 224 px, 0.8 centre crop, about 0.945 alone per its author) mixed into the Raptor slot at 0.35 (final weight 0.175), under a time guard | **yes**: the checkpoint is in `nartaa/rsna-knee-publication-swa-weights-20261007`, which v47 already attaches (file list checked) | the only new public component. **Correction**: on 10-13 12:30 we wrote that its metadata lacks the checkpoint's dataset; wrong, the notebook finds the file in the dataset we already use. The author claims it "moved my rank inside the 0.956 block" (claim, not verified). Same OAI-trained CoAtNet family: no new rule risk, less diversity than the reader |
| jingshuifu "flip-TTA" | not scored | R7 with the bundle's `flip_tta` switched on (mirrored windows averaged in logit space; MCL plain pass); R7's own manifest has it off | yes | wait for its score; the bundle author left it off. (**Corrected 10-14**: the TTA is label-safe and matches R7's training mirror, see `silver-push-2026-10-14.md`) |
| le4ves "0.957 R7 blend", tahmidtawsif V13, mercurydust, Jenil, raihanjs, jingshuifu "0.957 fork" | 0.956 or none | code copies of R7 (identical cells or restructured with the same weights) | - | nothing new |
| lavinwins "RSNA Gold Medal" | 0.956 (API) | current code: CoAtNet + goodpjw2008 reader with per-finding weights, header "LB 0.950"; the 0.956 belongs to another version (L32) | - | nothing new |
| karttikjangid05 "Ensemble map", varshithakolupuri "What the top notebooks are made of" | - | audits: the top is a monoculture of six public datasets; R384 is inferred at 320 px in the shared Raptor recipe | - | context only |
| hukumjailer "Consensus Raptor training" | - | trains a CoAtNet-384 on 5-source consensus labels, weights not yet public | not yet | watch |
| github.com/sinhaaditya5/kaggle-rsna-knee-abnormality | - | a solo report-label + 2.5D pipeline (pushed 10-09) | - | nothing new |

## 2. External-data rulings (new to our notes)

- **Topic 741819, 2026-09-21, host Po-Hao "Howard" Chen**: using OAI "does not violate the ... rules if it is generally
  accessible to all participants without an escalated (i.e. institutional) review and sign-off or access to a legal team,
  and is free of charge"; the hosts do not comment on OAI's own terms.
- Topic 743416 (to 10-12): participants report individual OAI access via a Login.gov account with "Institutional Approval
  Required: No"; others report that access is blocked from some countries (China). No explicit host yes/no.
- Reading: the OAI risk behind the public CoAtNet (D-019) is lower than "no host answer" suggested, but not settled
  (country access). fastMRI (R7, D-032) was not covered by Codex before its quota ran out; unchanged.

## 3. Judgment

- No public notebook beats 0.956 and no different family has appeared; the 129-154 teams at >= 0.957 use private work.
- The only new public component we can use is the 224-px CoAtNet (R224). It is cheap (same dataset, about one more
  Raptor-stage pass), carries no new rule risk, and its author claims a hidden-digit gain on the R7 host. It is the same
  model family as our CoAtNet, so its expected gain is below the reader's (L33, L37).
- A probe v48 = v47 + R224 (public recipe weight 0.35 of the Raptor slot) needs a decision (D-031/D-032 closed the probe
  set), a runtime guard (v47's hidden-test runtime is unknown; v44 already adds the ROI stage), and should score after v44
  is judged (one submission that can change the best at a time).
