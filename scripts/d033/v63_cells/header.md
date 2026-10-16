# v63 - v61 (0.957) rank-blended 0.5/0.5 with the v62 recipe (public 0.958: R6 flip-TTA, per-finding weights) (D-033)

Explicit ensemble version (D-017), decision D-033; design `docs/research/v63-v61-v62-blend-design.md`. Two verified recipes of
similar displayed score, combined by one fixed, untuned rule:
`mix = pct(0.5 x pct(v61 anchor) + 0.5 x pct(v62 recipe))`, `final = pct(0.9 x pct(mix) + 0.1 x pct(reader))` per finding, where
the v61 anchor is v61's stage-3 output before the reader and the reader is used at v61's 0.10 under v61's own decision
(final = mix without it), so the reader keeps its tested weight instead of being halved (review finding 1).

## Provenance of the addition

- R6: heliosli's ConvNeXt-small bundle `fe055406fad6a12f` (4 folds, fluid and state stackers, flip-TTA), dataset
  `heliosli/rsna-knee-r6-frozen-fe055406-w1` (manifest sha256 `6508ce69...`, every checkpoint asserted against it), run by the
  asset cell of `notebooks/v62-submit.ipynb` (cell 7, byte for byte apart from the temp folder `probe` -> `probe_r6`) and v62's
  controller call. Source notebook: https://www.kaggle.com/code/heliosli/blend-mine-in-private-lb-luck-to-all-upvoters (version 1;
  licence not stated; dataset licence `other`).
- v62 recipe: v62's stage-3 formula (Raptor half 0.65 R384 + 0.35 R224; Raptor weight Lateral OA 0.2, PF OA 0.6, Synovitis 0.8,
  Baker's 0.35, else 0.5), here with this notebook's R224, which uses the anatomical mirror (v54); v62 itself has no mirror.
  R224 enters only if v61's stage 3 used it; otherwise the Raptor half is R384 alone.

## Our changes (against v61)

1. This cell and the configuration cell (`VERSION = 'v63'`).
2. Appended after v61's last cell: a markdown cell, `%%writefile /tmp/v63_r6_setup.py` (v62's R6 asset cell), the R6 stage
   (own namespace, own temp folder, own output files `ours_r6_sub.csv`, `r6_submission_receipt.json`, `r6_worker*_log.txt`;
   launch only with time left >= 1.3 x this run's R7 controller time and >= 20 min before an 8.65 h cut-off; own process group,
   killed at the cut-off and on every exit path) and the final blend (`v61_submission.csv` and `v63_receipt.json` written).
3. Every v61 cell is byte-identical (asserted in `scripts/d033/build_v63.py`). Any R6 problem leaves v61's output byte for byte.

Extra input to attach: `heliosli/rsna-knee-r6-frozen-fe055406-w1`.

---

Base notebook header (v61):

__BASE_BODY__
