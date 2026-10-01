"""Static checks for project notebooks.

Run after every notebook change:
    python scripts/validate_notebooks.py                 # all notebooks/*.ipynb
    python scripts/validate_notebooks.py notebooks/v05-*.ipynb
    python scripts/validate_notebooks.py --allow-outputs path/to/run_output.ipynb

Checks:
  1. The file parses as a valid nbformat v4 notebook.
  2. Every code cell compiles as Python (IPython magics and shell lines are skipped).
  3. The filename starts with a two-digit version (vNN-) and that version string
     appears in the notebook source.
  4. No stored execution outputs (unless --allow-outputs).
  5. No CJK characters in project-authored cells.

Exit code is non-zero if any check fails.
"""

from __future__ import annotations

import argparse
import re
import sys
import warnings
from pathlib import Path

import nbformat

REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^(v\d{2})-")
CJK_RE = re.compile(r"[぀-ヿ㐀-䶿一-鿿가-힯＀-￯]")
MAGIC_PREFIXES = ("%", "!")


def strip_magics(source: str) -> str:
    """Replace IPython magic and shell lines with `pass` so the cell still compiles."""
    lines = []
    for line in source.splitlines():
        stripped = line.lstrip()
        # A continuation line such as "!= x" is Python, not a shell escape.
        if stripped.startswith(MAGIC_PREFIXES) and not stripped.startswith("!="):
            indent = line[: len(line) - len(stripped)]
            lines.append(f"{indent}pass")
        else:
            lines.append(line)
    return "\n".join(lines)


def validate(path: Path, allow_outputs: bool) -> list[str]:
    errors: list[str] = []
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            nb = nbformat.read(path, as_version=4)
    except Exception as exc:  # noqa: BLE001 - report any parse failure
        return [f"invalid notebook JSON: {exc}"]

    match = VERSION_RE.match(path.name)
    if not match:
        errors.append("filename must start with a two-digit version, e.g. v05-...")

    full_source = []
    for idx, cell in enumerate(nb.cells):
        source = cell.source
        full_source.append(source)
        if CJK_RE.search(source):
            errors.append(f"cell {idx}: contains CJK characters")
        if cell.cell_type != "code":
            continue
        try:
            compile(strip_magics(source), f"{path.name}[cell {idx}]", "exec")
        except SyntaxError as exc:
            errors.append(f"cell {idx}: SyntaxError line {exc.lineno}: {exc.msg}")
        if not allow_outputs and (cell.get("outputs") or cell.get("execution_count")):
            errors.append(f"cell {idx}: has stored outputs or execution_count")

    if match and match.group(1) not in "\n".join(full_source):
        errors.append(f"version '{match.group(1)}' does not appear in the notebook source")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--allow-outputs", action="store_true")
    args = parser.parse_args()

    paths = args.paths or sorted((REPO_ROOT / "notebooks").glob("*.ipynb"))
    if not paths:
        print("No notebooks to validate.")
        return 0

    failed = 0
    for path in paths:
        errors = validate(path, args.allow_outputs)
        status = "OK  " if not errors else "FAIL"
        print(f"[{status}] {path}")
        for error in errors:
            print(f"       - {error}")
        failed += bool(errors)
    print(f"\n{len(paths) - failed}/{len(paths)} notebooks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
