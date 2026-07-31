#!/usr/bin/env python3
"""Smoke-check the tutorial notebooks without executing them.

Catches the failure classes that full execution would, minus the cost
(no LLM/API calls, no kernel):
1. Every notebook parses as valid JSON.
2. Every code cell's source compiles (IPython magic lines skipped).
3. Every third-party top-level import used in the notebooks is importable
   — guards against a notebook using a dependency that isn't declared/installed
   (e.g. the rank_bm25 gap in 10.rag).
"""

import ast
import importlib
import json
import pathlib
import sys
import warnings

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors = []


def py_lines(src: str) -> list[str]:
    """Drop IPython magic lines (!pip / %env …) which are not valid Python."""
    return [line for line in src.splitlines() if not line.lstrip().startswith(("!", "%"))]


def top_level_imports(src: str) -> set[str]:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split(".")[0])
    return mods


notebooks = sorted(ROOT.glob("*.ipynb"))
if not notebooks:
    print("No notebooks found at repo root")
    sys.exit(1)

# 1 & 2: JSON validity + cells compile
for nb in notebooks:
    try:
        data = json.loads(nb.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report any JSON failure
        errors.append(f"{nb.name}: invalid JSON — {exc}")
        continue
    for i, cell in enumerate(data.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        code = "\n".join(py_lines("".join(cell.get("source", []))))
        if not code.strip():
            continue
        try:
            # PyCF_ALLOW_TOP_LEVEL_AWAIT: Jupyter kernels run cells async,
            # so top-level `await` is valid there but not in plain compile().
            compile(code, f"{nb.name}:cell{i}", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
        except SyntaxError as exc:
            errors.append(f"{nb.name}:cell{i}: syntax error — {exc}")

# 3: every third-party top-level import must be importable
stdlib = set(sys.stdlib_module_names)
third_party: set[str] = set()
for nb in notebooks:
    data = json.loads(nb.read_text(encoding="utf-8"))
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = "\n".join(py_lines("".join(cell.get("source", []))))
        third_party |= top_level_imports(src) - stdlib

for mod in sorted(third_party):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # third-party libs emit SyntaxWarnings at import
            importlib.import_module(mod)
    except ImportError as exc:
        errors.append(f"import '{mod}' used in notebooks but not importable — {exc}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(
    f"OK: {len(notebooks)} notebooks valid, all cells compile, {len(third_party)} third-party imports available"
)
