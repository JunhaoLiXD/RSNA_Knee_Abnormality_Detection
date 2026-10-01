# knee s75 w50

- Source: https://www.kaggle.com/code/aastikrajan15/knee-s75-w50 (version 1, pulled 2026-10-01)
- License: Apache 2.0 (shown on the Kaggle page)
- Public LB: 0.945 (as of 2026-10-01); sibling `knee-s75-w60` also 0.945
- Local copy: external/kernels/aastikrajan15__knee-s75-w50/

## What it is (verified in code)

The unmodified Speedy Raptors root (62-line diff, all appended at the end) plus one extra
stage. The extra stage is a 1,132-line Python script embedded as base64
(`_OURS_SCRIPT_B64`), written to disk and run in a subprocess. We decoded it locally (not
executed). It loads 10 checkpoints from one private dataset:

- `convnext_tiny`, 320 px, 24 slices, 5 folds x 2 checkpoints each
  (`f{0..4}_convnext_tiny_320x24_pt_v5_cv{8961..9154}_best.pt`); the filename CV values
  0.896-0.915 are on the author's own weak-label folds.
- 130 mm crop, `test_series` image root, models grouped by input geometry.

Final blend: `rank(0.5 * rank(public stack) + 0.5 * rank(own ConvNeXt))` (verified,
`OUR_WEIGHT = 0.5`).

## Reproducibility

Not reproducible: the checkpoint dataset is a "[Private Datasource]" (one empty slug in
`kernel-metadata.json`).

## Takeaway

Independent confirmation of the d4-blend pattern: a plain 5-fold ConvNeXt-tiny at 320 px
with weak-label CV around 0.90, blended 50/50 by rank, lifts the 0.943 public stack to
0.945. This is a modest, reproducible-in-principle model, and the strongest argument that
our own diverse model is worth more than further reweighting of the public stack.

Everything else (backbone of the public part, input, run time, external weights): see the
[root analysis](kernel-mattiaangeli-bend-the-knee-to-speedy-raptors-the-original.md).
