# v64 - the v62 recipe (public 0.958: R6 flip-TTA, per-finding weights) + the R224 mirror + the reader at 0.10 (D-033/D-034)

Explicit ensemble version (D-017). Same notebook as v63 (`scripts/d033/build_v63.py v64 0.0`) with one constant changed:
the v61 anchor weight is 0, so `final = pct(0.9 x pct(v62 recipe) + 0.1 x pct(reader))` per finding (final = v62 recipe
without the reader). Relative to v62 (a byte-equal copy of heliosli's 0.958 notebook) the differences are two additions
with positive evidence on earlier hosts:

- R224 scores the plain and the anatomically mirrored knee (v54 over v53: +44 stable witnesses, L41).
- goodpjw2008's reader at an outer weight of 0.10 under v61's own use/fallback decision (v40: +211, v47: +191, L33, L37).

The v62 recipe is kept verbatim (Raptor half 0.65 R384 + 0.35 R224; Raptor weight Lateral OA 0.2, PF OA 0.6, Synovitis 0.8,
Baker's 0.35, else 0.5; R6 in the compact slot). Public evidence: heliosli's uniform-weight R6 notebook and goodpjw2008's
R6 + mirror + reader versions (uniform weights) display 0.957; only the per-finding version displays 0.958.

The v61 stages (R7, S6F0) still run because the notebook is v63's: they feed only the fallback. Any R6 problem leaves v61's
output byte for byte, as in v63. R224 enters only if v61's stage 3 used it.

## Provenance

- R6: heliosli's ConvNeXt-small bundle `fe055406fad6a12f`, dataset `heliosli/rsna-knee-r6-frozen-fe055406-w1`, run by v62's
  asset cell and controller call (see v63). Source notebook: https://www.kaggle.com/code/heliosli/blend-mine-in-private-lb-luck-to-all-upvoters
  (version 1; licence not stated; dataset licence `other`).
- Reader: goodpjw2008/rsna-knee-2-5d-convnext-reader (Apache 2.0), cells of v47/v61 unchanged.

## Our changes (against v61)

As v63 (appended R6 stage and final blend; every v61 cell byte-identical), with `V63_W_ANCHOR = 0.0`.

Extra input to attach: `heliosli/rsna-knee-r6-frozen-fe055406-w1`.

---

Base notebook header (v61):

__BASE_BODY__
