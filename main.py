"""5L-TEP Layer 2 (Semantic Policies) command line.

Sub-commands:

  validate   check rule files against the authoring format 1.0 (schema, cross references,
             regular-expression subset); exit code 1 when any error is found

Examples:
  python main.py validate                     # every rules/**/*.yaml
  python main.py validate rules/territory     # one folder
  python main.py validate my-rule.yaml --no-name-check
  python main.py validate --format json

The engine that resolves CKAN resources and evaluates rules is not implemented yet.
"""

import argparse
import sys

from src import validate


def cmd_validate(args) -> int:
    findings = validate.validate_paths(args.paths or ["rules"], check_names=not args.no_name_check)
    errors = sum(f.level == validate.ERROR for f in findings)
    warnings = len(findings) - errors
    if args.format == "json":
        print(validate.as_json(findings))
    else:
        for f in findings:
            print(f.render())
        print(f"{errors} erro(s), {warnings} aviso(s)")
    return 1 if errors else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="5L-TEP Layer 2 (Semantic Policies)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate", help="validate rule files")
    p.add_argument("paths", nargs="*", help="files or folders (default: rules)")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--no-name-check", action="store_true", help="do not require <id>.yaml as file name")
    p.set_defaults(func=cmd_validate)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
