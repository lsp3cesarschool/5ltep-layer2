"""Validation of rule files: schema, cross references and regular-expression subset.

The JSON Schema fixes the structure and the allowed tokens. What a schema cannot say is checked
here: every source and column a parameter, identity or field meaning names must be declared in the
same application; an enabled application needs prepared references; `pattern` must stay inside the
subset of I-Regexp (RFC 9485) that Python and DuckDB evaluate alike. Messages are in Portuguese,
the initial interface language; codes are stable English identifiers.
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
        if path[-2:] == ["mapping_review", "status"]:
            return path, "schema.enabled_needs_review", 'aplicação "enabled" exige revisão do mapeamento "confirmed"'
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


# --- I-Regexp subset ---------------------------------------------------------------

_SINGLE_CHAR_ESCAPES = set("\\.-^?*+{}[]|()nrt")
_BOUND = 1000


def pattern_problem(pattern: str) -> str | None:
    """None if `pattern` is inside the accepted subset of I-Regexp, else the reason."""
    i, in_class, atom, quantified = 0, False, False, False
    while i < len(pattern):
        c = pattern[i]
        if c == "\\":
            if i + 1 >= len(pattern):
                return "termina com \\ sem caractere escapado"
            n = pattern[i + 1]
            if n in "pP":
                return "\\p{...} ainda não é aceito; use classes explícitas"
            if n not in _SINGLE_CHAR_ESCAPES:
                return f"escape \\{n} fora do subconjunto; use classes como [0-9]"
            i, atom, quantified = i + 2, True, False
            continue
        if in_class:
            if c == "]":
                in_class, atom, quantified = False, True, False
            elif c == "[":
                return "[ dentro de classe precisa de escape"
            i += 1
            continue
        if c == "[":
            in_class, i = True, i + 1
            if pattern[i:i + 1] == "^":
                i += 1
            if pattern[i:i + 1] == "]":
                return "classe vazia ou ] sem escape"
            continue
        if c in "^$":
            return "não use ^ ou $: o padrão já precisa casar com o valor inteiro"
        if c == "(":
            if pattern[i + 1:i + 2] == "?":
                return "grupos especiais (?...) não são aceitos"
            i, atom, quantified = i + 1, False, False
            continue
        if c == ")":
            i, atom, quantified = i + 1, True, False
            continue
        if c == "|":
            i, atom, quantified = i + 1, False, False
            continue
        if c in "*+?{":
            length = 1
            if c == "{":
                m = re.match(r"\{(\d+)(,(\d*))?\}", pattern[i:])
                if not m:
                    return "{ literal precisa de escape \\{"
                low, high = int(m.group(1)), m.group(3)
                if low > _BOUND or (high and (int(high) > _BOUND or int(high) < low)):
                    return f"limites do quantificador inválidos (máximo {_BOUND})"
                length = m.end()
            if quantified:
                return "quantificador preguiçoso, possessivo ou repetido não é aceito"
            if not atom:
                return "quantificador sem elemento antes"
            i, atom, quantified = i + length, False, True
            continue
        if c in "}]":
            return f"{c} literal precisa de escape \\{c}"
        i, atom, quantified = i + 1, True, False
    if in_class:
        return "classe [ sem ]"
    try:
        re.compile(pattern)
    except re.error as exc:
        return f"expressão inválida: {exc}"
    return None


# --- cross references --------------------------------------------------------------

def _used_columns_hierarchical(params: dict) -> list[tuple[str, str, list]]:
    """(source, column, path inside parameters) for every column the template reads."""
    used = []
    for arg in ("child", "parent"):
        ref = params.get(arg) or {}
        used.append((ref.get("source"), ref.get("column"), ["parameters", arg, "column"]))
    lookup = params.get("parent_lookup")
    if lookup:
        for arg in ("key_column", "value_column"):
            used.append((lookup.get("source"), lookup.get(arg), ["parameters", "parent_lookup", arg]))
    return used


USED_COLUMNS = {"hierarchical-code": _used_columns_hierarchical}


def cross_findings(rule: LoadedRule) -> list[Finding]:
    data, found = rule.data, []

    def add(level, path, code, message):
        found.append(Finding(level, str(rule.path), rule.line_of(path), dotted(path), code, message))

    template = data["execution"]["template"]
    applications = data["execution"]["applications"]
    for app_id, app in applications.items():
        base = ["execution", "applications", app_id]
        sources = app["sources"]

        def declared(source_id, column, source_path, column_path):
            if source_id not in sources:
                add(ERROR, source_path, "ref.unknown_source", f'fonte "{source_id}" não existe na aplicação "{app_id}"')
                return False
            if column not in sources[source_id]["columns"]:
                add(ERROR, column_path, "ref.undeclared_column", f'coluna "{column}" não declarada na fonte "{source_id}"')
                return False
            return True

        used = set()
        for source_id, column, rel in USED_COLUMNS[template](app["parameters"]):
            if declared(source_id, column, base + rel[:-1] + ["source"], base + rel):
                used.add((source_id, column))
        lookup = app["parameters"].get("parent_lookup")
        if lookup and lookup["source"] in sources and sources[lookup["source"]]["kind"] != "reference":
            add(WARNING, base + ["parameters", "parent_lookup", "source"], "ref.lookup_not_reference",
                "a consulta auxiliar costuma usar uma referência versionada (kind: reference)")

        identity = app["evaluation"]["identity"]
        for i, column in enumerate(identity["columns"]):
            if declared(identity["source"], column, base + ["evaluation", "identity", "source"],
                        base + ["evaluation", "identity", "columns", i]):
                used.add((identity["source"], column))

        for source_id, source in sources.items():
            for column, spec in source["columns"].items():
                cpath = base + ["sources", source_id, "columns", column]
                if (source_id, column) not in used:
                    add(WARNING, cpath, "ref.unused_column",
                        "coluna declarada e não usada; declare só o que a verificação lê")
                if "pattern" in spec:
                    problem = pattern_problem(spec["pattern"])
                    if problem:
                        add(ERROR, cpath + ["pattern"], "pattern.subset", problem)

        if app["status"] == "enabled":
            for source_id, source in sources.items():
                if source["kind"] != "reference":
                    continue
                for key in ("version", "sha256", "license", "coverage"):
                    if source.get(key) is None:
                        add(ERROR, base + ["sources", source_id, key], "enabled.reference_not_ready",
                            f'aplicação "enabled" exige "{key}" preenchido na referência')

    for i, meaning in enumerate(data["description"].get("field_meanings", [])):
        path = ["description", "field_meanings", i]
        app = applications.get(meaning["application"])
        if app is None:
            add(ERROR, path + ["application"], "ref.unknown_application",
                f'aplicação "{meaning["application"]}" não existe em execution.applications')
            continue
        source = app["sources"].get(meaning["source"])
        if source is None:
            add(ERROR, path + ["source"], "ref.unknown_source",
                f'fonte "{meaning["source"]}" não existe na aplicação "{meaning["application"]}"')
        elif meaning["column"] not in source["columns"]:
            add(ERROR, path + ["column"], "ref.undeclared_column",
                f'coluna "{meaning["column"]}" não declarada na fonte "{meaning["source"]}"')
    unique, seen = [], set()
    for f in found:
        if (f.path, f.code, f.message) not in seen:
            seen.add((f.path, f.code, f.message))
            unique.append(f)
    return unique


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
