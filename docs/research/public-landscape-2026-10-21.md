# Public landscape 2026-10-21: hedge view for the final pair

- Date: 2026-10-21 ~04:30 UTC
- Method: Kaggle web `ListKernels` (competition 154281, `bestPublicScore`), 100 notebooks by score and 100 by last run,
  from the built-in browser (no sign-in needed); inputs (`dataset_sources`) of nine candidates read with
  `kaggle kernels pull -m` into the session scratchpad (not kept). Claims below are from metadata and a keyword scan of the
  code, not from runs.
- Question (user, D-036): besides higher scores, what hedges do others use, and is there a structurally different public
  recipe with a decent score that could serve as the second final pick?

## Findings

1. **Nothing above 0.958.** Six notebooks show 0.958 (versia-7 = V25 byte for byte; goodpjw2008 V25; lavinwins x2;
   heliosli x2), all known and covered by v62/v67/v68/v69.
2. **Every public notebook at >= 0.950 attaches nartaa's OAI-trained CoAtNet** (`nartaa/rsna-knee-publication-swa-weights-20261007`).
   The ones whose titles suggest another family use it too: romantamrazov "DINOsaur the last" (0.954) and matterhorn3838
   "Velciraptor DINOsaur" (0.954) = CoAtNet-384 + heliosli compact-v1 (old S6) + goodpjw2008 reader; laimerbotrolenk "four
   model ensemble" (0.957) = CoAtNet + R7 + nartaa S6F (all-data S6), no R6; mkhamzanov b1-ctrl (0.956) = heliosli R7 base +
   reader; seanmoch tri-reader (0.950) and masumhuq v8 (0.950) = CoAtNet + reader.
3. **The 0.950-0.958 range is one family with two axes of variation**: the compact model (old S6 / R7 / R6 / S6F) and the
   blend weights (uniform vs per-finding). No public notebook in this range drops the CoAtNet.
4. Without the CoAtNet, the best public evidence is a compact model alone (nartaa `rsna-knee-s6fall-solo` 0.950) and our
   own non-OAI v15 (0.944, D-018).

## What this means for the hedge

Two different risks can be hedged, and no single second pick covers both:

| Risk | Hedge | Cost on the public LB | Our candidates |
|---|---|---|---|
| Per-finding weights fitted to the public split (L51) | uniform weights, same models | about one display step (v71 0.957) | v85, v87 (scoring / to be pushed) |
| A ruling against OAI-trained weights (open question; host statement 09-21 says OAI is allowed if freely accessible) | no CoAtNet | about 0.006-0.014 | v15 (0.944); a compact-only stack (R6 + R7 + reader) would be new and untested |

The second risk is shared by every team at >= 0.950, so if it materialised the whole top of the board would move; the
host statement (STATUS open questions) makes it less likely than once assumed. A compact-only (non-OAI) build is possible
from v86's cells (drop the Raptor stages) but its score is unknown; it is a user decision because it trades expected score
for rule-risk cover.
