# RSNA Knee Fast 2xT4 Inference

- Source: https://www.kaggle.com/code/jiweiliu/rsna-knee-fast-2xt4-inference (version 11, pulled 2026-10-01)
- License: Apache 2.0 (shown on the Kaggle page)
- Public LB: 0.943 best (as of 2026-10-01; the scored version is not identified)
- Local copy: external/kernels/jiweiliu__rsna-knee-fast-2xt4-inference/

## Relationship to the root

Same model stack and weights as
[Speedy Raptors](kernel-mattiaangeli-bend-the-knee-to-speedy-raptors-the-original.md); the
author states the recipe is copied from Mattia Angeli's v34 (0.943). Code diff to the root
is 443 lines. It is the parent of pjmathematician's d4-lite/d4-blend (316-line diff) and the
base of evgendvorkin's versia-5 and Roman Tamrazov's DINOsaur V5. All 18 inputs are public.

## What it changes (author's changelog, spot-checked in code)

- Two-T4 scheduling: the 6 frozen DINOv2 prefix blocks are hash-verified identical across
  the 20 members and computed once (verified: `SHARED_DINO_PREFIX_SHA256`); CPU preparation
  overlaps GPU work; MaxSpan forward/reverse share one decode.
- v9: CoAt family = residual / D4 / Global96 / Repair-v1 at 0.25 each, probability mean
  then rank; CoAt 0.40 vs Raptor 0.60 (verified in the blend cell).
- v10-v11: for more than 48 studies the four CoAt readers run one at a time to bound RAM;
  if a CoAt arm fails, the remaining arms share its weight (verified: try/except per
  reader, `_coat_*_ok` flags).

Backbone, input, labels, TTA and external weights are identical to the root; see that note.

## Run time and GPU

- Requires exactly 2 x T4 (`torch.cuda.device_count() != 2` raises, verified).
- `TIME_BUDGET = 8.0 * 3600` (verified). The full hidden-test runtime is not published;
  the visible run is ~5 min on 3 placeholder studies.

## Why it matters for us

It is the most-forked, best-documented 0.943 notebook whose inputs are all public, and its
changelog records exactly which weight changes moved the public score. That makes it the
cleanest anchor to reproduce.

## Risks

Same as the root: public-LB-tuned weights, silent arm fallback, bf16 on T4 in the A5 stage.
