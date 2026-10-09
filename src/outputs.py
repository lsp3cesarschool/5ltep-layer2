"""Files written by a run, as in the other layers: `results/` is the record, `docs/data/` feeds the
dashboard. Nothing here carries a value read from a portal: only counts, record numbers (per file
of the resource, 1 = first line after the header), SHA-256 of the evaluated bytes and metadata
published by CKAN itself.

results/run_log.jsonl            one line per stage, source and rule (appended)
results/manifest.json            the run: engine version, rule files and source bytes (hashes)
results/sources.json             integrity of each CKAN resource in this run
results/history.json             per run: status and counts of each rule, status of each source
results/rules/<id>/result.json   counts and sources of one rule
docs/data/layer2.json            the dashboard: totals, one card per rule, sources, recent history
docs/data/rules/<id>.json        record numbers of each outcome (the "see list" download)
docs/data/status.json            badge (shields.io endpoint), and status.pt.json
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import time
import subprocess
from pathlib import Path

import duckdb

from src.engine import EVALUATED, SIGNALS, evaluated_source
from src.fetch import OK

HISTORY_KEPT_ON_PAGE = 52


def _write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def _engine() -> dict:
    root = Path(__file__).resolve().parent.parent
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                                text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "src", "main.py", "schema"],
                                    cwd=root, capture_output=True, text=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    return {"commit": commit, "uncommitted_changes": dirty, "python": platform.python_version(),
            "duckdb": duckdb.__version__}


def run_identity() -> dict:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return {"run_id": os.environ.get("GITHUB_RUN_ID"), "environment": "github-actions",
                "run_url": f"{os.environ.get('GITHUB_SERVER_URL')}/{os.environ.get('GITHUB_REPOSITORY')}"
                           f"/actions/runs/{os.environ.get('GITHUB_RUN_ID')}"}
    return {"run_id": None, "environment": "local", "run_url": None,
            "note": "ensaio local: serve para depurar, não é resultado publicado"}


def _rule_path(entry: dict, rules_root: Path) -> str:
    try:
        return entry["file"].resolve().relative_to(rules_root.resolve()).as_posix()
    except ValueError:
        return entry["file"].name


def _card(entry: dict, rules_root: Path, run: dict) -> dict:
    data = entry["data"] or {}
    desc = data.get("description", {})
    rel = _rule_path(entry, rules_root)
    card = {
        "id": entry["id"], "rule_version": data.get("rule_version"), "origin": data.get("origin"),
        "file": rel, "folder": rel.rsplit("/", 1)[0] if "/" in rel else "",
        "language": desc.get("language"), "title": desc.get("title"),
        "title_translations": desc.get("title_translations", {}), "text": desc.get("text"),
        "justification": desc.get("justification"), "exceptions": desc.get("exceptions", []),
        "examples": desc.get("examples", []), "template": (data.get("check") or {}).get("template"),
        "evaluated_source": evaluated_source(data["check"]) if data.get("check") else None,
        "timeline": (data.get("check") or {}).get("timeline"),
        "exposure": data.get("exposure", "records"),
        "datasets": [{"source": sid, "label": s.get("resource")} for sid, s in entry.get("sources", {}).items()],
        "status": entry["status"], "reason_code": entry.get("reason_code"), "reason": entry.get("reason"),
    }
    if entry["status"] == EVALUATED:
        card.update(evaluated_at=entry["evaluated_at"], total=entry["total"], counts=entry["counts"],
                    signals=sum(entry["counts"][o] for o in SIGNALS),
                    signals_by_outcome={o: entry["counts"][o] for o in SIGNALS}, list=f"rules/{card['id']}.json")
    return card


def download_speed(sources: list[dict], timings: dict | None = None) -> dict:
    """Download speed of this run, separately for the primary portal and the secondary ones:
    total bytes over total download time of the resources that downloaded."""
    speed = {}
    for role in ("primary", "secondary"):
        done = [s["download"] for s in sources if s["role"] == role and s["download"].get("bytes") is not None
                and s["download"].get("seconds")]
        size, secs = sum(d["bytes"] for d in done), sum(d["seconds"] for d in done)
        speed[role] = {"resources": len(done), "bytes": size, "seconds": round(secs, 2),
                       "mb_per_s": round(size / 1e6 / secs, 3) if secs else None}
    if timings and timings.get("processing_s"):
        size, secs = timings["bytes_processed"], timings["processing_s"]
        speed["processing"] = {"bytes": size, "seconds": secs, "mb_per_s": round(size / 1e6 / secs, 3) if secs else None}
    return speed


def write(run: dict, out: Path, rules_root: Path) -> dict:
    t_outputs = time.monotonic()
    ident = run_identity()
    results, data = out / "results", out / "docs" / "data"
    sources = [f.record() for f in run["fetched"]]
    cards = [_card(e, rules_root, run) for e in run["rules"]]
    speed = download_speed(sources, run.get("timings"))
    timings = dict(run.get("timings") or {})

    # results/ -----------------------------------------------------------------------------------
    manifest = {**ident, "started_at": run["started_at"], "finished_at": run["finished_at"],
                "engine": _engine(), "primary_portal": run.get("primary_portal"), "download_speed": speed,
                "rules": [{"id": c["id"], "rule_version": c["rule_version"], "file": c["file"],
                           "sha256": hashlib.sha256(e["rule_text"]).hexdigest()}
                          for c, e in zip(cards, run["rules"])],
                "sources": [{"label": s["label"], "status": s["status"], "resource_id": s["resource"].get("id"),
                             "metadata_modified": s["resource"].get("metadata_modified"),
                             "bytes": s["download"].get("bytes"), "sha256": s["download"].get("sha256")}
                            for s in sources]}
    _write(results / "manifest.json", manifest)
    _write(results / "sources.json", {**ident, "checked_at": run["finished_at"], "sources": sources})
    for card, entry in zip(cards, run["rules"]):
        _write(results / "rules" / card["id"] / "result.json",
               {**ident, **{k: v for k, v in card.items() if k not in ("examples",)},
                "sources": entry.get("sources", {})})

    history_file = results / "history.json"
    history = json.loads(history_file.read_text(encoding="utf-8")) if history_file.exists() else []
    history.append({"run_id": ident["run_id"], "environment": ident["environment"], "at": run["finished_at"],
                    "rules": {c["id"]: {"status": c["status"], "reason_code": c["reason_code"],
                                        "total": c.get("total"), "counts": c.get("counts")} for c in cards},
                    "sources": {s["label"]: s["status"] for s in sources}, "download_speed": speed,
                    "timings": timings})
    _write(history_file, history)

    log = results / "run_log.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8") as fh:
        for s in sources:
            fh.write(json.dumps({"at": run["finished_at"], "run_id": ident["run_id"], "stage": "fetch",
                                 "source": s["label"], "status": s["status"], "reason": s["reason"],
                                 "bytes": s["download"].get("bytes"), "sha256": s["download"].get("sha256"),
                                 "seconds": s["download"].get("seconds")}, ensure_ascii=False) + "\n")
        fh.write(json.dumps({"at": run["finished_at"], "run_id": ident["run_id"], "stage": "download_speed",
                             **speed}, ensure_ascii=False) + "\n")
        for c in cards:
            fh.write(json.dumps({"at": run["finished_at"], "run_id": ident["run_id"], "stage": "rule",
                                 "rule": c["id"], "status": c["status"], "reason_code": c["reason_code"],
                                 "total": c.get("total"), "counts": c.get("counts")}, ensure_ascii=False) + "\n")

    # docs/data/ ---------------------------------------------------------------------------------
    for card, entry in zip(cards, run["rules"]):
        target = data / "rules" / f"{card['id']}.json"
        if entry["status"] == EVALUATED:
            _write(target, {"rule": card["id"], "rule_version": card["rule_version"], "evaluated_at": entry["evaluated_at"],
                            **ident, "numbering": "registro por arquivo (o publicado, ou cada arquivo dentro do zip); 1 = primeira linha após o cabeçalho",
                            "sources": {sid: {"label": s["resource"], "file": s.get("file"), "files": s.get("files"),
                                              "url": s.get("url"),
                                              "archive_members": s.get("archive_members"), "sha256": s["sha256"],
                                              "records": s.get("records")}
                                        for sid, s in entry["sources"].items()},
                            "counts": entry["counts"], "total": entry["total"],
                            # exposure "counts" (health, education...): never the record numbers
                            "records": {} if card["exposure"] == "counts" else entry["records"],
                            "members": entry["members"], "by_member": entry["by_member"], "by_period": entry["by_period"],
                            "timeline": card.get("timeline")})
        else:
            target.unlink(missing_ok=True)

    timings["outputs_s"] = round(time.monotonic() - t_outputs, 2)
    history[-1]["timings"] = timings
    _write(history_file, history)
    evaluated = [c for c in cards if c["status"] == EVALUATED]
    totals = {"rules": len(cards), "evaluated": len(evaluated), "not_evaluated": len(cards) - len(evaluated),
              "sources": len(sources), "sources_ok": sum(s["status"] == OK for s in sources),
              "signals": sum(c["signals"] for c in evaluated)}
    # L2 pass rate (SOFTENG 2026, Qs = w1·L1 + w2·L2 + ...): checks without a signal / checks in scope,
    # one check per (record, rule); records out of scope and rules not evaluated do not count
    totals["checks"] = sum(c["total"] - c["counts"].get("out_of_scope", 0) for c in evaluated)
    totals["l2_rate"] = round(1 - totals["signals"] / totals["checks"], 4) if totals["checks"] else None
    _write(data / "layer2.json", {"layer": 2, **ident, "generated_at": run["finished_at"],
                                  "started_at": run["started_at"], "totals": totals, "rules": cards,
                                  "sources": sources, "engine": manifest["engine"], "rule_files": manifest["rules"],
                                  "primary_portal": run.get("primary_portal"), "download_speed": speed, "timings": timings,
                                  "portal": run.get("portal", {}),
                                  "history": history[-HISTORY_KEPT_ON_PAGE:]})

    if not cards:
        color = "lightgrey"
    elif totals["not_evaluated"] == 0 and totals["sources_ok"] == totals["sources"]:
        color = "brightgreen"
    else:
        color = "orange" if evaluated else "red"
    _write(data / "status.json", {"schemaVersion": 1, "label": "Layer 2", "color": color,
                                  "message": f"{totals['evaluated']}/{totals['rules']} rules · "
                                             f"{totals['sources_ok']}/{totals['sources']} sources ok · "
                                             f"{totals['signals']} signals"})
    _write(data / "status.pt.json", {"schemaVersion": 1, "label": "Camada 2", "color": color,
                                     "message": f"{totals['evaluated']}/{totals['rules']} regras · "
                                                f"{totals['sources_ok']}/{totals['sources']} fontes ok · "
                                                f"{totals['signals']} sinais"})
    return totals
