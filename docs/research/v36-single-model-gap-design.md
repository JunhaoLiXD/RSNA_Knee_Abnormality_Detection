# v36 design: why our single model trails the forum's best single models (fold-0 diagnostics)

Status: revision 2 after the Codex review (section 9; all required changes accepted). No GPU spent. User decision
2026-10-11: "write the design note and send it to Codex" after the gap evidence in `related-work-2026-10-11.md`
section 7. Team merger is not considered for now (user, same day). Evidence cited: STATUS v11, v13, v14, v22, v24;
lessons L6, L9, L10, L11, L17, L20, L23, L26-L30; `llm-labels-feasibility-2026-10-11.md` section 6 finding 4.

## 0. Summary

Several participants report public scores of 0.947-0.959 for single architectures, and some of them state that they
used no external data; our best own model scores 0.934 (N fold 0 alone, v14) and 0.936 (5 folds). This is an
**observed score gap between incompletely specified recipes**, not an established cause. v36 tests three
recipe changes against a matched local control on fold 0 (unit training weights, 224 px with denser training
sampling, a round-3 pseudo-label target) and decides by fold-0-alone LB submissions against v14's 0.934. Only a
fold-0 LB of at least 0.940 funds four more folds of one recipe; blends of a winner are designed and reviewed
separately.

## 1. Evidence (forum self-reports, read in `external/forum/`; not verified)

| Poster | Reported | Unknown |
|---|---|---|
| colum2131 (topic 735304) | ConvNeXt-T 2.5D 0.953, DINOv2-S 0.951, ensemble 0.955; pseudo labels; "no external data" | folds, resolution, teacher, target mixture |
| azamat1ch | five-fold single-architecture ensembles: ConvNeXt-T 0.959, EfficientNetV2-S 0.956, CoAtNet 0.952 | labels, external data, resolution |
| CoolinLai; Adel Zebiche | ResNet-50 224 px 5 folds 0.954; DINOv2 224 px single fold 0.952 | label recipes, external data |
| k256.dev | fold 0 0.947, "only LLM labels", no pseudo labels | resolution, recipe |
| Archit Konde | single-fold 2.5D CoAtNet 224 px 0.950; mixing extracted labels with OOF predictions helped (50/50, more with a larger model share); hard rounding hurt; masking uncertain labels did not help | teacher lineage, folds; others report such bootstrapping gains locally that did not transfer to the LB |
| Danial Zakaria (topic 746792) | competition-only recipes 0.940-0.942; 0.949 with OAI, epoch averaging, dense inference, mirroring; steps confounded | - |

Ours: N fold 0 0.934 (v14; val 0.8988, gold 0.9200), N 5 folds 0.936, own CoAtNet fold 0 0.934 (v24). Gold-58 does
not resolve the gap (N 5-fold 0.920 vs the public CoAtNet 0.923 on gold, 0.936 vs 0.949 on the LB; L20).
Descriptively, the CoAtNet's largest per-finding gold leads over N are Synovitis +0.051, Lateral Meniscus +0.029,
PF OA +0.019, Fracture +0.017. Blend value also depends on errors shared with the anchor (L26-L30), so a stronger
leg is not guaranteed to help the OAI pick.

## 2. Control and common settings

**Control arm C (new, local)**: N fold 0 retrained locally with the original v13 round-2 target and frozen settings,
so that arms are compared with a run on the same hardware and code; v14 (0.934) stays the historical LB benchmark.
One control run does not estimate seed variance; no noise floor is claimed.

Every arm = the control except the one factor named: ConvNeXt-tiny `fb_in22k_ft_in1k`, v07 cache (320 px tokens of a
140 mm field), 2.5D triplets, 5 slots, gated per-finding attention, 15 epochs, AdamW 1e-4 backbone / 3e-4 for all
non-backbone parameters (slot embeddings, LayerNorm, attention, classifier), cosine, effective batch 8, K_train 4,
K_infer 16, seed 2026, checkpoint = best validation macro AUC (unweighted, against `soft >= 0.5`), scanner-grouped
fold 0 (3,402 training studies = 78.2% of the 4,349 non-gold studies; 947 validation). Notebook
`notebooks/v36-gap-diagnostics.ipynb` derived from `v22-n-gemini-target.ipynb` (the N trainer used locally) with the
v13 target; arms differ by configuration or an arm-specific target file; the resolved configuration is asserted at
launch. Runner: `scripts/local_v13.py` gains `v36` with an arm-aware target check (an independent recomputation of
each arm's training target). About 2.1 h per run (v22: 7,566 s at 208 img/s).

## 3. Arms (fold 0)

| Arm | Factor | Change | Why |
|---|---|---|---|
| C | none | control as above | matched local baseline |
| W | training weights | a training-only weight policy: every training cell weight 1.0 (control: 0.3 where pilkwang's verdict is UNK); evaluation weights unchanged | 28.7% of fold-0 training cells are down-weighted (27.3% of all non-gold cells; Synovitis 84.4%, Fracture 56.6%, Baker's 45.8%). The loss is normalised by each micro-batch's weight sum, so W also changes the relative contribution of findings and studies |
| G | 224 px with denser training sampling | tokens resized to 224 px (after the 320 px cache decode, before augmentation, `INTER_AREA` as the dataset already does) and K_train 8; K_infer 16 | several 0.95+ reports use 224 px. A package: training input pixels about matched (ratio 0.98), but the training bag doubles (20 -> 40 tokens; train/eval bag ratio 1:4 -> 1:2) and evaluation uses 0.49x the pixels. Measured: studies/s, epoch time, evaluation time, memory |
| P | round-3 pseudo label | target `0.5 * 4-source soft + 0.5 * N OOF`, where N OOF = the concatenated held-out raw probabilities of the five N fold models (one prediction per study; 4,349 rows, fold membership checked; source hashes recorded); control: v11 OOF | forum: OOF mixing helped one poster; L17: round 2 transferred to the LB |

Dropped from revision 1: H (head LR 2e-3): weak rationale (the cited recipe differs in supervision, batching and
backbone LR) and its slot goes to the control. Order: C, W, G, P.

**Leakage (all arms).** The training target of a fold-0 training study contains a teacher prediction from a model
trained on the other folds, including fold 0's validation studies (L9). P's stronger teacher can inflate its
validation more than the control's; P is a leaky development experiment whose result is decided on the LB. Nested
cross-fitting would remove this but does not fit the deadline.

**Checkpoint selection.** All arms select by validation AUC against the report-derived soft labels. An arm that
improves image truth while disagreeing with these labels (W is the likely case) can be penalised; a W failure does
not show that the down-weighting is harmless. Per-epoch validation metrics are kept to expose selection effects.

## 4. Measurements

Per arm: fold-0 validation macro AUC and per finding, the paired bootstrap of the difference to C on the same 947
studies (descriptive and conditional on this scanner mix: 497 of 947 studies share one scanner fingerprint), the
same split by scanner fingerprint, gold-58 (descriptive only, D-024), throughput as above, best epoch. The earlier
train/validation loss-gap item is dropped (no comparable training probe).

## 5. Decision rules (frozen before training)

1. **Local flags.** +0.003 validation over C with the paired interval above zero is a *strong-positive flag*, not an
   admission condition (precedent: v11-B -> N gained only +0.0009 validation while gold gained +0.009 and the LB
   rose; L30: validation also ranked two legs the wrong way). No gold veto (gold is descriptive, D-024).
2. **LB tests** (fold-0 leg alone, `v36_submit`, comparator v14 0.934; at most three): (a) one of W or G: the
   strong-positive one, the larger gain if both are flagged, else W (frozen fallback priority); (b) P, if technically
   successful; (c) one combined arm X trained on fold 0 with the factors whose LB test displayed >= 0.936, only if
   at least two did. An arm "passes" its LB test at displayed >= 0.936.
3. **Expansion**: folds 1-4 (about 9 h) for **one** recipe only: the highest displayed fold-0 LB among the tested
   arms and X, if it is **>= 0.940** (ties: the simpler recipe). If X fails, a passing individual arm can still be
   the one. Otherwise stop with the result "these tested settings did not justify expansion".
4. **Blends of a 5-fold winner**: at most two candidates, each with its own frozen design and Codex review before
   submission: (i) non-OAI hedge = v05 anchor + the new leg at w 0.30 (v15 structure) against v15 0.944; (ii) OAI pick
   = the incumbent B (v35 if it beats v33, else v33) with the new leg under a frozen aggregation, by D-022's rules.
5. **Caps**: five local fold-0 runs (C, W, G, P, X), three diagnostic submissions, one expansion of four folds, two
   blend candidates. v35 and approved D-026 probes keep priority for submission slots. Everything stops on
   2026-10-19 (D-021).

## 6. Implementation and checks before training

- Trainer: a `train_weight_policy` setting (`'v06'` default, `'unit'` for W) applied to the training loss only.
- Target files: C and W use the v13 round-2 target (recomputed independently and compared, as for v13/v22); P's
  target from the five N OOF files with coverage, uniqueness and range assertions and SHA-256 of the sources.
- Submission notebook (for the LB tests): built from the v14 notebook with the model and image size taken from the
  checkpoint configuration (v14 hard-codes 320 px), the arm's own OOF reference study, cache rendering at 320 px
  before any resize, and the v14 checks (reference byte-equal, OOF at 1e-3, coverage).
- `scripts/validate_notebooks.py` and `scripts/check_notebook_names.py` on both notebooks; a smoke run of G (memory,
  speed) before its full run.

## 7. Budget and timeline

Local GPU after v29 fold 2 (about 20:40 UTC 2026-10-11) and the v35 local leg test: C, W, G, P back to back about
8.5 h (to about 06:00 UTC 2026-10-12); LB tests on 2026-10-12; X about 2.1 h; one expansion about 9 h (2026-10-13);
blend designs after that. Kaggle GPU quota only for submission runs.

## 8. Risks

1. Forum numbers are unverified; pseudo labels may carry knowledge from public OAI-trained models; azamat1ch and
   others do not state their data.
2. Causes not tested here: information lost by the v07 cache (the 32-slice cap affects 30.6% of selected slot
   entries, 47.9% of AX_FS; series of up to 320 slices, so adjacent cached slices can be non-adjacent original
   slices); slot selection and cropping; training on 78.2% of the studies per fold (an all-data model is not
   tested); supervision and checkpoint selection against report-derived labels. JPEG quality, the attention head,
   augmentation and epochs have no evidence of a 0.01-0.02 effect (N's validation plateaus after its best epoch).
3. One factor at a time misses interactions; X only combines LB-passing factors.
4. Validation and gold misranked LB candidates before (L20, L28, L30); each LB test is one draw of public-LB noise.
5. Earlier single-factor changes did not move the student (L23 target, L27 backbone).

## 9. Codex review (GPT-6 Astra, high, read-only, 2026-10-11) and disposition

Verdict: proceed with changes (preferred sequence: local control, W, G, P; drop H). Codex reproduced N fold 0's
validation 0.898751 and gold 0.920047 from the saved predictions and checked the N OOF files (4,349 unique rows).

| # | Finding (severity) | Verified | Disposition |
|---|---|---|---|
| 1 | The diagnosis overstates the forum evidence: architecture, checkpoint count and supervision are conflated; external-data exclusion is stated only by some posters (medium) | Yes (threads re-read) | **Accepted**: section 0-1 reworded, per-poster table |
| 2 | The historical control is fine for the LB benchmark but not for local comparisons; v22 changed the target, and the local inference check is not a retraining check (high) | Yes | **Accepted**: control arm C; no noise floor claimed |
| 3 | W via a different targets file would change evaluation weights too; weights are read from `CFG['targets']`, separately from `train_targets`; the per-micro-batch normalisation changes relative contributions; 28.71% of fold-0 training cells are down-weighted (high) | Yes (trainer code) | **Accepted**: training-only weight policy |
| 4 | Selection by AUC against report labels can oppose W's intended benefit (high) | Yes (selection code) | **Accepted**: stated limitation, per-epoch metrics kept |
| 5 | G is a package, not compute-matched: bag size doubles, evaluation at 0.49x pixels (medium) | Yes (arithmetic) | **Accepted**: relabelled, throughput measured |
| 6 | H's rationale is weak and `lr_head` covers all non-backbone parameters (medium) | Yes (parameter groups) | **Accepted**: H dropped for the control |
| 7 | P must use held-out raw probabilities, one per study, and is still leaky (high) | Yes (fold structure) | **Accepted** |
| 8 | The +0.003 validation gate contradicts our own precedent (v11-B -> N: +0.0009 validation, +0.009 gold, LB up) (high) | Yes (STATUS v11/v13 rows) | **Accepted**: flag, not gate; frozen fallback W; gold veto removed |
| 9 | The bootstrap conditions on one scanner mix (497/947 studies share a fingerprint) (medium) | Not recounted | **Accepted**: descriptive, split by fingerprint |
| 10 | The loss-gap measurement is unspecified (no training probe) (medium) | Yes (`train_probe_n` 0) | **Accepted**: dropped |
| 11 | Runner lacks v36 and would route unknown targets to the T3 check; v14 hard-codes 320 px (high) | Yes (`local_v13.py` lines 37-40; v14 `'img': 320`) | **Accepted**: section 6 |
| 12 | Allocation rules ambiguous: explicit caps for expansions, X, submissions and blends (high) | Yes | **Accepted**: section 5 rule 5 |
| 13 | Omitted causes: supervision/selection, the v07 32-slice cap (30.61% of slot entries), scanner-grouped 78.2% training subsets (medium) | Yes (recomputed from `v07_cache_index.csv`: 30.6%, AX_FS 47.9%, max 320 slices) | **Accepted** as untested hypotheses (section 8); a cache rebuild does not fit this test |
