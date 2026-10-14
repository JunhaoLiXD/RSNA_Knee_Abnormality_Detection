# Silver push, 2026-10-14: two independent proposals and the conclusion

Status: proposal for the user (not yet a decision; record as D-033 when approved). Claude and Codex (GPT-6 Astra, high,
read-only, live web search) wrote independent proposals; the user stopped Codex's run before its final write-up, so its
part below comes from its log (`codex_silver.out` in the session scratchpad). Claims are marked as verified here or not.

## Situation (snapshot `external/lb/2026-10-14a`, 01:26 UTC)

5,952 teams; silver = top 5% = rank 297, bronze rank 595, both at 0.956; 169 teams at >= 0.957; the 0.956 block spans ranks
170-840, mostly code copies of heliosli's R7 notebook. Our best v47 = 0.956 at rank 417: about 120 ranks below silver
inside the block. Medals are decided on the private board (the public board is a subset of the test). **Runtime headroom
(verified):** v47 scored within 3.4 h of submission (submitted 16:04 UTC, rank change visible in the 19:27 snapshot), v46
within 3.9 h, so at least 5 h of the 9 h limit are free.

## Evidence that shapes both proposals (STATUS lessons)

- Large hidden-digit gains came only from adding a different public model family at a small outer weight: the reader on
  the old S6 host +211 witnesses (L33) and on R7 +191 (L37).
- Weaker models of the same family or the same target hurt or did nothing: v44 ROI experts 0.955 (L38); our own legs
  (L21, L29-L31); v41's weight change. Our own training recipe is capped at 0.934-0.937 (L35).

## Claude's proposal (written first; candidates then verified)

Diversity stacking with the reader rule (each new component a separate outer rank component at fixed weight 0.10, v47's
failure guards, judged by rank crossing; winners combined by the same rule; no weights fitted on the public board).
Candidates after verification: hengck23's MaViT-288 (a different architecture, 0.935, about 1.5 s/study); a trimmed
"Speedy Raptors" stack (DINOv2/RadImageNet families, as in our v05; heavy); R224 last (same family, L38 risk). One
candidate was withdrawn on inspection: prvsiyan "The bee's knees" (0.949) is a tutorial around nartaa's CoAtNet, not a new
family, and it does use the OAI weights.

## Codex's proposal (from its log, before it was stopped)

"A capped inference-and-ensemble campaign, with no new training program: test R224 first, then the MA-ViT contribution and
R7's existing TTA path, while reserving time for a genuinely new public release ... retain two final candidates with
meaningfully different failure risks." Its verified points:
- **R7 flip-TTA is label-safe** (verified here in `compact_infer.py` lines 30-38 and 198-237): coronal and axial windows are
  flipped on the patient's left-right axis, sagittal windows reversed along the slice axis with `rel_pos` negated, the
  coronal bilateral views exchanged, the outputs permuted (Medial <-> Lateral Meniscus, Medial <-> Lateral OA), MCL from the
  plain pass. **R7 was trained with this mirror** (`run_config` `"mirror": 0.5`, verified), so the TTA matches training;
  the bundle simply ships with `flip_tta: false`. (Claude's landscape note of 10-13 doubted label safety: withdrawn.)
- hengck23's dataset holds the MaViT checkpoint and code under an MIT licence (Codex; to re-check on the dataset page).
- The block bounds above (verified).

## Conclusion

Both proposals converge: **no new training; three inference-only probes from public assets, each judged alone by rank
crossing against v47, then the winners combined at fixed rules.** Ranked by expected value per submission:

| Probe | Change to v47 | Why | Cost | Risk |
|---|---|---|---|---|
| **A: R7 flip-TTA** | `--flip-tta` for the R7 worker (its own, training-consistent mirror) | TTA that matches the training augmentation usually adds a little to every column; no new model | R7 forward about 2x (decode shared); one commit run | the bundle author left it off (reason unknown); jingshuifu's public flip-TTA notebook is unscored |
| **B: MaViT at outer 0.10** | hengck23 MaViT-288 as a fourth component (reader rule, own process group, fallback) | a different architecture, as strong as the reader; the reader rule worked twice | about 35 min for 1,300 studies; licence MIT (claimed) | loads with `strict=False` (gate: all keys must load); unknown training labels |
| **C: R224 in the Raptor slot** | nartaa's 224-px CoAtNet at 0.35 of the Raptor slot (public recipe) | public notebooks with it display 0.956; its author claims a rank gain | one more CoAtNet pass | same family, weaker (0.945): L38 says it may hurt |

Schedule: 10-14 build and commit-run A and B, submit A, then B after A is judged (one submission that can change the best
at a time; each scores in about 3.5 h); 10-15 C, then the combination of the winners (e.g. A + B); 10-16 to 10-19 one
combination at a time and persistence checks, plus any genuinely new public release; 10-20 final picks (first: the best
combination; second: a submission with a different failure risk, to be decided with the user: v45 for fastMRI, or v15 for
OAI). Not doing: weight searches on the public board, own-model training, ROI experts, reader-weight tweaks.

Honest odds: silver needs about 120 ranks inside the block on public, and the private board decides. With one or two
successful probes of the reader's size the public silver line is within reach; the private outcome is far less certain.
Rough estimate: about 25-35% for a private silver with the plan, under 10% without it.

## Update 2026-10-14 12:00 UTC: results and new public recipes

Results: v48 (A, R7 flip-TTA) 0.956, above v47 by 6 witnesses (Kaggle's best since); v49 (B, MaViT) **0.955, rejected**
(L39); v53 (A + C: flip + R224 with the failure-path fix) submitted 11:40 UTC as "R224 on top of v48".

Recipe analysis (sub-agent, notebooks pulled to `external/kernels/*_20261014/`, scored versions read from Kaggle's version
pages):
- Several displayed scores belong to older versions: jingshuifu's "a224 topview/multiview" 0.956 and "raptor
  topview/multiview" 0.954 are V1 copies of other notebooks; their view-arm code (dreaddevelopment CoAtNet checkpoints v5/v8/v10,
  0.926-0.928 alone, probably fed nartaa's 96-slice pipeline instead of their own 64-slice one) is unscored. Not used.
- Measured weight variants: R7 with W_RAPTOR 0.3 -> 0.955 and A224 blend with W_RAPTOR 0.3 -> 0.955 (both one step below
  0.956); A224 = 0.35 -> 0.956. Confirms: no weight search.
- varshithakolupuri "One Free Flip, 68 Ranks Up" (10-14, unscored on the API; the rank claim is the author's): **not** R7's
  flip; it adds nartaa's anatomical mirror TTA (the one the R384 model already uses) to the R224 stage. New to our stack:
  **v54 = v53 + that mirror on R224** (the three `[s9]` hunks, asserted verbatim).
- rudrpratapsingh "Four public models, one rank blend" (unscored): R7 + old S6 at 0.5/0.5 in the ConvNeXt slot, R224 in the
  Raptor slot; same-family addition (L38 risk), about 1.6 h more runtime. Possible later probe, not now.
