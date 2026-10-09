"""Templates: the fixed SQL behind each `check.template`.

A rule never carries SQL. It names columns (`source.column`), fixed values and a few options; each
template here turns them into one SQL statement that gives every record of the evaluated source
exactly one outcome. Column names reach DuckDB only as quoted identifiers of tables the engine
built, and fixed values only as SQL literals produced by `_literal`.

Typed columns: a column declared with `type: date|datetime` is parsed with its `format` (strptime
codes, as in DuckDB and Python); `type: number` is parsed with its `decimal` separator ("," means
"." is a thousands separator). A value that is present but cannot be parsed is `invalid_value`; an
empty value is `missing_value`. Neither is ever counted as consistent.

`where` (any template): conditions on columns of the evaluated source, compared as trimmed text.
Records outside them are `out_of_scope`: counted, so the outcomes still add up to the records read,
but not a signal.
"""

from __future__ import annotations

import math

OUTCOMES = ("match", "mismatch", "key_not_found", "missing_value", "invalid_value", "ambiguous_key", "out_of_scope")
SIGNALS = ("mismatch", "key_not_found", "missing_value", "invalid_value", "ambiguous_key")


def ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _literal(value) -> str:
    if isinstance(value, bool) or value is None:
        raise ValueError("valor fixo inválido")
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("valor fixo inválido")
        return repr(value)
    return "'" + str(value).replace("'", "''") + "'"


def split(ref: str) -> tuple[str, str]:
    source, _, column = ref.partition(".")
    return source, column


class Columns:
    """SQL expressions for `source.column` references, aware of each column's declared type."""

    def __init__(self, sources: dict, aliases: dict[str, str]):
        self.sources, self.aliases = sources, aliases       # aliases: source id -> table alias in the FROM

    def spec(self, ref: str) -> dict:
        source, column = split(ref)
        spec = self.sources[source]["columns"][column]
        return spec if isinstance(spec, dict) else {"meaning": spec, "type": "text"}

    def raw(self, ref: str) -> str:
        source, column = split(ref)
        return f"trim({self.aliases[source]}.{ident(column)})"

    def empty(self, ref: str) -> str:
        return f"coalesce({self.raw(ref)}, '') = ''"

    def typed(self, ref: str, as_date: bool = False) -> str:
        spec, raw = self.spec(ref), self.raw(ref)
        kind = spec.get("type", "text")
        if kind in ("date", "datetime"):
            formats = spec["format"] if isinstance(spec["format"], list) else [spec["format"]]
            value = f"try_strptime({raw}, [{', '.join(_literal(f) for f in formats)}])"
            return f"CAST({value} AS DATE)" if (as_date or kind == "date") else value
        if kind == "number":
            if spec.get("decimal", ".") == ",":
                raw = f"replace(replace({raw}, '.', ''), ',', '.')"
            return f"TRY_CAST({raw} AS DOUBLE)"
        return raw

    def invalid(self, ref: str, as_date: bool = False) -> str:
        return f"(NOT {self.empty(ref)} AND {self.typed(ref, as_date)} IS NULL)"


COMPARISONS = {"at_least": ">=", "below": "<", "above": ">", "at_most": "<=",
               "on_or_after": ">=", "before": "<", "after": ">", "on_or_before": "<="}


def _typed_literal(value, spec: dict) -> str:
    kind = spec.get("type", "text")
    if kind in ("date", "datetime"):
        if str(value) == "today":          # the day of the run (UTC)
            return "CAST(current_date AS DATE)" if kind == "date" else "CAST(current_date AS TIMESTAMP)"
        return f"CAST({_literal(str(value))} AS {'DATE' if kind == 'date' else 'TIMESTAMP'})"
    if kind == "number":
        return _literal(float(value))
    return _literal(str(value))


def condition_sql(c: dict, cols: Columns) -> str:
    """One condition: on a column (equals, not_equals, in, not_in, empty, at_least, below,
    on_or_after, before) or a group (all / any). Columns declared as numbers or dates are compared
    as numbers or dates; others as trimmed text. A value that cannot be read never satisfies a
    comparison."""
    if "all" in c or "any" in c:
        parts = [condition_sql(x, cols) for x in c.get("all") or c.get("any")]
        return "(" + (" AND " if "all" in c else " OR ").join(parts) + ")"
    ref, spec = c["column"], cols.spec(c["column"])
    typed = spec.get("type", "text") != "text"
    value = cols.typed(ref) if typed else f"coalesce({cols.raw(ref)}, '')"
    lit = (lambda v: _typed_literal(v, spec)) if typed else (lambda v: _literal(str(v)))
    if "empty" in c:
        return f"({cols.empty(ref)})" if c["empty"] else f"(NOT {cols.empty(ref)})"
    if "equals" in c:
        return f"coalesce({value} = {lit(c['equals'])}, FALSE)"
    if "not_equals" in c:
        return f"coalesce({value} <> {lit(c['not_equals'])}, FALSE)"
    if "in" in c or "not_in" in c:
        values = ", ".join(lit(v) for v in (c.get("in") or c.get("not_in")))
        return f"coalesce({value} {'IN' if 'in' in c else 'NOT IN'} ({values}), FALSE)"
    for op, sql in COMPARISONS.items():
        if op in c:
            return f"coalesce({value} {sql} {lit(c[op])}, FALSE)"
    raise ValueError(f"condição sem operador: {c}")


def condition_refs(c: dict) -> list[str]:
    if "all" in c or "any" in c:
        return [r for x in (c.get("all") or c.get("any")) for r in condition_refs(x)]
    return [c["column"]]


def where_sql(conditions: list[dict], cols: Columns) -> str:
    return " AND ".join(condition_sql(c, cols) for c in conditions) if conditions else "TRUE"


# --- templates: each returns (evaluated source, FROM clause, CASE expression) ----------------------

NORMALIZE = {
    "lower": "lower({x})",
    # genus and epithet: "Manilkara huberi (Ducke) A.Chev." -> "manilkara huberi"
    "binomial": "lower(array_to_string(list_slice(string_split(regexp_replace({x}, '\\s+', ' ', 'g'), ' '), 1, 2), ' '))",
    # text before the first parenthesis: "glifosato (glicina substituída) (480 g/L)" -> "glifosato"
    "before_parenthesis": "lower(trim(split_part({x}, '(', 1)))",
}


def _key(ref: str, cols: Columns, normalize: str | None = None) -> str:
    """A key compared as a number when its column is declared `type: number` (so 1234567 and
    1234567.0000000000 match), else as trimmed text, normalized the same way on both sides."""
    if cols.spec(ref).get("type") == "number":
        return cols.typed(ref)
    return NORMALIZE[normalize].format(x=cols.raw(ref)) if normalize else cols.raw(ref)


def _lookup_key(key: dict, cols: Columns) -> str:
    """The key of the lookup source: one column, or several joined by `to_join`."""
    to = key["to"] if isinstance(key["to"], list) else [key["to"]]
    if len(to) == 1:
        return _key(to[0], cols, key.get("normalize"))
    sep = _literal(key.get("to_join", "-"))
    return " || ".join(f"coalesce({cols.raw(r)}, '')" if n == 0 else f"{sep} || coalesce({cols.raw(r)}, '')"
                       for n, r in enumerate(to))


def _to_source(key: dict) -> str:
    return split(key["to"][0] if isinstance(key["to"], list) else key["to"])[0]


def lookup_equals(check: dict, sources: dict):
    f_src, t_src = split(check["key"]["from"])[0], _to_source(check["key"])
    cols = Columns(sources, {f_src: "f", t_src: "t"})
    t_val = cols.raw(check["compare"]["to"])
    lookup = (f"(SELECT {_lookup_key(check['key'], cols)} AS k, min({t_val}) AS v, count(DISTINCT {t_val}) AS n "
              f"FROM {ident('src_' + t_src)} AS t GROUP BY 1 HAVING k IS NOT NULL AND CAST(k AS VARCHAR) <> '')")
    key, val = check["key"]["from"], check["compare"]["from"]
    case = (f"CASE WHEN {cols.empty(key)} OR {cols.empty(val)} THEN 'missing_value' "
            f"WHEN {cols.invalid(key)} THEN 'invalid_value' "
            f"WHEN l.k IS NULL THEN 'key_not_found' WHEN l.n > 1 THEN 'ambiguous_key' "
            f"WHEN {cols.raw(val)} = l.v THEN 'match' ELSE 'mismatch' END")
    return f_src, f"{ident('src_' + f_src)} AS f LEFT JOIN {lookup} AS l ON {_key(key, cols, check['key'].get('normalize'))} = l.k", case, cols


def lookup_exists(check: dict, sources: dict):
    """The key of each record must exist in the lookup source. With `split`, the key field holds
    several keys (e.g. "123-A,456-B"); every one must exist. With `expect: absent` the lookup source
    is a list to watch: a key found in it is the signal."""
    f_src, t_src = split(check["key"]["from"])[0], _to_source(check["key"])
    cols = Columns(sources, {f_src: "f", t_src: "t"})
    lookup = (f"(SELECT DISTINCT {_lookup_key(check['key'], cols)} AS k FROM {ident('src_' + t_src)} AS t)")
    key = check["key"]["from"]
    f_tab = ident("src_" + f_src)
    absent = check.get("expect") == "absent"
    if "split" not in check["key"]:
        found = "WHEN l.k IS NULL THEN 'match' ELSE 'mismatch'" if absent else "WHEN l.k IS NULL THEN 'key_not_found' ELSE 'match'"
        case = (f"CASE WHEN {cols.empty(key)} THEN 'missing_value' WHEN {cols.invalid(key)} THEN 'invalid_value' "
                f"{found} END")
        return f_src, f"{f_tab} AS f LEFT JOIN {lookup} AS l ON {_key(key, cols, check['key'].get('normalize'))} = l.k", case, cols
    sep = _literal(check["key"]["split"])
    items = (f"(SELECT f.__member, f.__record, trim(unnest(string_split({cols.raw(key)}, {sep}))) AS item "
             f"FROM {f_tab} AS f)")
    found = (f"(SELECT i.__member, i.__record, count(*) AS n, bool_and(l.k IS NOT NULL) AS all_found "
             f"FROM {items} AS i LEFT JOIN {lookup} AS l ON i.item = l.k WHERE i.item <> '' GROUP BY 1, 2)")
    case = (f"CASE WHEN {cols.empty(key)} OR m.n IS NULL THEN 'missing_value' "
            f"WHEN NOT m.all_found THEN 'key_not_found' ELSE 'match' END")
    return f_src, (f"{f_tab} AS f LEFT JOIN {found} AS m ON f.__member = m.__member AND f.__record = m.__record"), case, cols


def temporal_order(check: dict, sources: dict):
    """Dates in `sequence` must not decrease; empty dates are skipped (at least two must be present).
    A date and a datetime are compared by day. `max_interval` caps first-to-last present dates.
    With `check_order: false` only the interval is checked, and records out of order are out of scope
    (another rule checks the order)."""
    seq = check["sequence"]
    src, _ = split(seq[0])
    cols = Columns(sources, {src: "f"})
    by_day = any(cols.spec(r).get("type") == "date" for r in seq)
    values = ", ".join(cols.typed(r, by_day) for r in seq)
    present = f"list_filter([{values}], x -> x IS NOT NULL)"
    invalid = " OR ".join(cols.invalid(r, by_day) for r in seq)
    over = "FALSE"
    if "max_interval" in check:
        limit = check["max_interval"]
        unit, amount = ("YEAR", limit["years"]) if "years" in limit else ("DAY", limit["days"])
        over = f"list_last({present}) > list_first({present}) + INTERVAL {int(amount)} {unit}"
    unordered = f"{present} <> list_sort({present})"
    if check.get("check_order", True):
        verdict = f"WHEN {unordered} OR {over} THEN 'mismatch'"
    else:
        verdict = f"WHEN {unordered} THEN 'out_of_scope' WHEN {over} THEN 'mismatch'"
    case = (f"CASE WHEN {invalid} THEN 'invalid_value' WHEN len({present}) < 2 THEN 'missing_value' "
            f"{verdict} ELSE 'match' END")
    return src, f"{ident('src_' + src)} AS f", case, cols


_OPS = {"<": "<", "<=": "<=", "=": "=", ">=": ">=", ">": ">"}


def _side(side, cols: Columns, empty_as_zero: bool):
    """(SQL value, refs used) of a field-comparison side: a column, a fixed number, or a sum/difference."""
    if isinstance(side, (int, float)) and not isinstance(side, bool):
        return _literal(side), []
    if isinstance(side, str):
        return cols.typed(side), [side]
    plus, minus = side.get("sum", []), side.get("minus", [])
    term = (lambda r: f"coalesce({cols.typed(r)}, 0)") if empty_as_zero else cols.typed
    expr = " + ".join(term(r) for r in plus) or "0"
    if minus:
        expr = f"({expr}) - ({' + '.join(term(r) for r in minus)})"
    if "times" in side:
        expr = f"({expr}) * {_literal(float(side['times']))}"
    return f"({expr})", plus + minus


def field_comparison(check: dict, sources: dict):
    first = check["left"] if isinstance(check["left"], str) else (check["left"].get("sum") or check["left"].get("minus"))[0]
    src, _ = split(first)
    cols = Columns(sources, {src: "f"})
    zero = bool(check.get("empty_as_zero", False))
    left, l_refs = _side(check["left"], cols, zero)
    right, r_refs = _side(check["right"], cols, zero)
    refs = l_refs + r_refs
    tol = _literal(float(check.get("tolerance", 0)))
    op = _OPS[check["op"]]
    if op == "=":
        ok = f"abs({left} - {right}) <= {tol}"
    elif op in ("<", "<="):
        ok = f"{left} {op} {right} + {tol}"
    else:
        ok = f"{left} {op} {right} - {tol}"
    invalid = " OR ".join(cols.invalid(r) for r in refs) or "FALSE"
    missing = "FALSE" if zero else (" OR ".join(cols.empty(r) for r in refs) or "FALSE")
    if zero:   # with empty_as_zero, a record with every referenced value empty has nothing to compare
        missing = " AND ".join(cols.empty(r) for r in refs)
    case = (f"CASE WHEN {invalid} THEN 'invalid_value' WHEN {missing} THEN 'missing_value' "
            f"WHEN {ok} THEN 'match' ELSE 'mismatch' END")
    return src, f"{ident('src_' + src)} AS f", case, cols


def flag_when(check: dict, sources: dict):
    """A record is a signal (`mismatch`) when any of the `any` conditions holds; else `match`.
    A typed value present but unreadable is `invalid_value`."""
    refs = [r for c in check["any"] for r in condition_refs(c)]
    src = split(refs[0])[0]
    cols = Columns(sources, {src: "f"})
    typed = [r for r in dict.fromkeys(refs) if cols.spec(r).get("type", "text") != "text"]
    invalid = " OR ".join(cols.invalid(r) for r in typed) or "FALSE"
    flagged = " OR ".join(condition_sql(c, cols) for c in check["any"])
    case = f"CASE WHEN {invalid} THEN 'invalid_value' WHEN {flagged} THEN 'mismatch' ELSE 'match' END"
    return src, f"{ident('src_' + src)} AS f", case, cols


TEMPLATES = {"lookup-equals": lookup_equals, "lookup-exists": lookup_exists,
             "temporal-order": temporal_order, "field-comparison": field_comparison, "flag-when": flag_when}


def evaluated_source(check: dict) -> str:
    template = check["template"]
    if template in ("lookup-equals", "lookup-exists"):
        return split(check["key"]["from"])[0]
    if template == "temporal-order":
        return split(check["sequence"][0])[0]
    if template == "flag-when":
        return split(condition_refs(check["any"][0])[0])[0]
    left = check["left"]
    return split(left if isinstance(left, str) else (left.get("sum") or left.get("minus"))[0])[0]


def used_refs(check: dict) -> list[tuple[str, list]]:
    """(source.column, path inside the rule) for every column the check reads, `where` included."""
    t = check["template"]
    out = []
    if t in ("lookup-equals", "lookup-exists"):
        parts = ("key", "compare") if t == "lookup-equals" else ("key",)
        for p in parts:
            for e in ("from", "to"):
                v = check[p][e]
                out += [(r, ["check", p, e, i]) for i, r in enumerate(v)] if isinstance(v, list) else [(v, ["check", p, e])]
    elif t == "temporal-order":
        out += [(r, ["check", "sequence", i]) for i, r in enumerate(check["sequence"])]
    elif t == "field-comparison":
        for side in ("left", "right"):
            v = check[side]
            if isinstance(v, str):
                out.append((v, ["check", side]))
            elif isinstance(v, dict):
                for k in ("sum", "minus"):
                    out += [(r, ["check", side, k, i]) for i, r in enumerate(v.get(k, []))]
    if t == "flag-when":
        out += [(r, ["check", "any", i]) for i, c in enumerate(check["any"]) for r in condition_refs(c)]
    out += [(r, ["check", "where", i]) for i, c in enumerate(check.get("where", [])) for r in condition_refs(c)]
    if "timeline" in check:
        out.append((check["timeline"], ["check", "timeline"]))
    return out


def statement(check: dict, sources: dict) -> tuple[str, str]:
    """(evaluated source, SQL creating table `outcome(__member, __record, outcome)`)."""
    src, frm, case, cols = TEMPLATES[check["template"]](check, sources)
    scope = where_sql(check.get("where", []), cols)
    period = (f"CAST(year({cols.typed(check['timeline'], True)}) AS VARCHAR)" if "timeline" in check else "NULL")
    sql = (f"CREATE TABLE outcome AS SELECT f.__member, f.__record, {period} AS __period, "
           f"CASE WHEN NOT ({scope}) THEN 'out_of_scope' ELSE {case} END AS outcome FROM {frm}")
    return src, sql
