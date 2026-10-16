# v65 - v64 with R7 as a second model of the compact slot (0.65 R6 + 0.35 R7, v61's S6F0 rule) (D-033/D-034)

Explicit ensemble version (D-017). Same notebook as v64 (`scripts/d033/build_v63.py v65 0.0 r7`) with one change in the final
blend cell: the compact slot that `v62_recipe` gives to R6 alone becomes, per finding,
`slot = 0.65 x rank(R6) + 0.35 x rank(R7)`, each model ranked over its own non-failed studies. A study R7 failed on keeps
rank(R6) alone; a study R6 failed on keeps rank(R7) alone. The slot ranks enter v62's per-finding blend unchanged; everything
else (Raptor half, per-finding Raptor weights, the reader at 0.10, every fallback) is v64's.

Rule, copied from v61's S6F0 rule (cell 14, `[s6f]`), weight 0.35 fixed before any run and not tuned. R7 is not used at all
(the slot is R6 alone, the output exactly v64's) if its output is missing or malformed, its unscored count differs from v61's
blend receipt, more than 3 % of the studies are unscored by R7, its mean per-finding Spearman with R6 is below 0.5 (checked
from 50 jointly scored studies on), or anything in the M2 code raises. R7's scored set = the studies with a complete row inside
[0, 1] in the R7 controller's `worker*/predictions.csv` under `pred` (bound once by v61 cell 8, never rebound later); the
controller's column-mean fill in `ours_sub.csv` is never read as a prediction.

Evidence and risk:

- For: a second compact model of a different bundle helped v54 at 0.35 of the slot (S6F0, L44); same-family additions that
  are close to the host's strength helped (R224, L40). R7 (public 0.957 host in v61) and R6 are different bundles.
- Against: a second same-lineage ConvNeXt moved nothing (old S6 on v54, L43). goodpjw2008's own notes (pulled
  `external/kernels/goodpjw2008__rsna-knee-coatnet-2-5d-convnext-mil-lb-0-954_20261016b/`, cell 1): versions 16-20 (224 mirror and
  S6 as a second compact model at 0.3/0.4) all displayed 0.956 but moved that notebook from rank 549 to 325 in its block, and
  V21 keeps R7 as a second compact model at 0.4 of the slot next to R6 for that reason (author's claim, not verified here).
- v62's per-finding Raptor weights (Lateral OA 0.2, PF OA 0.6, Synovitis 0.8, Baker's 0.35) were chosen for R6 alone (L45);
  this version keeps them for a mixed slot, which they were not selected for.

## Provenance

- R7: heliosli's ConvNeXt-small bundle `8c7b666e27dc0e8f`, v61's stage unchanged (its `ours_sub.csv` is reused, not rerun).
- R6: heliosli's ConvNeXt-small bundle `fe055406fad6a12f`, dataset `heliosli/rsna-knee-r6-frozen-fe055406-w1`, run by v62's
  asset cell and controller call (see v63). Source notebook: https://www.kaggle.com/code/heliosli/blend-mine-in-private-lb-luck-to-all-upvoters
  (version 1; licence not stated; dataset licence `other`).
- Reader: goodpjw2008/rsna-knee-2-5d-convnext-reader (Apache 2.0), cells of v47/v61 unchanged.

## Our changes (against v61)

As v64 (appended R6 stage and final blend; every v61 cell byte-identical, `V63_W_ANCHOR = 0.0`), plus the R7 term of the
compact slot in the final blend cell.

Extra input to attach: `heliosli/rsna-knee-r6-frozen-fe055406-w1`.

---

Base notebook header (v61):

__BASE_BODY__
