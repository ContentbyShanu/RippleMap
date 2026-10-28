# RippleMap
### Change-impact intelligence for Python repositories

RippleMap estimates which local Python files may be affected when a file changes. It parses source with Python's standard-library AST, resolves local imports, follows reverse dependency paths, and suggests candidate tests.

**Free and offline-first:** no API keys, no paid services, no third-party Python dependencies, and no network requests from the Python engine. RippleMap never imports or executes the repository being scanned.

## Requirements
- Python 3.10+
- GitHub account (only if you want to publish the static demo)

## Quick start
From this directory:

```bash
python -m ripplemap scan examples/sample_project --changed app/service.py --out report.json
```

Windows alternative: `py -m ripplemap scan examples/sample_project --changed app/service.py --out report.json`

Run tests:

```bash
python -m unittest discover -s tests -v
```

## CLI
`python -m ripplemap scan ROOT --changed FILE [--out FILE]`

- `ROOT`: repository directory to inspect.
- `--changed`: Python file relative to `ROOT`, or absolute path inside it.
- `--out`: output JSON path; default is `ripplemap-report.json`.

The JSON report contains the changed file, direct dependents, direct/transitive impacted files, candidate tests, resolved import evidence, warnings, and number of analyzed files.

## Dashboard demo
`docs/index.html` is a responsive static dashboard with sample data, filtering, evidence details, and JSON export. It is **not a live scan**; the Python engine runs locally. Open `docs/index.html` in a browser to preview.

### Publish on GitHub Pages
1. Create a new repository and upload the project files.
2. Open **Settings → Pages**.
3. Choose **Deploy from a branch**, select `main` and `/docs`, then save.
4. Wait for GitHub to display the published URL.

## Security model
- Reads and parses Python files; does not import or execute scanned code.
- Makes no network requests and needs no API key.
- Skips symlinks and checks that resolved paths remain inside the selected root.
- Limits file count and file size; reports syntax/read warnings.
- Only scans Python files inside the selected directory.

Only scan repositories you are authorized to inspect. Static analysis is not a security audit.

## Limitations
Dynamic imports, reflection, framework configuration, plugin registries, runtime-generated dependencies, and unusual package layouts may be missed. External packages are not resolved. An impact path means “possibly affected,” not “definitely broken.” Test suggestions are heuristic; run the actual test suite.

## Layout
- `ripplemap/`: analyzer, graph, models, CLI
- `tests/`: automated tests
- `examples/sample_project/`: example repository
- `docs/`: static GitHub Pages dashboard

## License
MIT — see [LICENSE](LICENSE).
