# Public notebooks and leaderboard: update 2026-10-05

Follow-up to `baseline-selection.md` (2026-10-01). Sources: Kaggle kernel list sorted by score
(CLI for order, Kaggle web API `ListKernels` for `bestPublicScore`, top 50 notebooks), kernel
metadata of two notebooks pulled to `external/kernels/`, the public leaderboard download
(2026-10-05 04:38 UTC), and the newest forum topics. Forum statements are participants'
claims, not verified.

## 1. Public notebooks: no new high score

| Public LB | Notebook | Inputs public | Note |
|---:|---|---|---|
| 0.946 | pjmathematician/rsna-knee-d4-blend | No (3 private) | unchanged since 2026-09-28 |
| 0.945 | pjmathematician/rsna-knee-d4-lite | No | unchanged |
| 0.945 | aastikrajan15/knee-s75-w50 | No (1 private) | unchanged |
| 0.945 | aastikrajan15/knee-s75-w60 | No (1 private; verified in `kernel-metadata.json`) | same author and run date as w50 (2026-09-27); not listed in the 2026-10-01 table |
| 0.943 | 30 notebooks, e.g. yamadan96/rsna-knee-d4-public0946, sushanthtiruvaipati/rsna-knee-d4-public0946-no-correction, weishanshan033/rsna-knee-d4-full-public-repro | Yes | d4 rebuilt with public inputs only scores 0.943 despite the "0946" names |
| 0.942 | kolyaflexcu/rsna-knee-speedy947 and others | Yes | name does not match the score |

Conclusion: the reproducible public ceiling is still **0.943**; every public score above it
uses private model legs (consistent with `baseline-selection.md` section 3). Nothing to adopt.

## 2. Leaderboard (2026-10-05)

5,184 teams. #1 0.963, #10 0.959, #50 0.955, #100 0.951, #200 0.946. 113 teams >= 0.950,
235 >= 0.946, 369 >= 0.944, 1,375 >= 0.943; the 0.943 tie block spans ranks 370-1,375.
Medal lines by rank: gold zone (top 20) 0.958, silver (top 5%, rank 259) 0.945, bronze (top
10%, rank 518) inside the 0.943 block. Our team (JerryMouse, v05 0.943) is rank 1,278:
inside the block, ties go to earlier submissions. **Any score >= 0.944 currently lands in
the top 369, i.e. inside bronze; 0.945 is the silver line.**

## 3. Forum points relevant to us (since 2026-10-01)

- Topic 745214 (participant "SpeedSci", claims): DINOv2 gold-58 0.917 -> LB 0.942; EffNet and
  ResNet gold about 0.89 -> LB 0.940; CoAtNet gold 0.915 -> LB 0.926; one label version gave
  EffNet gold 0.945 but LB 0.910. Relabelling alone moved their DINOv2 from LB 0.931 to 0.942.
  A reply notes that gold-58 is too small to resolve label choices. **Implication:** the
  gold -> LB relation is model-dependent and noisy. Our v08 (gold 0.897 -> LB 0.909) sits far
  below their EffNet/ResNet (gold about 0.89 -> 0.940), so either gold-58 noise or something
  in our leg that does not carry to the hidden test explains a gap of about 0.03; STATUS
  lesson 3 should be read as one data point.
- Topic 745861 (hengck23 and replies): image-level labels from a multimodal LLM shown the
  report and images, or active labelling; one participant reports 80-90% agreement on 800
  studies. Not actionable for us in the remaining time without a labelling budget.
- Topic 745759: public forks sort slices by file name (SOP UID), which is anatomically
  random; sorting by `ImagePositionPatient` gave +0.028 on one fold. Our pipeline already
  sorts by geometry (v06/v07, 100% of training series).
- Topic 745283 asks whether RadImageNet ResNet-50 weights are allowed for prize-eligible
  submissions (no host answer seen). Relevant to the anchor's licence for prizes only, not to
  the leaderboard.
