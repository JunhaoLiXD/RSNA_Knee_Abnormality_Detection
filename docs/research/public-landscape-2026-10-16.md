# Public landscape audit, 2026-10-16 00:22 UTC (October 15 EDT)

Status: read-only discovery requested by the user. No notebook built, GPU run started, or submission sent.
Incumbent: v61, public 0.957; 37 stable positive / zero reverse crossings, persistence pending.

## Scope and evidence

- Saved two 100-item CLI inventories, sorted by score and recent run, in
  `external/lb/public_notebooks_{score,recent}_20261016.json`. These are overlapping samples, not a complete census.
- Pulled 14 selected public notebooks unchanged into `external/kernels/<owner>__<slug>_20261016/`.
  `audit_kernel.json` records Kaggle's public `GetKernel` response; `audit_versions.json` records `ListKernelVersions`.
  These endpoints distinguish actual `bestPublicScore` from a score written in a title.
- Version histories expose commit input-version IDs and run receipts but no per-version competition score in the
  responses used here. A multi-version notebook's best badge therefore cannot be attributed to its latest code here.
- Downloaded small public manifests and commit-output CSVs/receipts. Did not download checkpoint binaries, execute
  third-party code, or independently reproduce a hidden-test leaderboard score.
- Web search was unhelpful and notebook pages were inaccessible through the web reader; primary evidence is Kaggle
  CLI/API data and the downloaded public code, not search snippets.

## Findings

| Public source | API best score | Verified code/input facts | Assessment |
|---|---:|---|---|
| [heliosli/blend-mine-in-private-lb-luck-to-all-upvoters](https://www.kaggle.com/code/heliosli/blend-mine-in-private-lb-luck-to-all-upvoters) | **0.958** | One visible version, V1, run 358751289, COMPLETE. R6 `fe055406fad6a12f` + flip TTA; R384/R224 rank mix 0.65/0.35; published per-finding outer weights. Exact attached R6 dataset is now API-accessible and attached as a dataset version. | **Highest-priority reproduction candidate.** New evidence changes the old unavailable-R6 conclusion. Score not yet reproduced by us. |
| [heliosli/this-is-best-public-dataset-new-version-0-9576](https://www.kaggle.com/code/heliosli/this-is-best-public-dataset-new-version-0-9576) | 0.957 | One visible V1, run 358332966. Same R6 and flip; uniform 0.5 outer weights. Commit receipt proves R6, not R7, ran. Original dataset has multiple versions; use exact identity checks. | Useful public control/reference; do not confuse it with the earlier R7-based v56 attempt. |
| [goodpjw2008 updated blend](https://www.kaggle.com/code/goodpjw2008/rsna-knee-coatnet-2-5d-convnext-mil-lb-0-954) | 0.956 | Latest V24, run 358807371, uses R6 + flip, R224 mirror, and reader at small per-finding weights; public versioned R6 mirror attached. Receipt confirms R6, 3/3 scored. | Useful independent confirmation that the R6 input works; badge does not establish V24's score. No demonstrated improvement over v61. |
| [laimerbotrolenk/rsna-four-model-ensemble](https://www.kaggle.com/code/laimerbotrolenk/rsna-four-model-ensemble) | 0.957 | V1 run 358703526. R7 + all-data S6F0 + R384/R224; R7 flip disabled; final R7/S6 weights 0.30/0.20. | Same components already present in v61, different weights/TTA; not a new model family and not a reason for a weight search. |
| [kiyoshiohno/rsna-knee-template](https://www.kaggle.com/code/kiyoshiohno/rsna-knee-template) | 0.957 | Latest V15 is a thin launcher; implementation lives in `kiyoshiohno/rsna-knee-local-logic`, dataset-version ID 20779065. Listing its files returns 403. | Not reproducible from accessible inputs; exclude. |
| [bliverrigpdoge knee-centred leg](https://www.kaggle.com/code/bliverrigpdoge/r7-raptor-knee-centred-convnext) | 0.957 | Author explicitly says private leg; attached `rsna-knee-kcd25leg` still returns 403. | Remains unavailable, consistent with prior audit. |
| [yuvrajlamba01/research-optimized](https://www.kaggle.com/code/yuvrajlamba01/rsna-knee-research-optimized) | 0.957 | Latest code pins R7 `8c7b666e27dc0e8f`; seven visible versions; original frozen dataset's attached version differs across notebooks. | No new component; latest-version score unestablished. |
| [yuvrajlamba01 LUPI blend](https://www.kaggle.com/code/yuvrajlamba01/rsna-knee-lupi-multi-plane-mil-sota-blend-0-957) | 0.956 | Title/text claim 0.9576; code is the R6 public stack, no newly released trained leg identified. | API score contradicts the implied new gain; no priority. |
| [degnonguidi/rnsa-best-public-score](https://www.kaggle.com/code/degnonguidi/rnsa-best-public-score) | 0.957 | R6 with accessible rostigor mirror, flip disabled in latest code. | Another R6 copy, not a new family. |
| [picond R6 readable](https://www.kaggle.com/code/picond/rsna-knee-9576-r6-v1-fixed-readable) | 0.957 | R6 + flip; one attached dataset slug is redacted in pulled metadata. | No extra component beyond the accessible R6 candidate. |
| [leoprovorov explanation](https://www.kaggle.com/code/leoprovorov/rsna-knee-0-957-explained-why-the-open-ensembl) | 0.957 | Explanation notebook; pulled input metadata contains a redacted source. | Context, not a separately verified accessible inference pipeline. |
| [prvsiyan/final-rsna-push](https://www.kaggle.com/code/prvsiyan/the-bee-s-knees-final-rsna-push) | 0.949 | Latest inputs now include the public R6 mirror; many historical versions. | No independent stronger released checkpoint identified. |
| [bulsahkecici/D3ALLLR2](https://www.kaggle.com/code/bulsahkecici/rsna-d3alllr2-submit-20261013) | 0.862 | Distinct standalone trained model and asset. | Too weak on available evidence to prioritize against v61 (L38/L39). |
| [masumhuq/v8](https://www.kaggle.com/code/masumhuq/rsna-knee-v8-58-study-weights) | none | Raptor + existing public reader, per-target weights; no scored new component. | No demonstrated gain. |

## R6 availability is the material change

Both accessible manifests are byte-identical:

- `heliosli/rsna-knee-r6-frozen-fe055406-w1`, dataset ID 12605688, attached version ID **20761842** in the 0.958 run.
- `rostigor/rsna-knee-r6-fe055406`, dataset ID 12606546, attached version ID **20763353** in goodpjw2008 V24.
- Manifest SHA-256: `6508ce6921eda986c885b2226fa55dd4d2aa8e5fc570b4c007c9a60c05bfc648`.
- Bundle: **`fe055406fad6a12f`**; four ConvNeXt-small checkpoints, crop 352, fluid/state stackers.
- This is different from v61's R7 **`8c7b666e27dc0e8f`**, and from nartaa's S6F0.
- Listings expose all four checkpoint filenames and supporting files. Actual checkpoint bytes have not been hashed in this audit.
- The 0.958 notebook's comment calls w1 private, but the current API file listing and manifest download succeed. Treat
  measured accessibility as evidence; do not infer availability from the stale comment.
- Dataset license is `other`; precise notebook/source license still needs confirmation before deriving a submission.
  No fresh external-data ruling was verified; D-032's previously accepted fastMRI risk remains relevant.

## What the 0.958 candidate changes

Published Raptor-slot share of the 224 model stays 0.35. Outer Raptor weights are 0.5 by default, with:

| Finding | Raptor share | R6 share |
|---|---:|---:|
| Lateral OA | 0.20 | 0.80 |
| PF OA | 0.60 | 0.40 |
| Synovitis | 0.80 | 0.20 |
| Baker's | 0.35 | 0.65 |

Medial OA remains 0.50. These are the author's published choices; their selection method/private validation is unknown.
No reader or S6F0 is added in this recipe. R224 does not use the added mirror stage in v61.

Author commit-run checks performed here:

- R6 receipt PASS, correct bundle, 3/3 scored; zero Raptor/compact failures.
- R6 output and both Raptor rank-output files are byte-identical between the public 0.957 and 0.958 recipes.
  Raw Raptor probability files differ; do not claim all raw stage outputs are identical.
- Independently recomputed the 0.958 recipe from its public stage outputs: maximum absolute difference
  `2.384185793236071e-08` after float32 conversion; official 12-label columns match.
- This validates the published placeholder artifact. It does not verify the hidden-test score or runtime on our copy.

## Recommended next action (not executed)

The next concrete candidate is an **unchanged reproduction of the public 0.958 recipe**, with exact input versions/hashes,
source license confirmation and parity against the author's outputs. Discuss and approve a design before a large build;
obtain approval before an unplanned Kaggle push/submission. Only after its own leaderboard result should we consider
whether anything from v61 transfers. Do not automatically add the reader/S6F0/mirrors or tune the published weight vector.

Evidence: L32/L42 require version/input identity checks; v56/v57 failed despite a displayed public claim. L40/L41/L44
support evaluating concrete new evidence, while L43's old-S6 failure does not test R6. L38/L39 argue against adding
unverified weak models merely for diversity. A higher public badge is a reason to reproduce, not proof of our future score.
