# RSNA_Versia_5

- Source: https://www.kaggle.com/code/evgendvorkin/rsna-versia-5 (version 18, pulled 2026-10-01)
- License: Apache 2.0 (shown on the Kaggle page)
- Public LB: 0.943 (as of 2026-10-01); 262 votes, the most-voted 0.943 notebook
- Local copy: external/kernels/evgendvorkin__rsna-versia-5/

## What it is

An annotated reproduction of the Jiwei Liu 0.943 notebook (526-line diff, most of it
Markdown). 25 Markdown cells explain each stage (partly in Russian) and record the public
score history with the change that produced each step (author's text, consistent with the
code we read):

| Public LB | Change |
|---|---|
| 0.937 | prvsiyan: four Raptor CoAtNet arms incl. a reverse-channel view; global CoAt weight 0.60 |
| 0.940 | renta.k: Lateral Meniscus routed 100% to the CoAt side |
| 0.941 | Mattia Angeli: per-target routing (ACL 0.75, MM 0.80, LM 1.00, LOA 0.75, Fx 0.75), maxspan weight 0.55 -> 0.60 |
| 0.942 | maverick: A5 0.45 -> 0.52, Rad 0.50 -> 0.55, Rad second pass 0.15 -> 0.20, residual-gated + D4 CoAt |
| 0.943 | Mattia v34 / Jiwei: four CoAt readers at 0.25 each, probability mean then rank |

Every step after 0.937 is a weight or routing change on the same checkpoints, chosen by
public LB. Attaches `metaresearch/dinov2` base in addition to small (verified in metadata).

All technical details: see the
[root analysis](kernel-mattiaangeli-bend-the-knee-to-speedy-raptors-the-original.md).

## Value for us

Best human-readable map of the stack; useful as documentation when we reproduce the
anchor. Not a separate candidate.
