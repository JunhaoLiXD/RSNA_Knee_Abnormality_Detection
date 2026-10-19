"""Reproduce a public Kaggle notebook unchanged as notebooks/<ver>-submit.ipynb (D-034 standing authorization: a higher public
recipe is copied, audited against the author's output, and submitted).

    python -I scripts/d033/copy_public.py <owner/slug> <vNN> [--push]

Steps: pull the latest version (notebook + metadata) into external/kernels/<owner>__<slug>_<UTC stamp>/, download the author's
run output next to it, prepend a provenance markdown cell, swap known unversioned inputs for their byte-equal versioned copies
(L42: heliosli/rsna-knee-r6-frozen-fe055406 may resolve to R7), write kernel-metadata.json (author's datasets, docker image and
machine shape) to <scratch>/push_<vNN>/, run the notebook validator, and push the commit run with --push. Cell sources are
otherwise unchanged; the audit (scripts/d033/audit_copy.py) compares the commit-run output with the author's.
"""
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRATCH = Path("C:/Users/Ling/AppData/Local/Temp/claude/E--Project-RSNA-Knee-Abnormality-Detection/"
               "c5e6b489-5f55-44c8-8fc9-f1f768568afa/scratchpad")
# unversioned slug -> versioned byte-equal copy (manifest sha256 6508ce69...; v62/v69 ran it)
SLUG_SWAPS = {"rsna-knee-r6-frozen-fe055406": "rsna-knee-r6-frozen-fe055406-w1"}
DATASET_SWAPS = {"heliosli/rsna-knee-r6-frozen-fe055406": "heliosli/rsna-knee-r6-frozen-fe055406-w1"}


def run(cmd):
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def main():
    ref, ver = sys.argv[1], sys.argv[2]
    push = "--push" in sys.argv[3:]
    assert re.fullmatch(r"v\d{2}", ver), ver
    out_nb = REPO / f"notebooks/{ver}-submit.ipynb"
    assert not out_nb.exists(), f"{out_nb} exists"
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M")
    kdir = REPO / "external/kernels" / f"{ref.replace('/', '__')}_{stamp}"
    kdir.mkdir(parents=True)
    r = run(["kaggle", "kernels", "pull", ref, "-p", str(kdir), "-m"])
    assert r.returncode == 0, r.stdout + r.stderr
    nbs = list(kdir.glob("*.ipynb"))
    assert len(nbs) == 1, nbs
    raw = nbs[0].read_bytes()
    nb = json.loads(raw)
    meta = json.loads((kdir / "kernel-metadata.json").read_text(encoding="utf-8"))
    (kdir / "output").mkdir()
    r = run(["kaggle", "kernels", "output", ref, "-p", str(kdir / "output")])
    print("author output:", r.returncode, sorted(p.name for p in (kdir / "output").iterdir())[:20])

    changes = []
    for ci, c in enumerate(nb["cells"]):
        src = "".join(c["source"])
        new = src
        for old_slug, new_slug in SLUG_SWAPS.items():
            new = re.sub(rf"(C_SLUG\s*=\s*')({re.escape(old_slug)})(')", rf"\g<1>{new_slug}\g<3>", new)
        if "\u8def" in new:                       # a mis-encoded middle dot seen in heliosli's credits (v69); the validator rejects CJK
            new = new.replace("\u8def", "\u00b7")
        if new != src:
            c["source"] = new.splitlines(keepends=True)
            changes.append(ci + 1)               # +1: the provenance cell is inserted at index 0
    datasets = [DATASET_SWAPS.get(d, d) for d in meta.get("dataset_sources", [])]

    prov = f"""# {ver} - public notebook {ref} reproduced (D-034)

Inference-only reproduction of a public notebook, as v62 and v67-v69 were. The author's cells below are unchanged except as
listed. Built by `scripts/d033/copy_public.py`.

## Provenance

- Source: https://www.kaggle.com/code/{ref} (latest version as pulled {stamp[:8]} {stamp[8:]} UTC). Pulled notebook sha256
  `{hashlib.sha256(raw).hexdigest()}`. Licence: as stated by the author (none stated unless the cells say so); every
  component keeps the author's credits below.
- Inputs: {', '.join(datasets)}.

## Our changes

1. This markdown cell.
2. Cells changed by the copy script (versioned input slug or a mis-encoded character): {changes or 'none'}.
"""
    nb["cells"].insert(0, {"cell_type": "markdown", "metadata": {}, "source": prov.splitlines(keepends=True)})
    text = json.dumps(nb, indent=1, ensure_ascii=False) + "\n"
    assert len(text.encode("utf-8")) < 950_000, "Kaggle source limit"
    out_nb.write_text(text, encoding="utf-8")
    pdir = SCRATCH / f"push_{ver}"
    pdir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out_nb, pdir / out_nb.name)
    kmeta = {"id": f"lingxd/{ver}-submit", "title": f"{ver}_submit", "code_file": out_nb.name, "language": "python",
             "kernel_type": "notebook", "is_private": True, "enable_gpu": meta.get("enable_gpu", True), "enable_tpu": False,
             "enable_internet": False, "keywords": ["gpu"], "dataset_sources": datasets,
             "kernel_sources": meta.get("kernel_sources", []), "competition_sources": meta.get("competition_sources", []),
             "model_sources": meta.get("model_sources", []), "docker_image": meta.get("docker_image"),
             "machine_shape": meta.get("machine_shape", "NvidiaTeslaT4")}
    (pdir / "kernel-metadata.json").write_text(json.dumps(kmeta, indent=2), encoding="utf-8")
    r = run([sys.executable, str(REPO / "scripts/validate_notebooks.py"), str(out_nb)])
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr)
    assert r.returncode == 0, r.stdout + r.stderr
    print(f"built {out_nb} ({len(text)} chars); changed cells {changes}; datasets {datasets}; pulled to {kdir}")
    if push:
        r = run(["kaggle", "kernels", "push", "-p", str(pdir)])
        print(r.stdout.strip()[-400:], r.stderr.strip()[-400:])
        assert r.returncode == 0


if __name__ == "__main__":
    main()
