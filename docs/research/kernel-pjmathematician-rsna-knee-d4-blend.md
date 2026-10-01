# rsna-knee-d4-blend (and rsna-knee-d4-lite)

- Source: https://www.kaggle.com/code/pjmathematician/rsna-knee-d4-blend (version 3, pulled 2026-10-01)
- Sibling: https://www.kaggle.com/code/pjmathematician/rsna-knee-d4-lite (version 1, pulled 2026-10-01)
- License: Apache 2.0 (both, shown on the Kaggle pages)
- Public LB: d4-blend 0.946, d4-lite 0.945 (as of 2026-10-01). These are the two highest
  public notebooks.
- Local copies: external/kernels/pjmathematician__rsna-knee-d4-blend/,
  external/kernels/pjmathematician__rsna-knee-d4-lite/

## What it is (verified in code)

The Jiwei Liu 0.943 public stack (316-line diff) plus an extra "our leg" stage appended at
the end. The two notebooks differ by 30 lines: d4-blend runs three student arms
(`S_dist`, `S_coat`, `S_cnxl`) at 54 windows instead of one arm at 36, and adds a
coverage / tie-fraction gate on the private leg output.

Final blend (verified):

```text
final = rank( (1 - 0.45 - w2) * rank(public stack)
              + 0.45 * rank(our fleet leg)
              + w2   * rank(our core leg) )      # w2 = RSNA_EFF_W, default 0.0
```

The private leg reads `rsna-knee-eff6-assets` and `rsna-knee-ens14-assets`, which are
**private datasets**: the Kaggle page lists three "[Private Datasource]" inputs and the
pulled `kernel-metadata.json` has three empty dataset slugs. The leg's architecture and
training are therefore unknown. The code comments claim "Our legs measured 0.75-0.89
[rank correlation] against the public ones offline" (author's text).

## Reproducibility

**Not reproducible by others.** If the private assets are missing, the code soft-fails to
"public only". This is visible on the board: forks such as
`yamadan96/rsna-knee-d4-public0946` and `ryokucha/rsna-knee-d4-blend-0946-ours10` score
0.943, the public-stack score.

## Takeaway

The only public evidence of how 0.946 is reached: a diverse, independently trained model
family rank-blended at about 45% into the 0.943 stack added about +0.003 public LB. This
is the pattern we should copy with our own models.

Backbone, input, labels, TTA, run time and external weights of the public part: see the
[root analysis](kernel-mattiaangeli-bend-the-knee-to-speedy-raptors-the-original.md).
The notebook budgets its leg from the remaining 9 h (`_proc_age_h`), so runtime is close
to the limit by design.
