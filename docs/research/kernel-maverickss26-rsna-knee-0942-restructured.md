# rsna-knee-0942-restructured

- Source: https://www.kaggle.com/code/maverickss26/rsna-knee-0942-restructured (version 7, pulled 2026-10-01)
- License: Apache 2.0 (shown on the Kaggle page)
- Public LB: 0.942 (as of 2026-10-01)
- Local copy: external/kernels/maverickss26__rsna-knee-0942-restructured/

## What it is

The 0.942 step of the Speedy Raptors lineage, rewritten for readability. Same checkpoints
and arithmetic as its parent (author's text; 828-line diff to the 0.943 root, which
also added Global96 and Repair-v1). Jiwei Liu's 0.943 notebook names this as its
starting point.

Notable additions (author's text, partly verified):

- A single `RUN` config dict with the nine blend weights, and presets: `speedy` (the 0.942
  run), `parent` (flat 0.60 outer routing), `halfway`, `sparse` (62/42 windows instead of
  94). This is the easiest place to see which knobs exist.
- Read-only EDA: slot missingness, label prevalence and co-occurrence, report languages,
  pixel-spacing variation, and scanner/site fingerprints "with the fold-grouping leak they
  imply" (author's claim: random folds leak site identity; we did not verify).
- Per-finding diagnostics: arm disagreement and largest tie block.
- Explains that the 20-member DINO stage only fits the 9 h limit because the first six
  DINOv2 blocks are shared (verified by the hash gate in the code).

Technical details otherwise as in the
[root analysis](kernel-mattiaangeli-bend-the-knee-to-speedy-raptors-the-original.md).

## Value for us

Documentation and the `sparse` preset (a cheaper run mode). The site-leak claim is worth
checking in our own CV: if true, our folds should be grouped by scanner/site fingerprint.
