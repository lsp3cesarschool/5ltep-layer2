"""signals.md: the latest run in plain Markdown, for readers that do not run the dashboard's JavaScript.

Written by the publish job (`main.py accept`) from the JSON it has just checked, like `changes.md` in
Layer 4. It holds counts only: no record numbers (those stay in docs/data/rules/ and on the
dashboard) and no value read from the portals.
"""

from __future__ import annotations

import json
from pathlib import Path

OUTCOMES = [("mismatch", "mismatch"), ("key_not_found", "key not found"), ("missing_value", "missing value"),
            ("invalid_value", "invalid value"), ("ambiguous_key", "ambiguous key")]


def _n(value) -> str:
    return f"{value:,}" if isinstance(value, int) else "–"


def _cell(text) -> str:
    return str(text or "").replace("|", "\\|").replace("\n", " ")


def _title(rule: dict) -> str:
    return rule.get("title_translations", {}).get("en") or rule.get("title") or rule["id"]


def render(page: dict) -> str:
    repo = page.get("portal", {}).get("repository", "lsp3cesarschool/5ltep-layer2")
    owner, name = repo.split("/", 1)
    dashboard = f"https://{owner}.github.io/{name}/"
    totals = page.get("totals", {})
    when = (page.get("generated_at") or "").replace("T", " ")[:16]
    run = f"[{page.get('run_id')}]({page['run_url']})" if page.get("run_url") else str(page.get("run_id", "–"))
    rate = f"{totals['l2_rate'] * 100:.1f}%" if totals.get("l2_rate") is not None else "–"
    history = page.get("history") or []
    previous = history[-2]["rules"] if len(history) >= 2 else {}

    lines = [
        f"# Signals in {page.get('primary_portal') or page.get('portal', {}).get('portal_url', '')}",
        "",
        "Plain-text summary of the latest run of Layer 2 (semantic policies), for readers that do not run",
        f"the JavaScript of the [dashboard]({dashboard}).",
        "Generated automatically by the publish job from the checked results; do not edit by hand. A signal is a record to review, never a verdict on the data. Only counts are",
        "shown here: the record numbers are on the dashboard and in [`docs/data/rules/`](docs/data/rules/),",
        "and no value read from the portals is published. Times are UTC.",
        "",
        f"- **Run:** {run}, finished {when} UTC ({page.get('environment', '–')})",
        f"- **Rules:** {totals.get('rules', 0)} ({totals.get('evaluated', 0)} evaluated, "
        f"{totals.get('not_evaluated', 0)} not evaluated)",
        f"- **Sources:** {totals.get('sources', 0)} CKAN resources ({totals.get('sources_ok', 0)} available)",
        f"- **Records flagged:** {_n(totals.get('signals'))}",
        f"- **L2 pass rate:** {rate} (checks without a signal / {_n(totals.get('checks'))} checks in scope; "
        "one check per record and rule)",
        "",
        "Signal types: `mismatch` (the check failed), `key not found` (no matching record in the other",
        "source), `missing value`, `invalid value` (unreadable as the declared type), `ambiguous key` (more",
        "than one match). Records outside a rule's scope (`where`) are not signals.",
        "",
        "## Rules (most signals first)",
        "",
        "| Rule | Records read | Signals | Previous run | Signal types |",
        "|---|---:|---:|---:|---|",
    ]
    rules = sorted(page.get("rules", []), key=lambda r: (-(r.get("signals") or 0), r["id"]))
    for r in rules:
        link = f"[{_cell(_title(r))}](rules/{r['file']})"
        if r.get("status") != "evaluated":
            reason = _cell(r.get("reason") or r.get("reason_code") or "")
            lines.append(f"| {link} | – | – | – | not evaluated: {reason} |")
            continue
        by = r.get("signals_by_outcome", {})
        types = "; ".join(f"{label} {_n(by[k])}" for k, label in OUTCOMES if by.get(k))
        before = previous.get(r["id"], {})
        prev = sum(v for k, v in (before.get("counts") or {}).items() if k not in ("match", "out_of_scope")) \
            if before.get("status") == "evaluated" else None
        lines.append(f"| {link} | {_n(r.get('total'))} | {_n(r.get('signals'))} | {_n(prev)} | {types or 'none'} |")

    lines += ["", "## Source health", "",
              "| Resource | Role | Status | Size | Download | Used by |",
              "|---|---|---|---:|---:|---|"]
    for s in page.get("sources", []):
        dl = s.get("download") or {}
        size = f"{dl['bytes'] / 1e6:,.1f} MB" if dl.get("bytes") else "–"
        secs = f"{dl['seconds']:,.1f} s" if dl.get("seconds") is not None else "–"
        status = "available" if s.get("status") == "ok" else f"failed: {_cell(s.get('reason'))}"
        lines.append(f"| {_cell(s.get('label'))} | {s.get('role', '')} | {status} | {size} | {secs} | "
                     f"{', '.join(s.get('used_by', []))} |")
    lines.append("")
    return "\n".join(lines)


def write(repo: Path) -> Path:
    page = json.loads((repo / "docs" / "data" / "layer2.json").read_text(encoding="utf-8"))
    out = repo / "signals.md"
    out.write_text(render(page), encoding="utf-8", newline="\n")
    return out
