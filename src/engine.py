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
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

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

    @property
    def records(self) -> int:
        return sum(m["records"] for m in self.members)


# --- reading -----------------------------------------------------------------------------------

def _members(fetched: Fetched, source: dict):
    """(member name, binary stream) for every file to read, in name order."""
    archive = source.get("archive")
    if archive is None:
        with open(fetched.path, "rb") as fh:
            yield fetched.key.name, fh
        return
    try:
        zf = zipfile.ZipFile(fetched.path)
    except zipfile.BadZipFile:
        raise ReadError("archive_invalid", "o recurso não é um zip válido")
    with zf:
        names = sorted(n for n in zf.namelist() if not n.endswith("/")
                       and fnmatch.fnmatchcase(n.rsplit("/", 1)[-1], archive["members"]))
        if not names:
            raise ReadError("member_missing", f'nenhum arquivo do zip casa com "{archive["members"]}"; '
                                              f"conteúdo: {sorted(zf.namelist())[:20]}")
        for name in names:
            with zf.open(name) as fh:
                yield name, fh


def read_source(fetched: Fetched, source: dict, out: Path) -> Read:
    spec, wanted = source["file"], list(source["columns"])
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
                    raise ReadError("column_missing", f"{name}: colunas ausentes {missing}; cabeçalho: {header[:40]}")
                index = [header.index(c) for c in wanted]
                width = len(header)
                for row in reader:
                    record += 1
                    if len(row) < width:
                        row = row + [""] * (width - len(row))
                    writer.writerow([name, record, *(row[i] for i in index)])
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
            con.execute(f"CREATE TABLE {_ident('src_' + source_id)} AS "
                        f"SELECT * FROM read_csv(?, header = true, all_varchar = true, delim = ',', quote = '\"')",
                        [str(read.path)])
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
    finally:
        con.close()
    total = reads[evaluated_source(rule["check"])].records
    if sum(counts.values()) != total:
        raise ReadError("count_mismatch", f"resultados somam {sum(counts.values())}, registros lidos {total}")
    return {"counts": counts, "total": total, "records": records}


# --- a run -------------------------------------------------------------------------------------

PORTAL_FILE = Path(__file__).resolve().parent.parent / "portal.json"


def primary_portal() -> str | None:
    """The portal of this instance (portal.json); resources of other portals are secondary."""
    try:
        return json.loads(PORTAL_FILE.read_text(encoding="utf-8"))["portal_url"].rstrip("/")
    except (OSError, ValueError, KeyError):
        return None


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

    # read and evaluate each rule
    for entry in rules:
        if "status" in entry:
            continue
        rule = entry["data"]
        entry["sources"] = {}
        failed = None
        for source_id, source in rule["sources"].items():
            f = fetched[ResourceKey.of(source)]
            entry["sources"][source_id] = {"resource": f.key.label, "fetch_status": f.status,
                                           "sha256": f.download.get("sha256")}
            if f.status != OK and failed is None:
                failed = (f"source_{f.status}", f'fonte "{source_id}" ({f.key.label}): {f.reason}')
        if failed:
            entry.update(status=NOT_EVALUATED, reason_code=failed[0], reason=failed[1])
            log(f"{entry['id']}: não avaliada — {failed[1]}")
            continue
        reads: dict[str, Read] = {}
        try:
            for source_id, source in rule["sources"].items():
                f = fetched[ResourceKey.of(source)]
                read = read_source(f, source, reads_dir / f"{entry['id']}.{source_id}.csv")
                reads[source_id] = read
                entry["sources"][source_id].update(records=read.records, members=read.members)
            result = evaluate(rule, reads)
        except ReadError as exc:
            entry.update(status=NOT_EVALUATED, reason_code=exc.code, reason=exc.message)
            log(f"{entry['id']}: não avaliada — {exc.message}")
            continue
        finally:
            for read in reads.values():
                read.path.unlink(missing_ok=True)
        entry.update(status=EVALUATED, evaluated_at=now(), **result)
        log(f"{entry['id']}: {result['total']} registros; " +
            ", ".join(f"{k} {v}" for k, v in result["counts"].items()))

    if not keep_downloads:
        for f in fetched.values():
            if f.path:
                f.path.unlink(missing_ok=True)
    return {"started_at": started, "finished_at": now(), "rules": rules, "primary_portal": primary,
            "fetched": list(fetched.values()), "problems": problems}
