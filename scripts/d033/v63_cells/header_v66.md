# v66 - v64 with S6F0 as a second model of the compact slot (0.65 R6 + 0.35 S6F0, v61's rule) (D-033/D-034)

Explicit ensemble version (D-017). Same notebook as v64 (`scripts/d033/build_v63.py v66 0.0 s6f`) with one change in the final
blend cell: the compact slot that `v62_recipe` gives to R6 alone becomes, per finding,
`slot = 0.65 x rank(R6) + 0.35 x rank(S6F0)`, each model ranked over its own non-failed studies. A study S6F0 failed on keeps
rank(R6) alone; a study R6 failed on keeps rank(S6F0) alone. The slot ranks enter v62's per-finding blend unchanged; everything
else (Raptor half, per-finding Raptor weights, the reader at 0.10, every fallback) is v64's.

Rule, copied from v61's S6F0 rule (cell 14, `[s6f]`, with R6 in R7's place), weight 0.35 fixed before any run and not tuned.
S6F0 is used only if v61's stage 3 used it (`blend_receipt.json` `s6f.used` is true), and not at all (the slot is R6 alone,
the output exactly v64's) if its output is missing or malformed, its unscored count differs from that receipt, more than 3 % of
the studies are unscored by S6F0, its mean per-finding Spearman with R6 is below 0.5 (checked from 50 jointly scored studies
on), or anything in the M2 code raises. S6F0's scored set is read as v61 cell 14 reads it: the studies with a complete row
inside [0, 1] in `S6F_PRED/part*/predictions.csv` and `S6F_PRED/retry/predictions.csv`.

Evidence and risk:

- For: S6F0 at 0.35 of the compact slot improved v54 (v61 vs v55: 37 stable witnesses, none reversed, L44); a near-host-strength
  addition of a different training set helped before (R224, L40).
- Against: a second same-lineage ConvNeXt moved nothing on v54 (old S6, L43); L44 supports that fixed blend with R7, not a
  general rule, and R6 is a different host. goodpjw2008's own notes (pulled
  `external/kernels/goodpjw2008__rsna-knee-coatnet-2-5d-convnext-mil-lb-0-954_20261016b/`, cell 1): versions 16-20 (224 mirror and
  S6 as a second compact model at 0.3/0.4) all displayed 0.956 but moved that notebook from rank 549 to 325 in its block, and
  V21 keeps R7 as a second compact model at 0.4 of the slot next to R6 for that reason (author's claim, not verified here).
- v62's per-finding Raptor weights (Lateral OA 0.2, PF OA 0.6, Synovitis 0.8, Baker's 0.35) were chosen for R6 alone (L45);
  this version keeps them for a mixed slot, which they were not selected for.

## Provenance

- S6F0: nartaa's all-data S6 ConvNeXt-small (nartaa/rsna-knee-s6fall-solo, Apache 2.0 code; weights CC BY-NC 4.0), v61's
  stage unchanged (its `ours_s6f_sub.csv` is reused, not rerun).
- R6: heliosli's ConvNeXt-small bundle `fe055406fad6a12f`, dataset `heliosli/rsna-knee-r6-frozen-fe055406-w1`, run by v62's
  asset cell and controller call (see v63). Source notebook: https://www.kaggle.com/code/heliosli/blend-mine-in-private-lb-luck-to-all-upvoters
  (version 1; licence not stated; dataset licence `other`).
- Reader: goodpjw2008/rsna-knee-2-5d-convnext-reader (Apache 2.0), cells of v47/v61 unchanged.

## Our changes (against v61)

As v64 (appended R6 stage and final blend; every v61 cell byte-identical, `V63_W_ANCHOR = 0.0`), plus the S6F0 term of the
compact slot in the final blend cell.

Extra input to attach: `heliosli/rsna-knee-r6-frozen-fe055406-w1`.

---

Base notebook header (v61):

__BASE_BODY__
