# v40 design: two capped anchor probes on v37 (R1 reader, A1 weights), plus the planned v36 W test

Status: revision 2 after the Codex review (section 5; required changes accepted); approved by the user 2026-10-12 (D-030); build notes in section 6. Evidence: STATUS versions v32-v39, lessons L20-L32; decisions
D-022 (rank-crossing rules), D-024, D-028, D-029 (the leg line has stopped); `v32-s6-anchor-design.md` sections 8-10.

## 1. Situation (2026-10-12 ~12:00 UTC)

- Best public submission: **v37 0.954** = heliosli's public notebook version 2 (nartaa OAI CoAtNet-384 + heliosli S6, old
  bundle `209a32c8b50a6b1c`) at CoAtNet:S6 rank weights **0.5:0.5**; it beat v33 (v32 at 0.7:0.3 + our fold-0 leg) by rank
  crossing (50 witnesses, confirmed). v35 (v32 + three-fold leg) 0.953; v39 (v37 + fold-0 leg) 0.954 without crossing.
- Leaderboard 11:53 UTC: rank 506 of 5,819 (347 at 03:18); 687 teams at 0.954, 196 at >= 0.955; silver cut rank 290 and
  **bronze cut rank 581 both at 0.954**; about 18 ranks lost per hour inside the 0.954 block.
- Public notebooks: nothing usable above 0.954 (0.956 = the author's version 1 with an unavailable R6 S6; 0.955 uses a
  hidden input). Many 0.954 notebooks are three-way blends (CoAtNet + S6 + goodpjw2008 2.5D ConvNeXt reader), e.g.
  `external/kernels/romantamrazov__rsna-knee-dinosaur-the-last_20261011/`,
  `external/kernels/goodpjw2008__rsna-knee-coatnet-2-5d-convnext-mil-lb-0-954_20261011/`.
- v36 (D-027): arm P alone 0.937 (passes 0.936 vs v14 0.934, below the 0.940 expansion threshold); arm W +0.0010 val vs
  control (not flagged), its LB test is the rule-2(a) fallback. Cross-hardware noise about 0.001.
- Submissions: 5 per day; deadline 2026-10-22 (final selection of two); large experiments stop 2026-10-19.

## 2. Candidate probes (all on v37's anchor, no new training)

| # | Probe | Rationale | Risk |
|---|---|---|---|
| A1 | CoAtNet:S6 = **0.4:0.6** | 0.5:0.5 beat 0.7:0.3 in the hidden digits (v37 > v33); S6 alone is stronger on gold (0.9265 vs 0.9229, descriptive) | public-LB weight search; the direction may not continue |
| A2 | CoAtNet:S6 = **0.3:0.7** | same, one step further | as A1, larger |
| R1 | v37 + the public goodpjw2008 2.5D ConvNeXt reader as a third anchor component at a fixed weight (or reproducing one public three-way 0.954 notebook unchanged) | the reader helped the CoAtNet before (v17 0.950 > CoAtNet alone 0.949; L26); three-way blends populate the 0.954 block above us | adds a component and a runtime; weight choice is a search; reader's pylibjpeg wheel gap (STATUS open question) |
| W | v36 arm W fold-0 alone (planned rule 2(a)) | completes the v36 diagnostics; no effect on the team score | none for the rank |

Proposed caps: at most three anchor probes, sequential (one own submission scoring at a time), each judged against the
running best by display or by the rank-crossing test (>= 20 stable witnesses, none reversed, persistence); a probe that
does not demonstrably beat the incumbent is "no improvement"; no combination of winners without its own test; stop on
2026-10-17 to leave time for final verification. Picks stay v37 + v15 unless a probe wins.

## 3. Questions for the review

1. Is spending submissions on anchor probes sound given the slide, or is it a public-LB search that the earlier decisions
   warned against? What would you change (which probes, order, caps, adoption rule)?
2. Which probe has the best expected value: A1, A2 or R1 (and in which R1 form: reproduce a public three-way notebook
   unchanged, or add the reader to v37 at a predeclared weight)? Read the two pulled three-way notebooks for their weights
   and components.
3. Should the v36 W test still run now, and what should happen to the v36 line (X = W + P fold 0, or stop)?
4. Final picks: keep v37 + v15, or should the second pick change (for example v30, a non-S6 OAI backup)?

## 4. Revised plan (revision 2, frozen before any probe scores)

| Order | Version | Definition | Gate |
|---|---|---|---|
| 1 | `v40_submit` (R1) | v37 unchanged, then the public goodpjw2008 2.5D ConvNeXt reader (3 folds) as one outer component: `final = rank(0.90 * rank(v37 output) + 0.10 * rank(reader))`, uniform weight 0.10 for all 12 findings (a conservative design choice, not an estimated optimum); any reader failure keeps v37's output | commit run: v37 parts equal to the v37 run; reader decoders available (fixture), all three checkpoints loaded, slot and coverage diagnostics, bounded runtime with a process-group deadline, exact-anchor fallback; a skipped reader is not a completed R1 |
| 2 | `v41_submit` (A1) | **original v37** with CoAtNet:S6 = 0.4:0.6 for **all 12 findings** (`W_RAPTOR`, `W_OURS` and the three OA overrides in `W_RAPTOR_C`), nothing else changed; independent of R1's result, never combined with it | commit run: the 12 effective weights asserted; failure masks and rank semantics unchanged; outputs recomputed |
| - | v36 W | v36 arm W fold-0 alone (D-027 rule 2(a), the frozen fallback) | as P; X = W + P fold 0 only if W displays >= 0.936; one expansion only at >= 0.940 |

Adoption: execution gates passed, then a higher displayed score or >= 20 stable crossings with none reversed, unchanged
witness ordering and later persistence; one own submission scoring at a time; an unresolved comparison keeps the incumbent.
Witnesses resolve public ordering only (not private generalisation). **Non-renewable budget**: R1, A1, W, the conditional
X, and (only after a >= 0.940 fold-0 result justifies one four-fold expansion) one separately reviewed non-OAI hedge blend:
**at most five further submissions in total**; no A2, no winner combinations, no further OAI-leg blends. Anchor probing
closes on 2026-10-17; model development stops on 2026-10-19; 2026-10-20/21 verify the final artifacts. Picks stay
**v37 + v15** unless a probe wins (v30 remains the operational non-S6 backup; changing the hedge would change the objective).

## 5. Codex review (GPT-6 Astra, high, read-only, 2026-10-12) and disposition

Verdict: revise before proceeding; one reader probe and one small weight probe are defensible public-LB searches with
uncertain private value; drop A2. Codex reproduced the snapshot counts (rank 506, 687 at 0.954, 196 at >= 0.955) and the
v37/v39 crossings.

| # | Finding (severity) | Verified | Disposition |
|---|---|---|---|
| 1 | The DINOsaur pull is not a simple three-way blend: it adds a CoAtNet-224, Synovitis residuals and Baker's/Contusion/Lateral-OA adjustments, some active only at >= 64 studies (high) | Codex (cells 32-33), not re-read | **Accepted**: no unchanged reproduction as R1 |
| 2 | Higher-ranked authors do not show that these notebooks beat v37; scoring versions unknown (high) | Yes (L32) | **Accepted**: weak evidence only |
| 3 | A1's direction is confounded: v37 vs v33 also removes our leg; vs v32 it changes the S6 path (medium) | Yes | **Accepted**: A1 exploratory; A2 dropped |
| 4 | A weight-only edit leaves the three OA findings at 0.5 (`W_RAPTOR_C` overrides; fusion uses `wr`, `1 - wr`) (high) | Yes (v37 stage 3) | **Accepted**: all 12 effective weights set and asserted |
| 5 | Witness counts resolve public ordering, not generalisation; zero crossings cannot separate a loss from a tiny gain (high) | Yes | **Accepted**: wording; no permission for more searches |
| 6 | The cap allowed renewal through combinations (medium) | Yes | **Accepted**: whole-sequence cap of five, no combinations |
| 7 | Reader completion needs decoder fixtures, all checkpoints, coverage diagnostics, a bounded runtime and an exact-anchor fallback (medium) | Codex (goodpjw2008 final cell), not re-read | **Accepted**: R1 gates |
| - | Both pulls start from CoAtNet:S6 0.7:0.3 (old S6) and add the reader through an outer per-finding rank blend (goodpjw2008 weights 0.03-0.35, DINOsaur 0.015-0.20) | Codex | Recorded; R1 uses one uniform 0.10 instead |
| - | D-026 has no entry in `decisions.md` | Yes | Recorded: D-026 never existed as a decision; superseded by this plan if approved |

## 6. Build notes (2026-10-12, before any probe run)

**R1 = `notebooks/v40-submit.ipynb`** (20 cells): v37's header and receipt cell replaced as in v39, v37's author cells 2-9
unchanged (asserted), then: anchor check (`v40_anchor_receipt.json`), saved anchor, the reader's three source files copied
unchanged from the pulled goodpjw2008 0.954 notebook (equal to v17's up to trailing whitespace, asserted), a wrapper
`v40_reader.py`, a launch cell and a blend cell.

- **Reader path.** The wrapper calls the reader's own `infer.run` with its defaults (16 windows, batch 4, 4 loader workers)
  on the GPU with the most free memory, so predictions are those of the public CLI; it adds diagnostics only (per-series
  raw/bad/kept slice counts, transfer syntaxes of files that fail to decode, the pydicom decoder table of its environment).
- **Decoders (verified).** The reader dataset ships pylibjpeg wheels for cp311/cp312 only; on the pinned Python 3.13 image
  the author's install step fails ("No matching distribution found for pylibjpeg-libjpeg", v17 log), so it is not copied.
  After v37's S6 stage the environment has pydicom 3.0.1 and Pillow 12.3 with JPEG 2000 (v39 receipt), i.e. uncompressed,
  RLE, JPEG baseline/extended and JPEG 2000 decode; JPEG Lossless and JPEG-LS do not. This is the same reader environment as
  v17 (0.950) and the public three-way 0.954 notebook. The dataset contains no compressed fixtures (the author's fixture
  check finds none), so the commit-run decoder gate is: zero failed files on the placeholder studies plus the recorded
  decoder table. The author's claim that the hidden test has compressed DICOMs is unverified.
- **Guards (hidden run).** Launched only with >= 45 min left before the 8.6 h deadline (1.5 x 29 min projected from v18:
  76 s for 58 studies); own process group, killed at the deadline. Used only if: three checkpoints found once each, exit
  code 0, not killed, receipt `done`, output with the 12 labels for exactly the test studies, finite, no constant column,
  and at most half of the studies without a decodable slot (catastrophic decoding failure only: the public notebooks use
  the reader with whatever decodes, so a stricter threshold would silently turn R1 into v37). Otherwise v37's output.
- **Local tests** (`test_v40_blend.py`): the success path equals an independent `rank(0.9 rank(v37) + 0.1 rank(reader))`;
  16 failure cases keep the anchor exactly (not launched, killed, exit 1, receipt absent/truncated/not done, output
  absent/empty, missing/extra/duplicate study, NaN, missing column, constant column, 151 of 300 studies without a slot,
  setup error); the wrapper on stub reader modules records the expected counts and leaves predictions unchanged.
- **Commit-run gates** (`check_v40_gates.py`): CoAtNet ranks byte-equal to v17; S6 output and saved anchor equal to the v37
  run; reader used (exit 0, no kill, no setup/read error); three checkpoints; reader source equal to v17's; decoding clean on
  the placeholder studies; decoder table recorded; reader probabilities within 1e-3 of v17's reader run; blend recomputed;
  format.

**A1 = `notebooks/v41-submit.ipynb`** (11 cells): v37 with stage-3 `W_RAPTOR, W_OURS = 0.4, 0.6` and
`W_RAPTOR_C = {'Medial OA': 0.4, 'Lateral OA': 0.4, 'PF OA': 0.4}`, one assertion of all 12 effective weights, comments
updated; failure handling unchanged. Gates (`check_v41_gates.py`): CoAtNet and S6 outputs equal to the v37 run, receipt
weights, no failures, the submission recomputed at 0.4 / 0.6 with v37's rank semantics (the same formula reproduces v37's
own submission at 0.5 / 0.5 to 1.3e-8), different from v37, format.

**W:** `v36-submit` rebuilt for arm W (`build_v36_submit.py W`; checkpoint cfg: v36 / W / fold 0 / 320 px / unit weights);
`lingxd/rsna-knee-v36-weights` gets a new version with P and W. W alone cannot change the team's best score, so it may score
while R1 or A1 is scoring (as v36 P did beside v39); R1 and A1 never score at the same time.
