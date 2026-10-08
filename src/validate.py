"""Validation of rule files: schema and cross references.

The JSON Schema fixes the structure and the allowed tokens. What a schema cannot say is checked
here: every `source.column` the check names must be declared in `sources`, and declared sources and
columns should be used. Messages are in Portuguese, the initial interface language; codes are
stable English identifiers.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from jsonschema import Draft202012Validator

from src.loader import LoadedRule, RuleLoadError, load_rule

SCHEMA_FILE = Path(__file__).resolve().parent.parent / "schema" / "rule-v1.schema.json"

ERROR, WARNING = "error", "warning"


@dataclass
class Finding:
    level: str          # error | warning
    file: str
    line: int | None
    path: str           # dotted path inside the rule, "" for the file itself
    code: str
    message: str

    def render(self) -> str:
        where = f"{self.file}:{self.line}" if self.line else self.file
        label = "erro" if self.level == ERROR else "aviso"
        inside = f" {self.path}:" if self.path else ""
        return f"{where}: {label} [{self.code}]{inside} {self.message}"


def load_schema() -> dict:
    return json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))


_VALIDATOR = None


def _validator() -> Draft202012Validator:
    global _VALIDATOR
    if _VALIDATOR is None:
        schema = load_schema()
        Draft202012Validator.check_schema(schema)
        _VALIDATOR = Draft202012Validator(schema)
    return _VALIDATOR


def dotted(path) -> str:
    out = ""
    for step in path:
        out += f"[{step}]" if isinstance(step, int) else (f".{step}" if out else str(step))
    return out


# --- schema messages ---------------------------------------------------------------

_TYPE_PT = {"string": "texto", "integer": "número inteiro", "number": "número", "boolean": "true/false",
            "object": "mapa de campos", "array": "lista", "null": "null"}


def _kind(value) -> str:
    if isinstance(value, (dt.date, dt.datetime)):
        return "data sem aspas"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true/false"
    if isinstance(value, int):
        return "número inteiro"
    if isinstance(value, float):
        return "número"
    if isinstance(value, str):
        return "texto"
    if isinstance(value, list):
        return "lista"
    if isinstance(value, dict):
        return "mapa de campos"
    return type(value).__name__


def _translate(error) -> tuple[list, str, str]:
    """(path, code, Portuguese message) for one jsonschema error."""
    path = list(error.absolute_path)
    v, value, inst = error.validator, error.validator_value, error.instance
    if v in ("oneOf", "anyOf") and error.context:
        useful = [e for e in error.context if not (e.validator == "type" and e.validator_value == "null")]
        if useful:
            sub = sorted(useful, key=lambda e: len(e.absolute_path), reverse=True)[0]
            _, code, message = _translate(sub)
            if sub.validator == "type":
                return path, code, message.replace("esperado ", "esperado null ou ", 1)
            return path, code, f"deve ser null ou atender ao formato: {message}"
    if v == "required":
        match = re.search(r"'([^']+)' is a required property", error.message)
        name = match.group(1) if match else "?"
        return path, "schema.required", f'falta o campo obrigatório "{name}"'
    if v == "additionalProperties":
        allowed = set(error.schema.get("properties", {}))
        extra = sorted(k for k in inst if k not in allowed) if isinstance(inst, dict) else []
        if extra:
            return path + [extra[0]], "schema.unknown_field", (
                f'campo não previsto no formato 1.0: "{extra[0]}"' + (f" (e mais {len(extra) - 1})" if len(extra) > 1 else ""))
        return path, "schema.unknown_field", "campo não previsto no formato 1.0"
    if v == "enum":
        options = ", ".join(json.dumps(o, ensure_ascii=False) for o in value)
        return path, "schema.enum", f"valor {json.dumps(inst, ensure_ascii=False, default=str)} não permitido; use: {options}"
    if v == "const":
        return path, "schema.const", f"valor deve ser {json.dumps(value, ensure_ascii=False)}"
    if v == "type":
        expected = value if isinstance(value, str) else value[0]
        hint = "; datas e versões ficam entre aspas" if isinstance(inst, (dt.date, dt.datetime)) else ""
        return path, "schema.type", f"esperado {_TYPE_PT.get(expected, expected)}, encontrado {_kind(inst)}{hint}"
    if v == "pattern":
        return path, "schema.pattern", f"{json.dumps(inst, ensure_ascii=False)} não segue o formato exigido"
    if v in ("minItems", "minProperties"):
        return path, "schema.too_few", "precisa ter pelo menos um item"
    if v == "minLength":
        return path, "schema.empty_text", "texto vazio"
    if v == "maxLength":
        return path, "schema.too_long", f"texto com mais de {value} caracteres"
    if v in ("minimum", "maximum"):
        return path, "schema.range", f"valor {inst} fora do intervalo permitido"
    if v == "uniqueItems":
        return path, "schema.duplicate_items", "itens repetidos na lista"
    return path, f"schema.{v}", error.message


def schema_findings(rule: LoadedRule) -> list[Finding]:
    found = []
    for error in _validator().iter_errors(rule.data):
        path, code, message = _translate(error)
        found.append(Finding(ERROR, str(rule.path), rule.line_of(path), dotted(path), code, message))
    found.sort(key=lambda f: (f.line or 0, f.path, f.code))
    unique, seen = [], set()
    for f in found:
        key = (f.path, f.code, f.message)
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


# --- cross references --------------------------------------------------------------

def _split(ref: str) -> tuple[str, str]:
    source, _, column = ref.partition(".")
    return source, column


def _used_lookup_equals(check: dict) -> list[tuple[str, list]]:
    """(source.column, path inside the rule) for every column the template reads."""
    return [(check[part][end], ["check", part, end]) for part in ("key", "compare") for end in ("from", "to")]


USED_COLUMNS = {"lookup-equals": _used_lookup_equals}


def cross_findings(rule: LoadedRule) -> list[Finding]:
    data, found = rule.data, []
    sources, check = data["sources"], data["check"]

    def add(level, path, code, message):
        found.append(Finding(level, str(rule.path), rule.line_of(path), dotted(path), code, message))

    used = set()
    for ref, path in USED_COLUMNS[check["template"]](check):
        source, column = _split(ref)
        if source not in sources:
            add(ERROR, path, "ref.unknown_source", f'fonte "{source}" não existe em sources')
        elif column not in sources[source]["columns"]:
            add(ERROR, path, "ref.undeclared_column", f'coluna "{column}" não declarada na fonte "{source}"')
        else:
            used.add((source, column))

    if check["template"] == "lookup-equals":
        sides = {end: {_split(check[part][end])[0] for part in ("key", "compare")} for end in ("from", "to")}
        for end, names in sides.items():
            if len(names) > 1:
                add(ERROR, ["check", "compare", end], "check.mixed_sources",
                    f'key.{end} e compare.{end} precisam ser da mesma fonte')

    for source_id, source in sources.items():
        if not any(s == source_id for s, _ in used):
            add(WARNING, ["sources", source_id], "ref.unused_source", "fonte declarada e não usada pelo check")
            continue
        for column in source["columns"]:
            if (source_id, column) not in used:
                add(WARNING, ["sources", source_id, "columns", column], "ref.unused_column",
                    "coluna declarada e não usada; declare só o que a verificação lê")
    return found


# --- entry points ------------------------------------------------------------------

def validate_file(path: Path) -> tuple[LoadedRule | None, list[Finding]]:
    try:
        rule = load_rule(path)
    except RuleLoadError as exc:
        return None, [Finding(ERROR, str(path), exc.line, "", exc.code, exc.message)]
    findings = schema_findings(rule)
    if not findings:
        findings = cross_findings(rule)
    return rule, findings


def rule_files(paths) -> tuple[list[Path], list[Finding]]:
    files, found = [], []
    for p in map(Path, paths):
        if p.is_dir():
            files += sorted(p.rglob("*.yaml"))
            for wrong in sorted(p.rglob("*.yml")):
                found.append(Finding(ERROR, str(wrong), None, "", "file.extension", "use a extensão .yaml"))
        elif p.exists():
            files.append(p)
        else:
            found.append(Finding(ERROR, str(p), None, "", "file.missing", "arquivo ou pasta não encontrado"))
    return files, found


def validate_paths(paths, check_names: bool = True) -> list[Finding]:
    files, findings = rule_files(paths)
    seen: dict[str, Path] = {}
    for path in files:
        rule, found = validate_file(path)
        findings += found
        if rule is None or not isinstance(rule.data.get("id"), str):
            continue
        rule_id = rule.data["id"]
        if rule_id in seen:
            findings.append(Finding(ERROR, str(path), rule.line_of(["id"]), "id", "id.duplicate",
                                    f'id "{rule_id}" já usado em {seen[rule_id]}'))
        else:
            seen[rule_id] = path
        if check_names and path.stem != rule_id:
            findings.append(Finding(ERROR, str(path), rule.line_of(["id"]), "id", "id.file_name",
                                    f'o arquivo deve se chamar "{rule_id}.yaml"'))
    return findings


def as_json(findings: list[Finding]) -> str:
    return json.dumps([asdict(f) for f in findings], ensure_ascii=False, indent=2)
