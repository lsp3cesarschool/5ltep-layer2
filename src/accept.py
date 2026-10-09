"""Acceptance of a run's artifact by the publish job (the job that can write to the repository).

The evaluate job has a read-only token and hands its outputs over as an artifact. Before anything
is committed, this module checks the artifact: only the expected paths, valid JSON, sizes within
limits, the earlier history kept as it was, record lists made only of numbers, and no published
field outside the expected ones. Then it copies the files into the repository: `results/rules/` and
`docs/data/rules/` are replaced as a whole (a rule removed from rules/ disappears from the page),
`run_log.jsonl` is appended.
"""

from __future__ import annotations

import json
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = [
    r"results/run_log\.jsonl", r"results/manifest\.json", r"results/sources\.json", r"results/history\.json",
    r"results/rules/[^/\\.][^/\\]*/result\.json",
    r"docs/data/layer2\.json", r"docs/data/status\.json", r"docs/data/status\.pt\.json",
    r"docs/data/rules/[^/\\.][^/\\]*\.json",
]
MAX_FILE_BYTES = 50 * 1024 * 1024
LIST_KEYS = {"rule", "rule_version", "evaluated_at", "run_id", "environment", "run_url", "note", "numbering",
             "sources", "counts", "total", "records", "members", "by_member", "by_period", "timeline"}


class Refused(Exception):
    pass


def _files(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def check(artifact: Path, repo: Path) -> list[str]:
    files = _files(artifact)
    if "docs/data/layer2.json" not in files or "results/history.json" not in files:
        raise Refused("artefato incompleto: faltam layer2.json ou history.json")
    for rel in files:
        if not any(re.fullmatch(p, rel) for p in ALLOWED):
            raise Refused(f"arquivo não esperado no artefato: {rel}")
        path = artifact / rel
        if path.stat().st_size > MAX_FILE_BYTES:
            raise Refused(f"arquivo grande demais: {rel}")
        text = path.read_text(encoding="utf-8")
        try:
            if rel.endswith(".jsonl"):
                [json.loads(line) for line in text.splitlines() if line.strip()]
            else:
                json.loads(text)
        except json.JSONDecodeError as exc:
            raise Refused(f"JSON inválido em {rel}: {exc}")

    # record lists: only the expected keys, and record numbers that are integers
    for rel in files:
        if rel.startswith("docs/data/rules/"):
            data = json.loads((artifact / rel).read_text(encoding="utf-8"))
            extra = set(data) - LIST_KEYS
            if extra:
                raise Refused(f"{rel}: campos não esperados {sorted(extra)}")
            for outcome, by_file in data.get("records", {}).items():
                for member, numbers in by_file.items():
                    if not all(isinstance(n, int) and not isinstance(n, bool) and n > 0 for n in numbers):
                        raise Refused(f"{rel}: lista {outcome}/{member} com valor que não é número de registro")

    # the history may only grow: the earlier runs must be kept exactly
    old_file = repo / "results" / "history.json"
    old = json.loads(old_file.read_text(encoding="utf-8")) if old_file.exists() else []
    new = json.loads((artifact / "results" / "history.json").read_text(encoding="utf-8"))
    if new[:len(old)] != old or len(new) != len(old) + 1:
        raise Refused("history.json não preserva as rodadas anteriores ou não acrescenta exatamente uma")
    return files


def apply(artifact: Path, repo: Path) -> list[str]:
    t0 = time.monotonic()
    files = check(artifact, repo)
    for folder in ("results/rules", "docs/data/rules"):
        shutil.rmtree(repo / folder, ignore_errors=True)
    for rel in files:
        src, dest = artifact / rel, repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel == "results/run_log.jsonl":
            with open(dest, "a", encoding="utf-8") as fh:
                fh.write(src.read_text(encoding="utf-8"))
        else:
            shutil.copyfile(src, dest)
    # the publish job's own time, per run (the dashboard plots it after download and processing)
    run_id = json.loads((artifact / "docs" / "data" / "layer2.json").read_text(encoding="utf-8")).get("run_id")
    log_file = repo / "docs" / "data" / "publish.json"
    log = json.loads(log_file.read_text(encoding="utf-8")) if log_file.exists() else []
    log.append({"run_id": run_id, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "accept_s": round(time.monotonic() - t0, 2), "files": len(files)})
    log_file.write_text(json.dumps(log[-200:], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return files
