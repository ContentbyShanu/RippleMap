from __future__ import annotations
import ast
import os
from pathlib import Path
from .graph import DependencyGraph

DEFAULT_MAX_FILES = 10000
DEFAULT_MAX_FILE_BYTES = 1_000_000

def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=True))
        return True
    except (ValueError, OSError, RuntimeError):
        return False

def _module(path: Path, root: Path) -> str:
    parts = list(path.relative_to(root).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)

def _is_test(path: Path) -> bool:
    return path.name.startswith("test_") or path.name.endswith("_test.py") or "tests" in path.parts

def _imports(source: str):
    tree = ast.parse(source)
    refs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                refs.append((alias.name, node.lineno, f"import {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            name = "." * node.level + (node.module or "")
            if name:
                refs.append((name, node.lineno, f"from {name} import {', '.join(a.name for a in node.names)}"))
            if node.level and not node.module:
                for alias in node.names:
                    if alias.name != "*":
                        refs.append(("." * node.level + alias.name, node.lineno, f"from {'.' * node.level} import {alias.name}"))
    return refs

def _resolve_relative(name: str, importer: str, is_package: bool) -> str:
    level = len(name) - len(name.lstrip("."))
    remainder = name[level:]
    parts = importer.split(".") if importer else []
    if not is_package and parts:
        parts = parts[:-1]
    trim = level - 1
    if trim:
        parts = parts[:-trim] if trim <= len(parts) else []
    if remainder:
        parts.extend(remainder.split("."))
    return ".".join(p for p in parts if p)

def _resolve(name: str, importer: dict, known: set[str]):
    candidates = [_resolve_relative(name, importer["module"], importer["package"])] if name.startswith(".") else [name]
    for candidate in candidates:
        if candidate in known:
            return candidate
        parts = candidate.split(".")
        while len(parts) > 1:
            parts.pop()
            parent = ".".join(parts)
            if parent in known:
                return parent
    return None

def scan_repository(root, changed_file, *, max_files=DEFAULT_MAX_FILES, max_file_bytes=DEFAULT_MAX_FILE_BYTES):
    root = Path(root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Root is not a directory: {root}")
    changed = Path(changed_file)
    if not changed.is_absolute():
        changed = root / changed
    changed = changed.resolve(strict=True)
    if not _inside(changed, root):
        raise ValueError("Changed file must be inside the selected root.")
    if not changed.is_file() or changed.suffix != ".py":
        raise ValueError("Changed file must be an existing Python file inside the root.")

    warnings, modules, count = [], {}, 0
    for directory, dirs, names in os.walk(root, followlinks=False):
        current = Path(directory)
        dirs[:] = sorted(d for d in dirs if not (current / d).is_symlink() and _inside(current / d, root)
                         and d not in {".git", ".venv", "venv", "__pycache__", "node_modules"})
        for name in sorted(names):
            path = current / name
            if path.suffix != ".py" or path.is_symlink():
                continue
            if not _inside(path, root):
                warnings.append(f"Skipped path outside root: {path}")
                continue
            count += 1
            if count > max_files:
                warnings.append(f"Stopped after limit of {max_files} Python files.")
                break
            rel = path.relative_to(root).as_posix()
            try:
                size = path.stat().st_size
                if size > max_file_bytes:
                    warnings.append(f"Skipped oversized file ({size} bytes): {rel}")
                    continue
                source = path.read_text(encoding="utf-8")
                module = _module(path, root)
                modules[module] = {
                    "path": rel, "module": module, "package": path.name == "__init__.py",
                    "test": _is_test(path), "imports": _imports(source)
                }
            except (OSError, UnicodeError) as exc:
                warnings.append(f"Could not read {rel}: {exc}")
            except SyntaxError as exc:
                warnings.append(f"Could not parse {rel} at line {exc.lineno or '?'}: {exc.msg}")
        if count > max_files:
            break

    changed_rel = changed.relative_to(root).as_posix()
    changed_module = _module(changed, root)
    if changed_module not in modules:
        raise ValueError("Changed file could not be analyzed. Check syntax, encoding, and file-size limit.")

    graph, evidence = DependencyGraph(), []
    known = set(modules)
    for module in modules:
        graph.add_node(module)
    for importer, info in modules.items():
        for name, line, statement in info["imports"]:
            resolved = _resolve(name, info, known)
            if resolved and resolved != importer:
                graph.add_edge(importer, resolved)
                evidence.append({"importer": info["path"], "imported": modules[resolved]["path"],
                                 "line": line, "statement": statement})

    direct = sorted(modules[m]["path"] for m in graph.direct_dependents(changed_module))
    distances = graph.reverse_distances(changed_module)
    impacted = [{"file": modules[m]["path"], "module": m, "distance": d,
                 "reason": "Direct dependent" if d == 1 else f"Transitive dependency chain ({d} hops)"}
                for m, d in sorted(distances.items(), key=lambda x: (x[1], modules[x[0]]["path"]))]
    impacted_names = {changed_module, *distances}
    tests = {}
    for module, info in modules.items():
        if not info["test"]:
            continue
        imports_impacted = bool(graph.dependencies.get(module, set()) & impacted_names)
        filename_match = any(Path(modules[m]["path"]).stem.lower() in Path(info["path"]).stem.lower()
                             for m in impacted_names if Path(modules[m]["path"]).stem.lower() not in {"__init__", "test"})
        if module in distances or imports_impacted or filename_match:
            reasons = []
            if module in distances: reasons.append("depends on an impacted module")
            if imports_impacted: reasons.append("imports an impacted module")
            if filename_match: reasons.append("test filename matches an impacted module")
            tests[info["path"]] = {"file": info["path"], "confidence": "high" if imports_impacted or distances.get(module) == 1 else "medium",
                                   "reasons": sorted(set(reasons))}
    return {
        "root": str(root), "changed_file": changed_rel, "direct_dependents": direct,
        "impacted_files": impacted, "candidate_tests": sorted(tests.values(), key=lambda x: x["file"]),
        "edges": sorted(evidence, key=lambda e: (e["importer"], e["line"], e["imported"])),
        "warnings": warnings, "scanned_files": len(modules)
    }
