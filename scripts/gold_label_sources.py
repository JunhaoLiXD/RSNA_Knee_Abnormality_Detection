"""Gold-58 macro AUC of public report-label tables and of our training targets.

Analysis only (no training). Inputs: `data/train.csv` (gold labels), the v06 targets, the v11 and
v13-N gold predictions under `results/`, and public label tables downloaded unchanged to
`external/datasets/<owner>__<slug>/`. Used in `docs/research/external-levers-2026-10-09.md`.

Run from the repository root with the `kaggle` env (needs pyarrow for the parquet tables):
    python scripts/gold_label_sources.py
"""
import glob
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "external" / "datasets"
L = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA', 'PF OA',
     'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']
B = 2000

train = pd.read_csv(ROOT / "data" / "train.csv").drop(columns=["Report"])
gold = train.dropna(subset=L).set_index("StudyInstanceUID")[L].astype(int)
G = gold.index
Y = gold.values


def by_uid(df):
    return df.set_index("StudyInstanceUID")


def gold_mean(pattern):
    files = sorted(glob.glob(str(ROOT / pattern)))
    assert files, pattern
    return pd.DataFrame(np.mean([by_uid(pd.read_csv(f)).loc[G, L].values for f in files], 0), index=G, columns=L)


targets = by_uid(pd.read_csv(ROOT / "results/v06/run1/v06/v06_targets.csv"))
soft = targets.loc[G, L].astype(float)
v11 = gold_mean("results/v13/local_input/rsna-knee-v11-oof/v11_gold_fold*_B_k16.csv")
n_model = gold_mean("results/v13/*/v13/fold*_N/v13_gold_fold*_N_k16.csv")

src = {
    "ours: 4-source soft target (v06)": soft,
    "ours: round-2 target (0.5 soft + 0.5 v11)": 0.5 * soft + 0.5 * v11,
    "ours: model N 5-fold (image model)": n_model,
    "pilkwang": by_uid(pd.read_csv(EXT / "pilkwang__rsna-knee-llm-labels/report_labels_v2.csv"))[L],
    "steven_v2": by_uid(pd.read_csv(EXT / "stevenleehans__rsna-knee-llm-report-labels/llm_labels_v2.csv"))[L],
    "steven_v4_blend": by_uid(pd.read_csv(EXT / "stevenleehans__rsna-knee-llm-report-labels/llm_labels_v4_blend.csv"))[L],
    "lixin (GPT-5.6-Sol)": by_uid(pd.read_csv(EXT / "lixin73__rsna-knee-llm-report-labels-sol56/labels_llm_gpt56sol.csv"))[L],
    "ctogaurav_v4_blend": by_uid(pd.read_csv(EXT / "ctogaurav__rsna-knee-llm-labels-v4-blend/llm_labels_v4_blend.csv"))[L],
    "karttik consensus": by_uid(pd.read_csv(EXT / "karttikjangid05__rsna-knee-public-llm-label-sets-compared/consensus_labels.csv"))[L],
}
v1 = by_uid(pd.read_parquet(EXT / "nartaa__rsna-knee-hpo-assets/train_labels_v1.parquet"))
src["nartaa (Gemini 3 Flash)"] = v1[["y_" + l.replace("'", "").replace(" ", "_") for l in L]].set_axis(L, axis=1)
for f, n in [("grades_medgemma27_p3", "MedGemma-27B"), ("grades_qwen32_p3", "Qwen-32B"), ("grades_mistral_p3", "Mistral")]:
    src[f"kiritohayate95 ({n}, local LLM)"] = by_uid(pd.read_csv(EXT / f"kiritohayate95__rsna-knee-medgemma-grades/{f}.csv"))[L]
q = by_uid(pd.read_csv(EXT / "xhaitanya__qwen38b-labels-rsnaknee/llm_labels.csv"))
q.columns = L
src["xhaitanya (Qwen3-8B, local LLM)"] = q
cat = by_uid(pd.read_csv(EXT / "omarelhabashy__knee-labels-v3/labels_categories.csv"))[L]
src["omarelhabashy v3 (categories)"] = cat.replace(
    {"abnormal": 1.0, "uncertain": 0.5, "not_mentioned": 0.25, "normal": 0.0}).astype(float)


def macro_auc(y, p):
    """Macro AUC via Mann-Whitney ranks (ties averaged); nan if a label has one class."""
    out = []
    for j in range(y.shape[1]):
        pos = y[:, j] == 1
        npos, nneg = pos.sum(), (~pos).sum()
        if npos == 0 or nneg == 0:
            return np.nan
        r = rankdata(p[:, j])
        out.append((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))
    return float(np.mean(out))


rng = np.random.default_rng(0)
boots = [rng.choice(len(G), len(G)) for _ in range(B)]


def paired(p, ref, ok=None):
    """Mean gain over ref and its 95% bootstrap interval and P(gain <= 0) (study resamples)."""
    ok = np.ones(len(G), bool) if ok is None else ok
    d = []
    for b in boots:
        b = b[ok[b]]
        v = macro_auc(Y[b], p[b]) - macro_auc(Y[b], ref[b])
        if np.isfinite(v):
            d.append(v)
    d = np.array(d)
    return d.mean(), np.quantile(d, 0.025), np.quantile(d, 0.975), (d <= 0).mean()


rows = []
for name, df in src.items():
    df = df.apply(pd.to_numeric, errors="coerce").reindex(G)[L]
    ok = df.notna().all(axis=1).values
    p = np.where(ok[:, None], df.values, 0.0)
    gain = paired(p, soft.values, ok)
    rows.append((name, int(ok.sum()), macro_auc(Y[ok], p[ok]), *gain))
table = pd.DataFrame(rows, columns=["source", "n_gold", "gold_macro_auc", "gain_vs_soft4", "ci_low", "ci_high", "p_gain_le_0"])
print(table.sort_values("gold_macro_auc", ascending=False).round(4).to_string(index=False))

show = ["ours: 4-source soft target (v06)", "ours: round-2 target (0.5 soft + 0.5 v11)", "nartaa (Gemini 3 Flash)",
        "lixin (GPT-5.6-Sol)", "kiritohayate95 (Qwen-32B, local LLM)", "ours: model N 5-fold (image model)"]
per = pd.DataFrame({s: [macro_auc(Y[:, [j]], src[s].reindex(G)[L].values[:, [j]].astype(float)) for j in range(len(L))]
                    for s in show}, index=L)
print("\nPer finding (gold-58 AUC):")
print(per.round(3).to_string())

# T3 as pre-specified in design v21-shortlist section 3: the Gemini table as an equal-weight extra
# source, soft5 = (n * soft4 + gemini) / (n + 1) with n = the v06 source count of each cell. On gold
# n is 3 (684 cells) or 2 (12 cells), because the dread table has no gold rows, so Gemini weighs 1/4
# or 1/3 here against 1/5 in training. The v11 part on gold is the mean of the five fold models
# (teacher ensemble), not an out-of-fold prediction as for the training studies.
gem = src["nartaa (Gemini 3 Flash)"].reindex(G)[L].astype(float)
n_src = targets.loc[G, [f"{c}__n_sources" for c in L]].to_numpy(float)
soft5 = (n_src * soft.values + gem.values) / (n_src + 1.0)
round2 = (0.5 * soft + 0.5 * v11).values
t3 = 0.5 * soft5 + 0.5 * v11.values
m, lo, hi, ple0 = paired(t3, round2)
print(f"\nT3 (design v21-shortlist 3): soft5 {macro_auc(Y, soft5):.4f} (soft4 {macro_auc(Y, soft.values):.4f}); "
      f"T3 {macro_auc(Y, t3):.4f} vs round-2 {macro_auc(Y, round2):.4f}: {m:+.4f}, CI {lo:+.4f} to {hi:+.4f}, "
      f"P(gain <= 0) {ple0:.3f} ({B} paired resamples)")
