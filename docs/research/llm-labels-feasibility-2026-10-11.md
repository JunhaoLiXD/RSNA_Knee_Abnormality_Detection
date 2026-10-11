# LLM work beyond silver: feasibility (2026-10-11)

Status: revision 1 with the Codex review (section 6) and the resulting staged plan (section 7); awaiting the user's go-ahead. User decision 2026-10-11: keep the silver route first (v32-based,
D-024), and try to go higher; LLM use is allowed regardless of the host's position. Evidence: STATUS L4, L17,
L20, L23, L26-L30; `external-levers-2026-10-09.md` 2.1 and E2; forum topics 745861, 747658, 735304, 746792.

## 1. Where the top is and where we are (leaderboard 2026-10-11 03:35 UTC, 5,710 teams)

#1 0.965; 0.964 three teams; #10 0.963; gold cut (rank 21) 0.961; #100 0.955; silver cut (rank 285) 0.952 and
rising about 0.001 a day; 199 teams >= 0.954. Ours: v30 0.951 (rank 405); v32 (public 0.954 reproduction) pending.
Top-10 teams have 61-331 submissions. Our own image models alone: N 5-fold 0.936; legs add about +0.001 to a
public base (v27, v30).

## 2. What the forum says about labels (read 2026-10-11; authors' claims, not verified)

- hengck23 (rank 1,140): "model is not the key, it is your labels"; Claude Opus 4.5 report labels
  (github NTejas-1/RSNA-Knee-Abnormality-Detection: Snowflake Cortex extraction, soft targets, public LB 0.941 with
  a public ensemble) score **0.892 macro AUC on gold**; MRI + text models trained on them blend to gold 0.938.
  Gold labels can contradict the report (a gold study labelled Effusion = 1 whose report says "No knee effusion
  is present"): gold appears to be read from images, so report-only labels have a ceiling against gold.
- Kirderf: an LLM label-extraction benchmark (Kaggle Benchmarks); multi-read fusion (each report read several
  times, readers fused into one probability per cell).
- Single models: 0.945 single fold with LLM labels only (k256.dev); 0.952 (224 px) and 0.955 (5-fold) single
  models; the public CoAtNet 0.949 recipe gained most from OAI external data (+0.005 then +0.003 for a 384 px
  full-field recipe), +0.002 from a label blend ("JEV labels").
- Cost warnings: labelling with gpt-6-astra exhausted one participant's quota; hengck23 suggests spending the
  strongest reader only on uncertain or critical cells.

## 3. Our label state

Training target of N (and v26/v29: the soft part only): mean of four public LLM label tables (pilkwang,
stevenleehans, lixin73, dreaddevelopment) = **gold 0.8919**; no single public table beats it (external-levers
2.1); a fifth source (CC0 Gemini) raised the target on gold by +0.0036 but did not change the trained student
(L23); the OOF image teacher (v11, v13) did (L17: +0.007 gold). Local public tables not in the mean: ctogaurav v4
blend, omarelhabashy v3, xhaitanya Qwen3-8B, kiritohayate95 MedGemma grades, karttikjangid05 comparisons; the
NTejas Opus 4.5 table is public on GitHub (licence to check).

Reports: 4,407 (train only; absent at test), about 1.2 M tokens (median about 980 characters, p90 2,100); about
2,100 contain Latin-extended characters and 220 Cyrillic (non-English reports).

## 4. Options

| # | LLM work | Cost | For | Against |
|---|---|---|---|---|
| L1 | Add public tables (Opus 4.5, others) to the soft mean | hours | cheap, measurable on gold | L23: label-mean changes barely move the student |
| L2 | Our own multi-read labels with a fixed rubric (Claude Opus subagents in this session; 2 reads per report, about 1.2 M report tokens each) as a new source | about 1 day, several M tokens of the user's plan | independent reader, controlled rubric, multilingual | ceiling about 0.89 on gold like every report reader (section 2) |
| L3 | Graded extraction (severity / certainty per finding, ordinal) mapped to soft targets | about 1 day | within-class ranking matters for AUC; graded tables exist (MedGemma grades) to compare | mapping needs labels; gold is 58 studies and reused |
| L4 | Targeted adjudication of the cells where tables, OOF teacher and image models disagree (strongest model only) | 0.5-1 day, small token budget | spends tokens where labels are uncertain (forum advice; external-levers E2) | the gain is bounded by the share of uncertain cells; E2 audit not done |
| L5 | Image-grounded labels: an LLM reads the report plus a few key slices for uncertain cells | 1-2 days, large token budget | gold is image-read; only route past the report ceiling | LLM image reading of knee MRI is unproven; slice choice is hard (forum) |

Downstream use: retrain the N-type leg (fold 0 about 2.5 h local; or the B2 two-view recipe about 4.7 h) on the new
target, test it as a leg on v32 (or v17) with the v27/v30 machinery; 5-fold only on evidence. Large experiments
stop 2026-10-19; about 8 days remain; the local GPU is busy until about 2026-10-12 with v26/v29 folds.

## 5. Questions for the review

1. Which LLM work, if any, has a credible chance of moving the LB beyond what the v32-based silver route gives, in
   8 days? Is "labels are the key" applicable to us, given our target already equals the best single LLM reader on
   gold and the remaining gap to top teams also includes OAI data, model recipe and ensembles?
2. How to evaluate label changes when gold has misranked candidates three times (L20, L28, L30)? (Gold-58, the
   LLM-label validation AUC that correlates better with the LB (forum r = 0.87 vs 0.66), or LB tests only.)
3. Execution: Claude subagents vs Codex vs a local model on the 3080 Ti vs public tables only; cost control.
4. Is there a non-label route with better expected value for the same days (for example our two-view model at
   384 px, distillation from the S6/CoAtNet ensemble, more folds)?

## 6. Codex review (GPT-6 Astra, high, read-only, 2026-10-11) and disposition

Verdict: keep D-024's silver route intact; audit source handling and weights now (hours, no GPU); pilot L4 with
gates; L1 audit only (no indiscriminate averaging); L2 skip; L3 only as structured fields inside L4; L5 skip.
Planning expectation for the label branch: zero to +0.001 in the final ensemble, +0.002 a strong success; reaching
0.961 this week through label work is speculative (0.954 -> 0.961-0.965 needs a 15-24% cut of the remaining
macro pair-ranking error).

| # | Finding | Verified | Disposition |
|---|---|---|---|
| 1 | "4-source target = gold 0.8919" is not the training mixture: on gold 684 cells have three sources and 12 two (dread has no gold rows); the gold round-2 target uses a five-model teacher ensemble | Codex, from `gold_label_sources.py` (noted there) | **Accepted**: gold cannot rank the training mixture against single readers |
| 2 | v22 added a diluted fifth voter (target change 0.1 x (p_new - s_old)); it is evidence against more voters, not against repair; B1/B2 use report-only targets | Yes (target formula) | **Accepted**: repair changes cells directly under a frozen policy |
| 3 | 12.4% of non-gold cells (6,471 of 52,188, 3,151 studies) have one source <= 0.2 and another >= 0.8; spot checks show clear extraction errors and also genuine ambiguity | Codex; not recounted | **Accepted** as the pilot's sampling frame |
| 4 | Loss weights come only from pilkwang's `UNK` verdict: 27.3% of training cells downweighted, Synovitis 84.4%, Fracture 56.6%, Baker's 45.8% | **Yes** (recomputed from `v06_targets.csv`) | **Accepted**: audit the weight policy within L4 (no blanket change) |
| 5 | Some "new" tables recycle others: ctogaurav v4 equals steven v4 | **Yes** (all 12 columns identical, 4,407 rows) | **Accepted**: provenance audit before any source change |
| 6 | L3's rationale was wrong: ordering two positives does not enter binary AUC; severity is not presence probability | Yes | **Accepted**: L3 only as diagnostic fields |
| 7 | 1.2 M tokens is a character/4 estimate, not a billing estimate; L2 would be about 9-16 M tokens | Yes | **Accepted**: token caps in section 7 |

Other points accepted: the top gap is only partly a label question (our labels train only our leg; L20/L27 point
to external images and recipes); B2 at 384 px needs native rendering to add detail (lower priority); S6/CoAtNet
distillation skipped this week (no honest OOF, about 14-17 h of S6 inference, more redundancy); report
benchmark with duplicate-report groups kept together (46 groups, 177 studies); matched fixed-epoch control and
repair students; no local LLM on the busy 3080 Ti.

## 7. Staged plan (proposed D-025)

| Dates | Work | Gate |
|---|---|---|
| 10-11/12 | Silver route first (D-024). Source and weight audit (provenance, duplicates, report support, `UNK` weights); non-gold report benchmark (about 80 development + 160 evaluation reports, half random, half disagreement-enriched, script and scanner coverage, duplicate groups kept together) | no LLM spend before the repair hypothesis is written down |
| 10-12/13 | L4 pilot: blinded reads of disagreement cells with evidence spans, compartment and asserted / negated / uncertain / unmentioned status; second reader on proposed changes; manual check of a random sample | >= 30 material, evidence-supported corrections across >= 2 findings beyond one template; >= 90% support in a blinded sample of 50 corrections; otherwise stop |
| 10-13/14 | Repair up to about 1,000 selected reports; freeze one target and weight policy; one matched B2 fold-0 control and repair pair (same initialisation, fixed epochs) | stop on technical failure or no held-out report-fidelity gain |
| 10-14/16 | One control blend and one repaired blend, identical except the leg, against the silver incumbent | +0.001 displayed buys one confirmation fold, +0.002 at most two; a tie buys nothing |
| 10-16/18 | At most one expanded candidate | must keep its advantage and fit runtime |
| 10-19/22 | Freeze modelling; verify final picks, inputs, runtime | - |

Budgets: LLM pilot 0.8 M input + 0.2 M output tokens; cumulative 2.5 M + 0.5 M if the pilot passes. Local GPU
24 h for this branch (the v26/v29 queue finishes before 10-13). Kaggle: silver validation 6 h, label branch 6 h,
reserve 8 h, unallocated 9.8 h. At most three new-branch submissions. LLM reads: Claude subagents in this session
(structured JSON per report, prompt and model versions logged) or a hosted API if the user provides one.

## 8. Development set (40 reports) and the second Codex review (2026-10-11)

Reader A (two Claude Opus subagents, effort xhigh, rubric v1; about 245k subagent tokens and about 20% of a 5-hour
window): 480 cells, absent 177, present 165, not_mentioned 79, uncertain 59; all evidence quotes are verbatim.
No present/absent cell lies across 0.5 from the four-source mean with the 0.2 margin (three cross 0.5 with a smaller
margin); 27 present/absent cells (56 over all statuses) differ from the mean by >= 0.2: 12 are meniscus
"degeneration, no tear" (pilkwang and steven 0.68-0.82), several OA cells where dread is low and A agrees with the
majority. In decisive disagreement cells A agrees with lixin 0.97, pilkwang and steven 0.81, dread 0.21. Gold check
by regex: reports stating meniscal degeneration without a tear have gold meniscus = 1 in about 4 of 10 cases (gold is
image-read), so a literal "repair" can move targets away from the test labels.

Codex (GPT-6 Astra, high, read-only) verdict: pause LLM expansion; L4 narrowed, not refuted; the proposed
gold-calibration of reader categories is exploratory (58 observations per finding, MCL nine positives, 208 distinct
qualifier strings; leave-one-study-out AUC is biased for category-rate models; it must beat calibrated existing-source
features, and gold-built targets spoil later gold evaluation). Agreement with lixin is not accuracy (lixin gold
0.8352). Actions, accepted: (1) finish the manual audit of the 40 development reads (extraction mistakes vs rubric
disagreements vs probability differences; example `dev_0001`: a normal Hoffa fat pad used as Synovitis absent);
the sampler's enrichment truncation dropped Contusion and Fracture selections (fixed: quotas sum to the target);
(2) a token-free dread ablation: one matched B2 fold-0 student on the three-source target vs the four-source target
(same weights, initialisation, views, epochs), then one fixed blend comparison, no weight sweep; (3) gold reads only
if the audit finds a recurring distinction the existing sources miss, with a frozen vocabulary and baselines;
(4) stop the branch if its novelty reduces to meniscus ontology plus source reweighting.
