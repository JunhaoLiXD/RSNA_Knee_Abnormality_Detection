# Research Notes

Analyses of public notebooks, discussions, writeups, and papers. One Markdown file per
topic or source. These notes are tracked in git; the raw third-party code they discuss
lives in `external/` (not tracked).

## File conventions

- Public notebook analysis: `kernel-<owner>-<slug>.md`.
- Discussion or writeup digest: `discussion-<topic>.md`.
- Cross-source comparison or recommendation: `<topic>.md`, for example
  `baseline-selection.md`.

## Required header for a kernel analysis

```markdown
# <Notebook title>

- Source: https://www.kaggle.com/code/<owner>/<slug> (version N, pulled YYYY-MM-DD)
- License: <license shown on Kaggle>
- Public LB: <score> (as of YYYY-MM-DD)
- Local copy: external/kernels/<owner>__<slug>/
```

Then cover: backbone, input construction (planes, series and slice selection,
resolution), use of reports and labels, training recipe, inference (TTA, ensembling),
run time and GPU needs, external datasets or weights, and risks or open questions.
State which claims were verified in code and which are taken from the author's text.
