import argparse, json, sys
from pathlib import Path
from .analyzer import scan_repository

def main(argv=None):
    parser = argparse.ArgumentParser(prog="ripplemap", description="Estimate Python change impact with local static import analysis.")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="scan a repository")
    scan.add_argument("root")
    scan.add_argument("--changed", required=True)
    scan.add_argument("--out", default="ripplemap-report.json")
    args = parser.parse_args(argv)
    try:
        report = scan_repository(args.root, args.changed)
        output = Path(args.out).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"RippleMap error: {exc}", file=sys.stderr)
        return 2
    print(f"RippleMap scan complete: {report['scanned_files']} Python files analyzed")
    print(f"Changed file: {report['changed_file']}")
    print(f"Direct dependents: {len(report['direct_dependents'])}")
    print(f"Impacted files: {len(report['impacted_files'])}")
    print(f"Candidate tests: {len(report['candidate_tests'])}")
    print(f"Warnings: {len(report['warnings'])}")
    print(f"Report written to: {output.resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
