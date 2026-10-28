 # RippleMap

**Change-impact intelligence for Python repositories**

RippleMap is a lightweight, offline-first static analysis tool that estimates which local Python files and tests may be affected when a source file changes. It parses code with Python’s standard-library AST, resolves local imports, follows reverse dependency paths, and suggests candidate tests — without executing any of the scanned code.

**Repository:** [https://github.com/ContentbyShanu/RippleMap](https://github.com/ContentbyShanu/RippleMap)  
**Dashboard (static demo):** [https://contentbyshanu.github.io/RippleMap/](https://contentbyshanu.github.io/RippleMap/)

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [How RippleMap Works](#how-ripplemap-works)
- [Technology Stack and Requirements](#technology-stack-and-requirements)
- [Installation and Setup](#installation-and-setup)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
- [Example Scan (Sample Project)](#example-scan-sample-project)
- [JSON Report Format](#json-report-format)
- [Dashboard and GitHub Pages](#dashboard-and-github-pages)
- [Running the Dashboard Locally](#running-the-dashboard-locally)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Security and Privacy](#security-and-privacy)
- [Known Limitations](#known-limitations)
- [Example Use Cases](#example-use-cases)
- [Contributing](#contributing)
- [License](#license)
- [Links](#links)

---

## Overview

RippleMap helps developers understand the potential blast radius of a change before they commit or open a pull request. Given a repository root and a changed Python file, it builds a local dependency graph from import statements, computes reverse dependents (files that import the changed module, directly or transitively), and ranks candidate tests that are likely to exercise the affected code.

The tool is designed for everyday use by Python developers, students, open-source contributors, and engineering teams who want a fast, zero-dependency way to focus review and testing effort.

It never imports or executes the code under analysis, requires no API keys or network access, and has no third-party Python dependencies.

---

## Problem Statement

When you change a single module in a non-trivial Python project, it is easy to miss downstream files that import it — or tests that should be re-run. Manual grepping is incomplete; full test suites can be slow; and many impact tools are heavyweight or require runtime instrumentation.

RippleMap addresses this by providing a quick, static “who depends on this file?” answer based solely on local import structure. The result is a focused list of impacted files and candidate tests that can guide code review and test selection.

---

## Key Features

- **Static AST analysis** — Uses only the Python standard library (`ast`) to parse source files.
- **Local import resolution** — Resolves absolute and relative imports within the scanned repository.
- **Reverse dependency tracing** — Finds direct and transitive dependents of the changed module.
- **Candidate test suggestions** — Heuristically identifies tests that import impacted modules or whose filenames match them.
- **Evidence trail** — Records the exact import statements and line numbers that created each graph edge.
- **Safety limits** — Caps the number of files and file size; skips symlinks and paths outside the root.
- **Offline and dependency-free** — No external packages, no network requests, no code execution.
- **JSON report** — Machine-readable output for tooling or further processing.
- **Static dashboard** — A responsive HTML/JS/CSS demo that visualizes sample impact data (not a live scanner).

---

## How RippleMap Works

1. **Root and changed-file validation**  
   The tool resolves the repository root and the changed file, ensuring the changed file is an existing `.py` file strictly inside the root.

2. **Directory walk**  
   It walks the tree (never following symlinks), skipping common non-source directories (`.git`, `.venv`, `venv`, `__pycache__`, `node_modules`). Only `.py` files are considered.

3. **Parsing and module mapping**  
   Each eligible file is read (with size and count limits). The AST is parsed to extract `import` and `from … import` statements. Files are mapped to dotted module names relative to the root.

4. **Graph construction**  
   A directed graph is built where an edge `A → B` means “A imports B”. Only local modules that exist in the repository are linked.

5. **Reverse impact analysis**  
   Starting from the changed module, the graph is traversed in the reverse direction (dependents) to compute direct dependents and transitive distances (number of hops).

6. **Test candidate selection**  
   Test files (identified by name patterns or location under a `tests` directory) are scored if they:
   - Depend on an impacted module, or
   - Import an impacted module, or
   - Have a filename that matches an impacted module stem.

7. **Report generation**  
   A JSON document is written containing the changed file, direct dependents, full impact list (with distances and reasons), candidate tests (with confidence and reasons), import evidence, warnings, and the number of scanned files.

---

## Technology Stack and Requirements

| Component              | Details                                      |
|------------------------|----------------------------------------------|
| Language               | Python 3.10+                                 |
| Core libraries         | Standard library only (`ast`, `pathlib`, `os`, `argparse`, `json`, `collections`) |
| Packaging              | `pyproject.toml` (setuptools)                |
| Dashboard              | Static HTML + CSS + vanilla JavaScript       |
| Tests                  | `unittest` (stdlib)                          |
| License                | MIT                                          |

No third-party Python packages are required at runtime or for development of the core engine.

---

## Installation and Setup

### Clone the repository

```bash
git clone https://github.com/ContentbyShanu/RippleMap.git
cd RippleMap
```

### Optional: install as an editable package

```bash
python -m pip install -e .
```

After installation the `ripplemap` console script is available. You can also always run the module form:

```bash
python -m ripplemap ...
```

### Platform notes

- **Linux / macOS** — Use `python` or `python3`.
- **Windows** — Use `python` or `py`.

No additional system packages are needed beyond a supported Python interpreter.

---

## Quick Start

From the repository root:

```bash
python -m ripplemap scan examples/sample_project --changed app/service.py --out report.json
```

Windows alternative:

```bash
py -m ripplemap scan examples/sample_project --changed app/service.py --out report.json
```

Expected console output (exact numbers depend on the sample):

```
RippleMap scan complete: N Python files analyzed
Changed file: app/service.py
Direct dependents: ...
Impacted files: ...
Candidate tests: ...
Warnings: ...
Report written to: .../report.json
```

Inspect the report:

```bash
# Linux / macOS
cat report.json

# or pretty-print with Python
python -m json.tool report.json
```

---

## CLI Reference

```
python -m ripplemap scan ROOT --changed FILE [--out FILE]
```

| Argument       | Required | Description |
|----------------|----------|-------------|
| `ROOT`         | Yes      | Path to the repository (or project) directory to analyze. |
| `--changed`    | Yes      | Path to the changed Python file, relative to `ROOT` or an absolute path that resolves inside `ROOT`. |
| `--out`        | No       | Path for the JSON report. Default: `ripplemap-report.json`. Parent directories are created if needed. |

Exit codes:

- `0` — success
- `2` — validation or I/O error (message written to stderr)

The CLI is defined in `ripplemap/cli.py` and registered as the `ripplemap` entry point in `pyproject.toml`.

---

## Example Scan (Sample Project)

The repository includes a minimal sample under `examples/sample_project/`:

```
examples/sample_project/
├── app/
│   ├── __init__.py
│   ├── routes.py          # imports app.service
│   ├── service.py         # the “changed” file
│   └── worker.py          # imports app.service
└── tests/
    ├── __init__.py
    └── test_service.py    # imports app.service
```

Run:

```bash
python -m ripplemap scan examples/sample_project --changed app/service.py --out sample-report.json
```

You should see `app/routes.py` and `app/worker.py` listed as direct dependents, and `tests/test_service.py` among the candidate tests. The `edges` array in the JSON report will contain the concrete import statements that produced those links.

---

## JSON Report Format

The report is a single JSON object with the following fields (generated by `scan_repository` in `ripplemap/analyzer.py`):

| Field                | Type     | Description |
|----------------------|----------|-------------|
| `root`               | string   | Absolute path of the scanned root. |
| `changed_file`       | string   | Path of the changed file relative to root (POSIX-style). |
| `direct_dependents`  | string[] | Relative paths of modules that directly import the changed module. |
| `impacted_files`     | object[] | List of impacted modules. Each entry has: `file`, `module`, `distance` (hops), `reason`. |
| `candidate_tests`    | object[] | Suggested tests. Each entry has: `file`, `confidence` (`high` / `medium`), `reasons` (list of strings). |
| `edges`              | object[] | Import evidence. Each entry has: `importer`, `imported`, `line`, `statement`. |
| `warnings`           | string[] | Non-fatal issues (parse errors, oversized files, limit reached, etc.). |
| `scanned_files`      | integer  | Number of Python files successfully analyzed. |

Distances start at 1 for direct dependents. The changed file itself is not listed in `impacted_files`.

---

## Dashboard and GitHub Pages

A static, responsive dashboard is provided at the repository root (`index.html`, `app.js`, `styles.css`). It displays **sample / illustrative data** only. It does **not** run live scans and does not call the Python engine.

The live demo is available at:

**https://contentbyshanu.github.io/RippleMap/**

Because the dashboard files live at the repository root, GitHub Pages is configured to serve from the `main` branch root (not a `/docs` folder).

To enable or re-enable GitHub Pages on a fork:

1. Go to the repository **Settings → Pages**.
2. Under “Build and deployment”, set Source to **Deploy from a branch**.
3. Select branch `main` and folder `/ (root)`.
4. Save and wait for the site to become available at `https://<username>.github.io/RippleMap/`.

---

## Running the Dashboard Locally

No build step is required. From the repository root:

```bash
# any static file server, e.g.
python -m http.server 8000
```

Then open http://localhost:8000 in a browser. The page will load the embedded sample data.

You can also open `index.html` directly in a browser (some browsers restrict `file://` features such as the Clipboard API used by the “Copy” button).

---

## Running Tests

The test suite uses the standard-library `unittest` framework:

```bash
python -m unittest discover -s tests -v
```

Tests cover:

- Impact detection and candidate-test selection (`tests/test_analyzer.py`)
- Reverse-distance computation and cycle handling (`tests/test_graph.py`)

---

## Project Structure

```
RippleMap/
├── examples/
│   └── sample_project/
│       ├── app/
│       │   ├── __init__.py
│       │   ├── routes.py
│       │   ├── service.py
│       │   └── worker.py
│       └── tests/
│           ├── __init__.py
│           └── test_service.py
├── ripplemap/
│   ├── __init__.py          # package version
│   ├── __main__.py          # python -m entry point
│   ├── analyzer.py          # AST parsing, import resolution, report assembly
│   ├── cli.py               # argument parsing and CLI orchestration
│   └── graph.py             # DependencyGraph (forward + reverse edges)
├── tests/
│   ├── test_analyzer.py
│   └── test_graph.py
├── app.js                   # dashboard logic (sample data)
├── index.html               # dashboard markup
├── styles.css               # dashboard styles
├── pyproject.toml
├── LICENSE
├── .gitignore
└── README.md
```

---

## Security and Privacy

RippleMap is intentionally conservative:

- It **reads and parses** Python source only; it never imports or executes scanned code.
- It makes **no network requests** and requires **no API keys**.
- Symlinks are **not followed**.
- Resolved paths are checked to remain **inside the selected root**.
- File-count (`DEFAULT_MAX_FILES = 10_000`) and file-size (`DEFAULT_MAX_FILE_BYTES = 1_000_000`) limits are enforced.
- Only files with a `.py` suffix inside the chosen directory tree are examined.

Only scan repositories you are authorized to inspect. Static analysis is **not** a security audit and does not guarantee the absence of vulnerabilities or the completeness of dependency information.

---

## Known Limitations

Because analysis is purely static and limited to local import statements:

- Dynamic imports (`importlib`, `__import__`, string-based loading) are invisible.
- Framework-specific wiring (plugins, entry points, decorators that register handlers at runtime) is not modeled.
- External / third-party packages are never resolved; only modules present in the scanned tree are linked.
- Unusual package layouts, namespace packages, or non-standard path manipulations may produce incomplete graphs.
- An impact path means “there is a static import chain,” **not** “the change will break this file at runtime.”
- Test suggestions are heuristic; always run your real test suite.

Warnings collected during the scan (syntax errors, unreadable files, size limits, etc.) are included in the JSON report.

---

## Example Use Cases

- **Pre-commit / pre-PR checklist** — Quickly see which modules and tests are likely affected by a local change.
- **Code review focus** — Reviewers can prioritize files that appear in the impact list.
- **Onboarding** — New contributors can explore how a core module is used throughout a repository.
- **Test selection** — Generate a short list of candidate tests to run before a full suite.
- **Teaching / learning** — Demonstrate static dependency analysis with a small, self-contained sample project.

---

## Contributing

Contributions that improve accuracy, clarity, or safety of the static analysis are welcome. Please:

1. Keep the core engine free of third-party runtime dependencies.
2. Prefer the standard library.
3. Add or update unit tests for new behavior.
4. Preserve the offline, non-executing nature of the tool.
5. Open an issue or pull request on the GitHub repository.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for the full text.

```
MIT License

Copyright (c) 2026 RippleMap contributors
```

---

## Links

- **Source repository:** [https://github.com/ContentbyShanu/RippleMap](https://github.com/ContentbyShanu/RippleMap)
- **Static dashboard demo:** [https://contentbyshanu.github.io/RippleMap/](https://contentbyshanu.github.io/RippleMap/)

---

*RippleMap v1.0.0 — Static analysis for Python. Designed for clarity. Built for safer changes.*
