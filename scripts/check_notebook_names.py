"""Static check: names used in a notebook code cell before any earlier cell defines them.
Catches build/rename slips (v33/v34 2026-10-11). Usage: python scripts/check_notebook_names.py notebooks/<file>.ipynb"""
import ast, builtins, json, sys
nb = json.load(open(sys.argv[1], encoding="utf-8"))
defined = set(dir(builtins)) | {"display", "get_ipython", "__file__"}
for idx, c in enumerate(nb["cells"]):
    if c["cell_type"] != "code":
        continue
    src = "".join(c["source"])
    if src.startswith("%%writefile"):
        continue
    src = "\n".join("pass" if l.lstrip().startswith(("%", "!")) else l for l in src.splitlines())
    tree = ast.parse(src)
    local = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            local.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                local.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            local.add(node.name)
        elif isinstance(node, ast.arg):
            local.add(node.arg)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            local.add(node.name)
        elif isinstance(node, ast.Global):
            local.update(node.names)
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    missing = sorted(used - defined - local)
    if missing:
        print(f"cell {idx}: undefined before use: {missing}")
    defined |= local
print("checked", sys.argv[1])
