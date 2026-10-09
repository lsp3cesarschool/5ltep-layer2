"""The evaluation engine: rules in, counts and record numbers out.

A run (1) validates every rule file, (2) fetches each CKAN resource the valid rules name, once,
(3) reads, for each rule, only the declared columns of the declared archive members into a UTF-8
work file, numbering the records of each member (1 = first line after the header), (4) loads those
files into an in-memory DuckDB, turns external access off and runs the fixed SQL of the rule's
template. No SQL comes from a rule file: the template's SQL is in this module and the rule only
names columns, which reach DuckDB as quoted identifiers of tables the engine built.

Every record read gets exactly one outcome; the counts must add up to the records read. A rule
whose sources could not be fetched or read is `not_evaluated`, with the reason; there is no
partial result and no reuse of a previous run.
"""

from __future__ import annotations

import csv
import json
import fnmatch
import io
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

import duckdb

from src import templates, validate
from src.fetch import OK, Fetched, ResourceKey, fetch

EVALUATED, NOT_EVALUATED = "evaluated", "not_evaluated"
OUTCOMES, SIGNALS = templates.OUTCOMES, templates.SIGNALS     # every outcome but match and out_of_scope is a signal

csv.field_size_limit(1 << 30)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ReadError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


@dataclass
class Read:
    """One rule source read into a UTF-8 work file with columns __member, __record, <declared>."""
    path: Path
    columns: list[str]
    members: list[dict] = field(default_factory=list)   # name, records
    missing: dict[str, list[str]] = field(default_factory=dict)   # member -> declared columns it lacks

    def view(self, columns: list[str]) -> "Read":
        """The same work file seen by one rule: only its columns; ReadError if a member lacks one."""
        for member, absent in self.missing.items():
            lacking = [c for c in columns if c in absent]
            if lacking:
                raise ReadError("column_missing", f"{member}: colunas ausentes {lacking}")
        return Read(self.path, list(columns), self.members, {})

    @property
    def records(self) -> int:
        return sum(m["records"] for m in self.members)


# --- reading -----------------------------------------------------------------------------------

def published_file(fetched: Fetched) -> str:
    """The exact name of the published file (from its URL), e.g. termo_de_embargo.csv."""
    name = PurePosixPath(unquote(urlparse(fetched.resource.get("url") or "").path)).name
    return name or fetched.key.name


def _members(fetched: Fetched, source: dict):
    """(file name, binary stream) for every file to read: each published file of the source (one, or
    one per resource matching a name pattern), and inside a zip each member matching the pattern."""
    parts = fetched.parts or [{"name": published_file(fetched), "path": fetched.path}]
    for part in parts:
        yield from _part_members(part, source)


def _part_members(part: dict, source: dict):
    archive = source.get("archive")
    if archive is None:
        with open(part["path"], "rb") as fh:
            yield part["name"], fh
        return
    try:
        zf = zipfile.ZipFile(part["path"])
    except zipfile.BadZipFile:
        raise ReadError("archive_invalid", f"{part['name']}: o recurso não é um zip válido")
    with zf:
        names = sorted(n for n in zf.namelist() if not n.endswith("/")
                       and fnmatch.fnmatchcase(n.rsplit("/", 1)[-1], archive["members"]))
        if not names:
            raise ReadError("member_missing", f'{part["name"]}: nenhum arquivo do zip casa com "{archive["members"]}"; '
                                              f"conteúdo: {sorted(zf.namelist())[:20]}")
        for name in names:
            with zf.open(name) as fh:
                yield name, fh


def read_source(fetched: Fetched, source: dict, out: Path, columns: list[str] | None = None) -> Read:
    """Reads the declared columns (or `columns`, the union several rules need) of every member into
    one UTF-8 work file. A column a member lacks is written empty and recorded in `missing`; each rule
    then refuses only the columns it declared (`Read.view`)."""
    spec, wanted = source["file"], list(columns or source["columns"])
    result = Read(out, wanted)
    with open(out, "w", encoding="utf-8", newline="") as dest:
        writer = csv.writer(dest)
        writer.writerow(["__member", "__record", *wanted])
        for name, raw in _members(fetched, source):
            # utf-8-sig drops a BOM before the CSV is parsed (with it, a quoted first header keeps its quotes)
            encoding = "utf-8-sig" if spec["encoding"] == "utf-8" else spec["encoding"]
            text = io.TextIOWrapper(raw, encoding=encoding, errors="strict", newline="")
            reader = csv.reader(text, delimiter=spec["delimiter"])
            record = 0
            try:
                header = next(reader, None)
                if header is None:
                    result.members.append({"name": name, "records": 0})
                    continue
                header = [h.lstrip("﻿") for h in header]
                missing = [c for c in wanted if c not in header]
                if missing:
                    result.missing[name] = missing
                    if columns is None:
                        raise ReadError("column_missing", f"{name}: colunas ausentes {missing}; cabeçalho: {header[:40]}")
                index = [header.index(c) if c in header else None for c in wanted]
                width = len(header)
                for row in reader:
                    record += 1
                    if len(row) < width:
                        row = row + [""] * (width - len(row))
                    writer.writerow([name, record, *("" if i is None else row[i] for i in index)])
            except UnicodeDecodeError as exc:
                raise ReadError("decode_error", f"{name}: bytes inválidos para {spec['encoding']} "
                                                f"perto do registro {record + 1} ({exc.reason})")
            except csv.Error as exc:
                raise ReadError("parse_error", f"{name}: CSV ilegível no registro {record + 1} ({exc})")
            result.members.append({"name": name, "records": record})
    return result


# --- evaluation --------------------------------------------------------------------------------

def _ident(name: str) -> str:
    return templates.ident(name)


evaluated_source = templates.evaluated_source


def evaluate(rule: dict, reads: dict[str, Read]) -> dict:
    con = duckdb.connect(":memory:")
    try:
        for source_id, read in reads.items():
            cols = ", ".join(_ident(c) for c in ["__member", "__record", *read.columns])
            con.execute(f"CREATE TABLE {_ident('src_' + source_id)} AS SELECT {cols} "
                        f"FROM read_csv(?, header = true, all_varchar = true, delim = ',', quote = '\"')",
                        [str(read.path)])
        con.execute("SET TimeZone = 'UTC'")              # "today" in a rule is the day of the run in UTC
        con.execute("SET enable_external_access = false")
        con.execute("SET lock_configuration = true")
        _, sql = templates.statement(rule["check"], rule["sources"])
        con.execute(sql)
        counts = dict.fromkeys(OUTCOMES, 0)
        counts.update(dict(con.execute("SELECT outcome, count(*) FROM outcome GROUP BY 1").fetchall()))
        records: dict[str, dict[str, list[int]]] = {}
        for outcome, member, numbers in con.execute(
                "SELECT outcome, __member, list(CAST(__record AS BIGINT) ORDER BY CAST(__record AS BIGINT)) "
                "FROM outcome WHERE outcome NOT IN ('match', 'out_of_scope') GROUP BY 1, 2 ORDER BY 1, 2").fetchall():
            records.setdefault(outcome, {})[member] = numbers
        by_member: dict[str, dict[str, int]] = {}
        for member, outcome, n in con.execute(
                "SELECT __member, outcome, count(*) FROM outcome GROUP BY 1, 2 ORDER BY 1, 2").fetchall():
            by_member.setdefault(member, {})[outcome] = n
        by_period: dict[str, dict[str, int]] = {}
        if "timeline" in rule["check"]:
            for period, outcome, n in con.execute(
                    "SELECT coalesce(__period, 'unknown'), outcome, count(*) FROM outcome GROUP BY 1, 2 ORDER BY 1, 2").fetchall():
                by_period.setdefault(period, {})[outcome] = n
    finally:
        con.close()
    total = reads[evaluated_source(rule["check"])].records
    if sum(counts.values()) != total:
        raise ReadError("count_mismatch", f"resultados somam {sum(counts.values())}, registros lidos {total}")
    return {"counts": counts, "total": total, "records": records, "by_member": by_member, "by_period": by_period,
            "members": reads[evaluated_source(rule["check"])].members}


# --- a run -------------------------------------------------------------------------------------

PORTAL_FILE = Path(__file__).resolve().parent.parent / "portal.json"


def portal_config() -> dict:
    """portal.json: the portal of this instance (url, name, title) and its repository."""
    try:
        return json.loads(PORTAL_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def primary_portal() -> str | None:
    """The portal of this instance; resources of other portals are secondary."""
    url = portal_config().get("portal_url")
    return url.rstrip("/") if url else None


def run(paths, work: Path, keep_downloads: bool = False, log=print) -> dict:
    """Evaluates every rule under `paths`. Returns the run: rules, fetched sources, timings."""
    started = now()
    primary = primary_portal()
    downloads, reads_dir = work / "downloads", work / "reads"
    downloads.mkdir(parents=True, exist_ok=True)
    reads_dir.mkdir(parents=True, exist_ok=True)

    files, problems = validate.rule_files(paths)
    rules: list[dict] = []
    for path in files:
        loaded, findings = validate.validate_file(path)
        errors = [f for f in findings if f.level == validate.ERROR]
        if problem := validate.name_problem(path):
            errors.append(problem)
        entry = {"id": validate.rule_id(path), "file": path, "data": loaded.data if loaded else None,
                 "rule_text": path.read_bytes()}
        if errors:
            entry.update(status=NOT_EVALUATED, reason_code="invalid_rule",
                         reason="; ".join(f.render() for f in errors)[:1000])
        rules.append(entry)
    names = [validate.name_key(r["id"]) for r in rules]
    for entry in rules:
        if names.count(validate.name_key(entry["id"])) > 1 and "status" not in entry:
            entry.update(status=NOT_EVALUATED, reason_code="invalid_rule",
                         reason=f'há mais de uma regra chamada "{entry["id"]}" em rules/')
    log(f"{len(rules)} regra(s); {sum('status' not in r for r in rules)} válida(s)")

    # fetch every resource once
    t_download = time.monotonic()
    fetched: dict[ResourceKey, Fetched] = {}
    for entry in rules:
        if "status" in entry:
            continue
        for source in entry["data"]["sources"].values():
            key = ResourceKey.of(source)
            if key not in fetched:
                log(f"baixando {key.label}")
                fetched[key] = fetch(key, downloads)
                f = fetched[key]
                f.role = "primary" if key.portal == primary else "secondary"
                log(f"  {f.status}" + (f" — {f.reason}" if f.reason else
                                       f" — {f.download['bytes'] / 1e6:.1f} MB, sha256 {f.download['sha256'][:12]}…"))
            fetched[key].used_by.append(entry["id"])

    download_s = time.monotonic() - t_download

    # read each resource once (union of the columns its rules declare), then evaluate each rule
    t_processing = time.monotonic()
    shared: dict[tuple, dict] = {}
    for entry in rules:
        if "status" in entry:
            continue
        for source in entry["data"]["sources"].values():
            key = (ResourceKey.of(source), json.dumps(source.get("archive"), sort_keys=True),
                   json.dumps(source["file"], sort_keys=True))
            item = shared.setdefault(key, {"columns": [], "source": source, "read": None, "error": None})
            item["columns"] += [c for c in source["columns"] if c not in item["columns"]]

    def shared_read(source: dict) -> Read:
        key = (ResourceKey.of(source), json.dumps(source.get("archive"), sort_keys=True),
               json.dumps(source["file"], sort_keys=True))
        item = shared[key]
        if item["read"] is None and item["error"] is None:
            try:
                item["read"] = read_source(fetched[key[0]], item["source"],
                                           reads_dir / f"shared-{list(shared).index(key)}.csv",
                                           columns=item["columns"])
            except ReadError as exc:
                item["error"] = exc
        if item["error"]:
            raise item["error"]
        return item["read"].view(list(source["columns"]))

    for entry in rules:
        if "status" in entry:
            continue
        rule = entry["data"]
        entry["sources"] = {}
        failed = None
        for source_id, source in rule["sources"].items():
            f = fetched[ResourceKey.of(source)]
            entry["sources"][source_id] = {"resource": f.key.label, "fetch_status": f.status,
                                           "sha256": f.download.get("sha256"), "url": f.resource.get("url"),
                                           "file": (published_file(f) if len(f.parts) <= 1 and f.resource.get("url")
                                                    else None),
                                           "files": [p["name"] for p in f.parts] if len(f.parts) > 1 else None,
                                           "archive_members": (source.get("archive") or {}).get("members")}
            if f.status != OK and failed is None:
                failed = (f"source_{f.status}", f'fonte "{source_id}" ({f.key.label}): {f.reason}')
        if failed:
            entry.update(status=NOT_EVALUATED, reason_code=failed[0], reason=failed[1])
            log(f"{entry['id']}: não avaliada — {failed[1]}")
            continue
        reads: dict[str, Read] = {}
        try:
            for source_id, source in rule["sources"].items():
                read = shared_read(source)
                reads[source_id] = read
                entry["sources"][source_id].update(records=read.records, members=read.members)
            result = evaluate(rule, reads)
        except ReadError as exc:
            entry.update(status=NOT_EVALUATED, reason_code=exc.code, reason=exc.message)
            log(f"{entry['id']}: não avaliada — {exc.message}")
            continue
        entry.update(status=EVALUATED, evaluated_at=now(), **result)
        log(f"{entry['id']}: {result['total']} registros; " +
            ", ".join(f"{k} {v}" for k, v in result["counts"].items()))

    processing_s = time.monotonic() - t_processing
    for item in shared.values():
        if item["read"]:
            item["read"].path.unlink(missing_ok=True)
    if not keep_downloads:
        for f in fetched.values():
            for p in f.parts:
                p["path"].unlink(missing_ok=True)
            if f.path:
                f.path.unlink(missing_ok=True)
    timings = {"download_s": round(download_s, 2), "processing_s": round(processing_s, 2),
               "bytes_processed": sum(f.download.get("bytes") or 0 for f in fetched.values() if f.status == OK)}
    return {"started_at": started, "finished_at": now(), "rules": rules, "primary_portal": primary, "timings": timings,
            "portal": portal_config(),
            "fetched": list(fetched.values()), "problems": problems}
