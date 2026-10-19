"""Build notebooks/<new>-submit.ipynb from notebooks/<base>-submit.ipynb with a changed per-finding Raptor weight line
(W_RAPTOR_C) and a new provenance cell; every other cell is byte-identical (asserted). Used for the D-034 end-phase probes
(v70-v73 were built the same way by hand).

    python -I scripts/d033/build_weights.py <base vNN> <new vNN> "<reason>" Finding=0.xx [Finding=0.xx ...]

Example: python -I scripts/d033/build_weights.py v68 v76 "Baker's one step toward V2" "Baker's=0.30"
The kernel metadata is copied from <scratch>/push_<base>/ with the new id/title/code_file.
"""
import ast
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRATCH = Path("C:/Users/Ling/AppData/Local/Temp/claude/E--Project-RSNA-Knee-Abnormality-Detection/"
               "c5e6b489-5f55-44c8-8fc9-f1f768568afa/scratchpad")
LABELS = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA', 'PF OA', 'Effusion', 'Synovitis',
          "Baker's", 'Contusion', 'Fracture']


def main():
    base, new, reason = sys.argv[1], sys.argv[2], sys.argv[3]
    changes = {}
    for a in sys.argv[4:]:
        k, v = a.rsplit("=", 1)
        assert k in LABELS, k
        changes[k] = float(v)
        assert 0.0 <= changes[k] <= 1.0
    out = REPO / f"notebooks/{new}-submit.ipynb"
    assert not out.exists(), out
    nb = json.loads((REPO / f"notebooks/{base}-submit.ipynb").read_text(encoding="utf-8"))
    hits = [(i, l) for i, c in enumerate(nb["cells"]) for l in "".join(c["source"]).splitlines() if l.startswith("W_RAPTOR_C = ")]
    assert len(hits) == 1, hits
    ci, old = hits[0]
    weights = ast.literal_eval(old.split("=", 1)[1].split("#", 1)[0].strip())
    before = dict(weights)
    weights.update(changes)
    body = ", ".join(f"{k!r}: {weights[k]:g}" if k != "Baker's" else f"\"Baker's\": {weights[k]:g}" for k in weights)
    line = f"W_RAPTOR_C = {{{body}}}   # [{new}] {reason}"
    src = "".join(nb["cells"][ci]["source"])
    assert src.count(old + "\n") == 1
    nb["cells"][ci]["source"] = src.replace(old + "\n", line + "\n").splitlines(keepends=True)
    diff = ", ".join(f"{k} {before.get(k, 'default 0.5')} -> {weights[k]:g}" for k in changes)
    prov = f"""# {new} - {base} with changed per-finding Raptor weights: {diff} (D-034)

End-phase probe: {reason}. Every cell of {base} except this provenance cell and the `W_RAPTOR_C` line (cell {ci}) is unchanged
(built by `scripts/d033/build_weights.py`). Judged against the incumbent by leaderboard rank crossing (>= 20 stable witnesses,
none reversed); a public-LB probe, not by itself a final-pick candidate. Provenance of the cells: notebooks/{base}-submit.ipynb.

## Our changes (against {base})

1. This markdown cell replaces {base}'s provenance cell.
2. `W_RAPTOR_C`: {diff} (Raptor share of the Raptor/compact blend for that finding; compact = 1 - it).
"""
    nb["cells"][0]["source"] = prov.splitlines(keepends=True)
    text = json.dumps(nb, indent=1, ensure_ascii=False) + "\n"
    out.write_text(text, encoding="utf-8")
    b = json.loads((REPO / f"notebooks/{base}-submit.ipynb").read_text(encoding="utf-8"))["cells"]
    differ = [i for i, (x, y) in enumerate(zip(b, nb["cells"])) if x != y]
    assert differ == [0, ci], differ
    pdir = SCRATCH / f"push_{new}"
    pdir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out, pdir / out.name)
    m = json.loads((SCRATCH / f"push_{base}/kernel-metadata.json").read_text(encoding="utf-8"))
    m.update(id=f"lingxd/{new}-submit", title=f"{new}_submit", code_file=out.name)
    (pdir / "kernel-metadata.json").write_text(json.dumps(m, indent=2), encoding="utf-8")
    print(f"built {out}: cells differing from {base}: {differ}; {line}")


if __name__ == "__main__":
    main()
