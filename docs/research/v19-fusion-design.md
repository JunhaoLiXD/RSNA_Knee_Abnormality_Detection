# v19/v20 fusion design: v17 anchor plus our v13 arm-N leg

Status: revision 2 after the Codex review (2026-10-08, section 5). Inputs: v17 (public 0.950,
D-019), v18 gold diagnostic (`results/v18/run1/`), v13 arm-N 5-fold gold predictions, STATUS L13,
L15-L18. No training; two submission notebooks and their commit runs.

## 1. Evidence

### 1.1 Public scores (3 decimals)

| Entry | Content | Public LB |
|---|---|---:|
| nartaa 0949 | CoAtNet-384 SWA alone (OAI-trained), mirror TTA | 0.949 |
| v17 | CoAtNet + goodpjw2008 ConvNeXt reader, per-finding rank weights TW (mean 0.162) | **0.950** |
| reader alone (author) | ConvNeXt-tiny 2.5D, 3 folds | 0.929 |
| v13_submit | our arm-N ConvNeXt-tiny 2.5D, 5 folds, OOF-teacher targets | 0.936 |
| v15 / v16 | v05 stack + N at w 0.30 / 0.45 | 0.944 / 0.943 |

TW (from the v17 source): Baker's 0.35, Contusion 0.30, Medial OA 0.25, ACL 0.25, Medial Meniscus
0.20, MCL 0.20, Lateral Meniscus / Fracture / Lateral OA / PF OA 0.08, Effusion 0.04, Synovitis 0.03.
The source's comments quote per-finding AUCs (e.g. Baker's 0.976 vs 0.940), so TW was probably set
on gold-58.

### 1.2 Gold-58 (v18)

No model was trained on these 58 studies, but they were used for selection: the CoAtNet checkpoint,
probably TW, and our own versions. The bootstrap resamples fixed predictions and ignores those
selections; `P(<=0)` is the share of non-positive resampled gains, not a probability of failure.

| Candidate | Gold macro AUC | vs v17 (paired bootstrap, 2000) |
|---|---:|---|
| CoAtNet alone | 0.9228 | -0.0017 (CI -0.0043 to +0.0007) |
| v17 = CoAtNet + reader (TW) | 0.9245 | - |
| CoAtNet + N (TW; N replaces the reader) | 0.9257 | +0.0013 (CI -0.0012 to +0.0039) |
| CoAtNet + reader (TW) + N (TW/2) | 0.9264 | +0.0019 (CI +0.0001 to +0.0043) |
| **v17 + N, global w 0.15** | 0.9264 | +0.0019 (CI -0.0010 to +0.0052, P(<=0) 0.10) |
| **v17 + N, global w 0.25** | 0.9286 | +0.0041 (CI -0.0007 to +0.0093, P(<=0) 0.04) |
| v17 + v05 proxy, global w 0.15 | 0.9266 | +0.0021 (CI -0.0005 to +0.0052) |

Within-class noise correlation on gold (probit ranks, pooled): N-CoAtNet 0.809, reader-CoAtNet
0.786, **N-v17 output 0.827**, N-reader 0.838, v05 proxy-CoAtNet 0.841, N-v05 proxy 0.867. Per
finding (gold AUC, N vs reader): N is stronger on MCL (0.966 vs 0.946), Effusion (0.980 vs 0.882),
Medial OA (0.988 vs 0.981) and Fracture (0.942 vs 0.932); weaker on ACL (0.964 vs 0.977), Lateral OA
(0.820 vs 0.855), Synovitis (0.778 vs 0.800) and Baker's (0.971 vs 0.984); similar elsewhere.
Against the CoAtNet, N is stronger on MCL, Medial OA, Lateral OA, Effusion and Contusion.

Gold-to-LB offsets differ by model (CoAtNet 0.923 -> 0.949, +0.026; N 0.920 -> 0.936, +0.016;
reader 0.915 -> 0.929, +0.014): gold weights are a weak guide to LB weights.

### 1.3 Scenario analysis with the binormal blend model (not an identified estimate)

The single-number binormal model (STATUS L15, L18) cannot identify a common noise correlation from a
per-finding rank fusion with unequal weights, and the 0.949 -> 0.950 step may be close to zero
after rounding. With that caveat: matching v17 (CoAtNet 0.949 + reader 0.929 at the mean TW 0.162 ->
0.950, rounding intervals sampled) needs a reader-CoAtNet correlation of 0.80-0.88 (median 0.84);
the interval reflects rounding only. On gold the same pair is 0.786, about 0.05 lower.

The relevant quantity is N against the **v17 output**, not against the CoAtNet: 0.827 on gold,
about 0.88 on the LB scale if shifted like the reader. Sensitivity for v17 (0.950) plus N (0.936):

| N-v17 correlation | w 0.15 | w 0.25 |
|---|---:|---:|
| 0.84 | 0.9516 (+0.0016) | 0.9520 (+0.0020) |
| 0.86 | 0.9512 (+0.0012) | 0.9514 (+0.0014) |
| **0.88** | **0.9507 (+0.0007)** | **0.9507 (+0.0007)** |
| 0.90 | 0.9503 (+0.0003) | 0.9500 (+0.0000) |
| 0.92 | 0.9498 (-0.0002) | 0.9494 (-0.0006) |
| 0.94 | 0.9494 (-0.0006) | 0.9487 (-0.0013) |

w 0.15 breaks even up to a correlation of about 0.91 and loses little beyond; w 0.25 has the same
centre but a wider downside. w 0.15 is the conservative test, w 0.25 a probe of a larger weight. No
gain is guaranteed; the public LB of the two entries is the measurement.

## 2. Proposal (pre-registered)

Two explicit ensembles (D-017), both `final = rank((1 - w) * rank(v17 output) + w * rank(N))` per
finding, where the v17 output is the unchanged v17 pipeline (CoAtNet + reader + TW fusion) and N is
the v13 arm-N 5-fold leg as in v13_submit / v15_submit:

- **v19_submit: w = 0.15**
- **v20_submit: w = 0.25**

Global outer weights, not per-finding: per-finding weights fitted on 58 studies would be tuned to
noise, and TW itself is probably gold-fitted already. No other weights or variants are submitted
from this design.

Implementation: v17's cells unchanged (its final `submission.csv` becomes the base, saved as
`vNN_base_submission.csv`), then the v15 leg cells (v13_submit leg script, weight checks, reference
and OOF checks) and the v15 blend cell with the base in place of the v05 anchor, changed as below.
Docker image: v17's (`2757e0c...`), where 0.950 was measured.

Changes to the inherited leg and blend cells (Codex findings 3-5):

- **Deadline:** one absolute deadline for the leg (notebook start + 8.0 h, minus 15 min for writing
  outputs). Each shard is waited for with the time left to that deadline only; on expiry the
  shard's process tree is killed. Inside the leg script the preparation pool is shut down with
  `cancel_futures=True` when its time limit is reached (today a `break` inside the `with` block
  still waits for every submitted job).
- **OOF check:** one reference study in each of the five folds (folds 2 and 3 added from the local
  OOF files; their DICOMs are in `train_series`), tolerance 1e-3 instead of 0.01 (measured
  differences so far <= 5.5e-5).
- **Use of the leg** (all required, otherwise the base is submitted unchanged): both shards
  finished with status done; reference check passes with `byte_equal` true for all three studies
  on this image (a thumbnail-only pass is not enough here, the preprocessing has not run on this
  image before); OOF check passes; coverage >= 0.98 of the test studies (studies the leg could not
  read take the base's rank, recorded). Runs below that are not the pre-registered test.
- **Record:** pixel decoders available to the leg on this image, whether the base contains the
  reader fusion (v17's own fallback), coverage, and the leg's timings.

### Gates (commit run on the 3 placeholder studies, before submitting)

1. The base output equals v17's commit-run `submission.csv` byte for byte (same image, same inputs).
2. Leg: weight metadata (v13, N, 0..4), reference check `byte_equal` for all three studies, OOF
   check pass at 1e-3 for all five folds, coverage 1.0, `used_leg` true.
3. Blend recomputed locally from the downloaded base and leg outputs equals the submission.

If gate 1 or 2 fails, do not submit; diagnose first.

Runtime on the hidden test (about 1,300 studies): v17 about 26 minutes turnaround (author's report
for the CoAtNet entry; v17 with the reader is not separately measured). The N leg's hidden-test
duration was never measured. Estimate from measured parts: one v13 N model evaluated 947 validation
studies at K16 in about 680 s on one T4 (F0 log), so five models on 1,300 studies over two T4s take
about 0.65 h; DICOM preparation of 1,300 studies about 0.3 h (v07 prepared 4,407 studies in 1.02 h).
Total about 1.5-2 h, well under 9 h, with the absolute deadline as a guard. Known gap: the reader's
`pylibjpeg-libjpeg` install fails on this image (v18 log; the dataset ships cp311/cp312 wheels only),
which v17 already lives with; our leg's decoders are recorded (all training and placeholder test
DICOMs seen so far are uncompressed).

### Decision rule

- Order: v19 (w 0.15) first; v20 (w 0.25) on the next UTC day if needed (the daily quota resets at
  00:00 UTC; one submission is left on 2026-10-08).
- Anchor-family pick: v19 replaces v17 unless v19's public score is lower than v17's (a tie keeps
  v19: the scenario analysis and gold both point to a small positive effect, and w 0.15 loses little
  even at a high correlation). v20 replaces the current pick only with a public score at least 0.002
  above it (a larger weight needs a larger observed advantage; 0.002 is a decision threshold, not a
  significance test).
- Second final pick: per D-019 (currently v15 as the non-OAI hedge).
- If both v19 and v20 score below v17, these two configurations are rejected on the public LB; that
  alone does not show that the leg's family or data must change.

## 3. Alternatives not proposed

- N replacing the reader (TW): +0.0013 on gold, but drops a component that is measured on the LB.
- Per-finding weights for N: overfitting risk on 58 studies.
- Adding the v05 stack: gold +0.0021 with the proxy, but hidden-test runtime above 5 h, and the
  public notebooks that blend the old stack into the CoAtNet score 0.949, below 0.950.
- More own models before this test: the cheapest information is the LB of v19/v20.

## 4. Review questions (as sent to Codex)

1. Is the LB calibration in 1.3 sound enough to prefer w 0.15 and 0.25 over other weights?
2. Is a global weight on top of the v17 output the right structure, given TW?
3. Are the gates sufficient, in particular running our leg on the v17 image?
4. Any reason the two submissions are not worth their cost (two of five daily submissions)?

## 5. Codex review (GPT-6 Astra, read-only, 2026-10-08) and disposition

Verdict: proceed with changes. Every finding was checked against the files.

| # | Finding (severity) | Verified | Disposition |
|---|---|---|---|
| 1 | The LB calibration cannot identify a common correlation (per-finding fusion, unequal weights, rounding); the interval reflects rounding only (high) | Yes; Codex reproduced 0.838 and 0.797-0.879 | **Accepted**: 1.3 reframed as a scenario analysis; deterministic gain claims withdrawn |
| 2 | The transfer from N-CoAtNet to N-v17 is optimistic; no negative scenario; 0.15 and 0.25 are not proven optima (medium) | Yes: N-v17 on gold is 0.827 vs N-CoAtNet 0.809 | **Accepted**: N-v17 measured and used; sensitivity 0.84-0.94 with negative cases; w 0.15 framed as the conservative test, 0.25 as a probe. Global outer blend kept (Codex agrees) |
| 3 | Gates do not guarantee identical preprocessing on the new image: thumbnails within 3 pass, OOF tolerance 0.01 is 180 times the measured maximum, only folds 0, 1, 4 checked; `pylibjpeg-libjpeg` fails to install in v18 (high) | Yes (v18 log; v15 cells) | **Accepted**: byte-equal required, OOF at 1e-3 for all five folds, decoders recorded. The decoder failure belongs to v17's reader (unchanged anchor); our leg uses the image's own decoders, recorded in the commit run |
| 4 | The inherited deadline guard is not a hard limit: sequential waits each get the full timeout; `break` inside the pool's `with` still waits for submitted jobs; the reader's `subprocess.run` has no timeout; 26 min is the author's figure (high) | Yes (v15 launch cell, leg script) | **Accepted** for our cells: absolute deadline, process-tree kill, `cancel_futures`. The reader call stays as in v17 (anchor unchanged; it scored within the limit). Runtime estimate rebuilt from measured parts |
| 5 | Fallbacks can change the tested model: partial coverage blends a subset; `used_leg` ignores the OOF check and shard status (medium) | Yes (v15 blend cell) | **Accepted with a threshold**: leg used only with both shards done, byte-equal reference, OOF pass and coverage >= 0.98; otherwise the base unchanged. A strict 1.0 would turn one unreadable hidden-test study into a silent fallback, which a scoring run does not let us observe |
| 6 | Gold is a selection set; bootstrap figures are not success probabilities (medium) | Yes | **Accepted**: wording in 1.2 |
| 7 | Choosing the top public score is too sensitive to one display unit; prefer the smaller weight unless the advantage is >= 0.002; two failures do not prove the family must change (medium) | Partly | **Partly accepted**: the 0.002 threshold applies to moving from w 0.15 to 0.25, and the "must change family" conclusion is removed. For v19 vs v17 we keep v19 unless it scores lower: the scenario analysis and gold both point to a small positive effect, and the downside of w 0.15 is small |
| 8 | Worth doing, but fix the run validation first; check the daily quota (low) | Yes: one submission left on 2026-10-08 | **Accepted**: v19 first, v20 the next UTC day |

## 6. Results (2026-10-08/09)

| Entry | Public LB | Note |
|---|---:|---|
| v17 (base) | 0.950 | - |
| v19 (w 0.15) | 0.950 | tie; kept as the anchor-family pick per the decision rule |
| v20 (w 0.25) | 0.949 | lower; rejected |

Reading under section 1.3: a tie at w 0.15 and a loss at w 0.25 fit an N-v17 correlation of about
0.90-0.93 on the LB scale, above the 0.88 central assumption; the gold correlations (0.81-0.83)
understated it. The N leg adds about nothing to this base; further gains need a different or
stronger model (STATUS L21, IMPROVEMENT_PLAN Priority 6).
