# Heliosli R6 reweighted public blend

- Source: https://www.kaggle.com/code/heliosli/blend-mine-in-private-lb-luck-to-all-upvoters (visible version 1, run 358751289, pulled 2026-10-16 UTC / 2026-10-15 EDT)
- License: notebook/source license not established in this audit; R6 dataset reports `other`. Confirm before derivation.
- Public LB: Kaggle API `bestPublicScore` **0.958** as of 2026-10-16 00:22 UTC; one version visible. Own reproduction not run.
- Local copy: `external/kernels/heliosli__blend-mine-in-private-lb-luck-to-all-upvoters_20261016/`

Inference: nartaa CoAtNet-384 and 224-px centre-crop checkpoints, mixed 0.65/0.35 in the Raptor slot;
heliosli R6 ConvNeXt-small four-fold bundle `fe055406fad6a12f`, knee-anchored views, flip TTA and fluid/state stackers
in the compact slot. Fixed per-finding rank blend: Raptor 0.5 by default, Lateral OA 0.2, PF OA 0.6, Synovitis 0.8,
Baker's 0.35. No new training/report-label generation occurs in this notebook. No outer goodpjw2008 reader or S6F0 leg.
The models' external-data history is inherited; the bundle's training configuration is a manifest claim, not independently retrained evidence.

Exact R6 input `heliosli/rsna-knee-r6-frozen-fe055406-w1` (attached dataset-version ID 20761842) is currently
accessible despite the stale private-copy code comment. Its manifest equals rostigor's versioned mirror byte for byte,
SHA-256 `6508ce6921eda986c885b2226fa55dd4d2aa8e5fc570b4c007c9a60c05bfc648`. Remaining inputs are nartaa's
selected SWA weights and heliosli's public OrthoFoundation code/anchor package, already used by the project.

Downloaded public commit receipts show PASS, correct R6 bundle, 3/3 scored and no component failures. Independent
rank-blend recomputation matches the published submission to 2.4e-8. Model binary hashes, source licensing, our own
end-to-end inference, hidden-test runtime and independent leaderboard reproduction remain unchecked.

Assessment: strongest newly found reproduction candidate; not yet an adopted model. Full comparison, exact checks,
risks and next-action boundaries: `public-landscape-2026-10-16.md`.
