# Re-plan after v40 (2026-10-12 ~19:30 UTC): independent Claude and Codex views, merged

Status: proposal for the user's decision (amends D-030 and shapes D-031 if approved). Claude and Codex (GPT-6 Astra, high,
read-only) answered the same question without seeing each other's text. Evidence: STATUS v32-v41, L20-L33;
`external/lb/2026-10-12e`, `2026-10-12f`; `v42-roi-experts-design.md` revision 1 and Codex's review of it.

## 1. Situation (both verified the crossing)

v40 = v37 + public reader at 0.10: 0.954 displayed, rank 524 -> 235 of 5,853, 211 stable witnesses down, none up, stable order
unchanged; persistence pending. 19:01 UTC: 216 teams >= 0.955; we are 19th of 753 teams at 0.954, 57 places inside the silver
cut (rank 292). Teams >= 0.955 keep growing (144 -> 216 in about 21 h); if more than about 295 reach >= 0.955, the silver cut
moves to 0.955. The 211 witnesses are not independent validation and do not convert into an AUC gain; persistence confirms the
public order only.

## 2. Agreement

| Item | Merged position |
|---|---|
| Priorities | (1) protect the deliverable and the value of the two final picks; (2) a bounded set of anchor-side probes (L33); (3) one Dense-P test; (4) a shrunk ROI option; (5) cancel X |
| Protect | v40 frozen as an immutable baseline after persistence (exact notebook version, inputs, weight hashes, submission ref); new work never overwrites it; gold-58 and teacher-leaky validation are diagnostics only (L20, L28, L30, L31) |
| Anchor probes | allowed as a **closed, predeclared set of at most four submissions, ending 10-16**, sequential (one anchor candidate scoring at a time), judged against the incumbent by display or rank crossing; no recursive search, no per-column hill climbing, no stacking of all winners; not renewable |
| ROI | shrink to **Lateral + Medial Meniscus, fold 0, one fixed submission** on the then-incumbent; Codex's nine required changes first; 10-13 pilot gate (>= 80% usable, <= 5% wrong, cache <= 13 GPU h); **no end-to-end submission by 10-16 -> stop**; no PF/ACL wave; folds 1-2 only if the package displays >= 0.956 and beats the incumbent; hidden-digit wins keep a candidate but fund no expansion (L31) |
| Dense-P | finish; one standalone LB test; < 0.944 ends; >= 0.944 and ROI failed -> one fixed v40 + Dense-P at outer **0.10** (not 0.25) |
| X | cancelled (W 0.936, P 0.937: small effects, no strong new model; X untested, not failed) |
| Second final pick | **v15 is not automatic**: it only pays if OAI-based submissions are voided without disqualifying the team, and no pick protects against team-level disqualification. Decide on 10-20 by "which candidate is most likely to rescue a medal when the first pick misses", without new rule evidence. Codex's default: v40 + v37 (or a structural winner + v40); Claude: decide on 10-20 with a short analysis, noting v37 is nearly identical to v40 (v40 = 0.9 v37 + 0.1 reader), so a moderately different strong candidate may hedge better |
| Budget | research submissions <= 7 plus 2 for repairs; Kaggle <= 17 h before the 10-17 refresh (2 h reserve), <= 12 h after; unspent budget is not a reason to start work |

## 3. Differences

| Point | Claude | Codex | Merged proposal |
|---|---|---|---|
| Reader-weight probes | one probe at 0.20 | two probes at 0.05 and 0.15 around 0.10 | **0.15 first; 0.20 only if 0.15 beats v40; no 0.05** (0.10 was a conservative pick that produced the largest crossing so far, so the informative direction is upward; at most two weight probes either way) |
| Per-finding public reader weights | excluded (fitted on gold-58) | one vector shrunk 50% towards uniform 0.10 | include as the third probe (one vector, no column picking) |
| Fourth probe | another public model family at 0.10 | v41 + reader 0.10 if v41 beats v40; else one qualified public group at 0.05 with independent evidence and runtime budget, cancelled if none by 10-15 | **Codex's rule** (Codex: the old DINO/RadImageNet components are weak, `anchor-components-2026-10-06.md`; L33 shows this reader helps, not any weak family) |
| Odds | public >= 0.955 by 10-19 about 25-30%; private silver about 50% | private-AUC gain >= 0.001 vs v40: anchor probes 15-25%, ROI 10-20%, Dense-P 5-10%, X < 5% (correlated); any medal 50-70% and silver or better 20-35% with the plan (40-60% / 15-25% frozen); gold < 2% | both are subjective; Codex is more pessimistic about private silver (late progress of other teams, private reshuffle) |

## 4. Calendar (merged)

| Date (UTC) | Work | Submissions |
|---|---|---:|
| 10-12 | v41 scoring; Dense-P finishes; ROI design revision 2 | 0 (used) |
| 10-13 | persistence snapshot before any submission; reader 0.15; Dense-P alone; ROI pilot on Kaggle | 2-3 |
| 10-14 | per-finding weight probe (or reader 0.20 if 0.15 won); ROI full cache only if the pilot passed | 1-2 |
| 10-15 | LM + MM experts; ROI submission if ready; fourth-probe eligibility locked | 1 |
| 10-16 | fourth probe; latest ROI submission; anchor probing closes | <= 2 |
| 10-17/18 | conditional ROI expansion or the Dense-P blend (one of the two) | <= 1 |
| 10-19 | freeze models and the candidate list | 0 |
| 10-20/21 | verify exact versions and dependencies; decide the two final picks | repairs only |

## 5. Decisions needed

1. Amend D-030: cancel X, cap the old sequence at the three used submissions, and open the closed set of at most four anchor
   probes above (reader 0.15 -> 0.20 rule, one shrunk per-finding vector, the fourth-probe rule).
2. Approve the shrunk ROI line (D-031) and Dense-P's follow-up as above.
3. Final picks: v15 no longer automatic; decide on 10-20.
