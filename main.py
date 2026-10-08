"""5L-TEP Layer 2 (Semantic Policies) command line.

Sub-commands:

  validate   check rule files against format 1.0 (schema and cross references);
             exit code 1 when any error is found
  run        fetch every CKAN resource the rules name (once each), evaluate the rules and write
             results/ and docs/data/ under --out (default work/out: a local run is a test,
             never a published result)
  accept     (publish job) check a run's artifact and copy it into results/ and docs/data/

Examples:
  python main.py validate                     # every rules/**/*.yaml
  python main.py validate rules/territory     # one folder
  python main.py validate my-rule.yaml --no-name-check
  python main.py validate --format json
  python main.py run                          # every rule, outputs in work/out

"""

import argparse
import sys
from pathlib import Path

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


def cmd_run(args) -> int:
    from src import engine, outputs

    paths = args.paths or ["rules"]
    run = engine.run(paths, Path(args.work), keep_downloads=args.keep_downloads)
    if not run["rules"]:
        print("nenhuma regra encontrada")
        return 1
    totals = outputs.write(run, Path(args.out), Path("rules"))
    print(f"{totals['evaluated']}/{totals['rules']} regra(s) avaliada(s), "
          f"{totals['sources_ok']}/{totals['sources']} fonte(s) ok, {totals['signals']} sinal(is); "
          f"saídas em {Path(args.out) / 'results'} e {Path(args.out) / 'docs' / 'data'}")
    return 0


def cmd_accept(args) -> int:
    from src import accept

    try:
        files = accept.apply(Path(args.dir), Path("."))
    except accept.Refused as exc:
        print(f"artefato recusado: {exc}")
        return 1
    print(f"artefato aceito: {len(files)} arquivo(s)")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="5L-TEP Layer 2 (Semantic Policies)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate", help="validate rule files")
    p.add_argument("paths", nargs="*", help="files or folders (default: rules)")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--no-name-check", action="store_true", help="do not check the file name (the rule identifier) format")
    p.set_defaults(func=cmd_validate)
    p = sub.add_parser("run", help="evaluate the rules against the CKAN portals")
    p.add_argument("paths", nargs="*", help="rule files or folders (default: rules)")
    p.add_argument("--out", default="work/out", help="folder for results/ and docs/data/ (default: work/out)")
    p.add_argument("--work", default="work", help="folder for downloads and work files (default: work)")
    p.add_argument("--keep-downloads", action="store_true", help="keep the downloaded files after the run")
    p.set_defaults(func=cmd_run)
    p = sub.add_parser("accept", help="check a run's artifact and copy it into results/ and docs/data/")
    p.add_argument("--dir", required=True, help="folder of the downloaded artifact")
    p.set_defaults(func=cmd_accept)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
