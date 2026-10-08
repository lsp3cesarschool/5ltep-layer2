"""Layer 2 validation tests. Each case edits the example rule and checks the finding it must produce."""

import json
import re
from pathlib import Path

import pytest

import main
from src import validate

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "rules" / "territory" / "territory.municipality-state.yaml"
TEXT = EXAMPLE.read_text(encoding="utf-8")
RULE_ID = "territory.municipality-state"


def check(tmp_path, text, name=RULE_ID + ".yaml"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return validate.validate_paths([path])


def edit(old, new, text=TEXT, count=1):
    assert text.count(old) == count, old
    return text.replace(old, new)


def codes(findings, level=None):
    return [f.code for f in findings if level is None or f.level == level]


# --- the example ---------------------------------------------------------------------

def test_example_rule_is_valid():
    assert validate.validate_paths([ROOT / "rules"]) == []


def test_schema_is_a_valid_draft_2020_12_schema():
    validate.Draft202012Validator.check_schema(validate.load_schema())


def test_cli_exit_codes(tmp_path):
    assert main.main(["validate", str(ROOT / "rules")]) == 0
    bad = tmp_path / f"{RULE_ID}.yaml"
    bad.write_text(edit("status: example", "status: exemplo"), encoding="utf-8")
    assert main.main(["validate", str(bad)]) == 1


def test_cli_json_output(tmp_path, capsys):
    bad = tmp_path / f"{RULE_ID}.yaml"
    bad.write_text(edit("status: example", "status: exemplo"), encoding="utf-8")
    main.main(["validate", str(bad), "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert data[0]["code"] == "schema.enum" and data[0]["path"] == "status" and data[0]["line"] == 7


# --- safe YAML -----------------------------------------------------------------------

@pytest.mark.parametrize("old, new, code", [
    ("status: example\n", "status: example\nstatus: proposed\n", "yaml.duplicate_key"),
    ("origin: cross_reference", "origin: &o cross_reference", "yaml.anchor"),
    ("version: \"0.1.0\"", "version: !!str 0.1.0", "yaml.tag"),
    ("schema_version: \"1.0\"\n", "schema_version: \"1.0\"\nextra: {<<: {a: 1}}\n", "yaml.merge_key"),
])
def test_unsafe_yaml_is_refused(tmp_path, old, new, code):
    assert codes(check(tmp_path, edit(old, new))) == [code]


def test_alias_is_refused(tmp_path):
    text = edit("origin: cross_reference", "origin: &o cross_reference").replace("status: example", "status: *o")
    assert codes(check(tmp_path, text))[0] in ("yaml.anchor", "yaml.alias")


def test_version_directive_and_multiple_documents_are_refused(tmp_path):
    assert codes(check(tmp_path, "%YAML 1.1\n---\n" + TEXT)) == ["yaml.version_directive"]
    assert codes(check(tmp_path, TEXT + "---\na: 1\n")) == ["yaml.multiple_documents"]


def test_yaml_1_2_keeps_no_as_text_and_dates_must_be_quoted(tmp_path):
    text = edit('missing_values: [""]\n              pattern: \'[0-9]{7}\'',
                'missing_values: ["", NO]\n              pattern: \'[0-9]{7}\'')
    assert check(tmp_path, text) == []                      # NO stays the string "NO" (YAML 1.2)
    text = edit("        checked_at: null", "        checked_at: 2026-10-08")
    found = check(tmp_path, text)
    assert codes(found) == ["schema.type"]
    assert found[0].message == "esperado null ou texto, encontrado data sem aspas; datas e versões ficam entre aspas"


def test_not_utf8_is_refused(tmp_path):
    path = tmp_path / f"{RULE_ID}.yaml"
    path.write_bytes(TEXT.encode("utf-8") + b"# C\xf3digo em Latin-1\n")
    assert codes(validate.validate_paths([path])) == ["file.encoding"]


# --- schema --------------------------------------------------------------------------

def test_portuguese_token_is_refused_with_line(tmp_path):
    found = check(tmp_path, edit("status: example", "status: exemplo"))
    assert [(f.code, f.path, f.line) for f in found] == [("schema.enum", "status", 7)]
    assert '"example"' in found[0].message


def test_unknown_field_points_to_its_line(tmp_path):
    text = edit("  dimension: consistency\n", "  dimension: consistency\n  domain: GEO\n")
    found = check(tmp_path, text)
    assert codes(found) == ["schema.unknown_field"]
    assert found[0].path == "classification.domain" and "domain" in found[0].message
    assert TEXT.splitlines()[found[0].line - 2].strip() == "dimension: consistency"


def test_missing_policy_is_required(tmp_path):
    found = check(tmp_path, edit("        ambiguous_resource: inapplicable\n", ""))
    assert [(f.code, f.message) for f in found] == [("schema.required", 'falta o campo obrigatório "ambiguous_resource"')]


def test_template_without_contract_is_refused(tmp_path):
    assert "schema.enum" in codes(check(tmp_path, edit("template: hierarchical-code", "template: temporal-order")))


def test_hierarchical_code_parameters_are_closed(tmp_path):
    text = edit("        prefix_length: 2\n", "        prefix_length: 2\n        sql: \"select 1\"\n")
    found = check(tmp_path, text)
    assert codes(found) == ["schema.unknown_field"] and found[0].path.endswith("parameters.sql")


def test_enabled_application_needs_confirmed_review(tmp_path):
    found = check(tmp_path, edit("status: pending_mapping", "status: enabled"))
    assert codes(found) == ["schema.enabled_needs_review"]


def test_confirmed_review_needs_who_and_when(tmp_path):
    text = edit("        status: pending\n        evidence: >", "        status: confirmed\n        evidence: >")
    found = check(tmp_path, text)
    assert {f.path.rsplit(".", 1)[-1] for f in found} == {"reviewed_at", "reviewed_by"}


def test_enabled_application_needs_prepared_reference(tmp_path):
    text = edit("status: pending_mapping", "status: enabled")
    text = edit("        status: pending\n        evidence: >", "        status: confirmed\n        evidence: >", text)
    text = edit("        reviewed_at: null\n        reviewed_by: null",
                "        reviewed_at: \"2026-10-08\"\n        reviewed_by: \"Revisora\"", text)
    found = check(tmp_path, text)
    assert codes(found, "error") == ["enabled.reference_not_ready"] * 4


def test_checked_source_needs_who_and_when(tmp_path):
    found = check(tmp_path, edit("        status: pending\n        checked_at", "        status: checked\n        checked_at"))
    assert {f.path.rsplit(".", 1)[-1] for f in found} == {"checked_at", "checked_by"}


def test_knowledge_areas_accept_any_category(tmp_path):
    text = edit("  category: DC\n  knowledge_areas: [GEO]", "  category: TC\n  knowledge_areas: [LEG, GEO]")
    assert check(tmp_path, text) == []
    assert codes(check(tmp_path, edit("knowledge_areas: [GEO]", "knowledge_areas: [GEO, GEO]"))) == ["schema.duplicate_items"]


# --- cross references ----------------------------------------------------------------

def test_parameter_column_must_be_declared(tmp_path):
    text = edit("          column: UF\n", "          column: SG_UF\n")
    found = check(tmp_path, text)
    assert ("ref.undeclared_column", "execution.applications.ibama_autos.parameters.parent.column") in [
        (f.code, f.path) for f in found]
    assert "ref.unused_column" in codes(found, "warning")      # UF is now declared but unused


def test_lookup_source_must_exist(tmp_path):
    found = check(tmp_path, edit("          source: uf_codes\n", "          source: ufs\n"))
    assert [(f.code, f.path) for f in found if f.level == "error"] == [
        ("ref.unknown_source", "execution.applications.ibama_autos.parameters.parent_lookup.source")]


def test_identity_column_must_be_declared(tmp_path):
    found = check(tmp_path, edit("columns: [SEQ_AUTO_INFRACAO]", "columns: [SEQ_AUTO]"))
    assert ("ref.undeclared_column", "execution.applications.ibama_autos.evaluation.identity.columns[0]") in [
        (f.code, f.path) for f in found]


def test_field_meaning_must_point_to_a_declared_column(tmp_path):
    found = check(tmp_path, edit("\n      column: COD_MUNICIPIO\n      meaning", "\n      column: CD_MUNICIPIO\n      meaning"))
    assert [(f.code, f.path) for f in found] == [("ref.undeclared_column", "description.field_meanings[0].column")]


def test_unused_column_is_a_warning(tmp_path):
    text = edit("            SEQ_AUTO_INFRACAO:\n", "            DES_AUTO_INFRACAO:\n              type: string\n"
                "              missing_values: [\"\"]\n            SEQ_AUTO_INFRACAO:\n")
    found = check(tmp_path, text)
    assert [(f.level, f.code) for f in found] == [("warning", "ref.unused_column")]
    assert found[0].path.endswith("DES_AUTO_INFRACAO")


def test_unicode_headers_are_kept_exactly(tmp_path):
    text = TEXT.replace("COD_MUNICIPIO", "Código do município")
    assert check(tmp_path, text) == []


# --- regular-expression subset --------------------------------------------------------

@pytest.mark.parametrize("pattern", ["[0-9]{7}", "[A-Z]{2}", "(AC|AL|AP)", "[0-9]{2,3}\\.[0-9]+", "[^;]*"])
def test_accepted_patterns(pattern):
    assert validate.pattern_problem(pattern) is None


@pytest.mark.parametrize("pattern, reason", [
    ("^[0-9]{7}$", "^ ou $"),
    ("\\d{7}", "\\d"),
    ("(?=a)b", "(?"),
    ("(a)\\1", "\\1"),
    ("a*?", "preguiçoso"),
    ("a{2,1}", "limites"),
    ("a{5000}", "limites"),
    ("a{", "{ literal"),
    ("[0-9", "sem ]"),
    ("\\p{L}+", "\\p"),
])
def test_refused_patterns(pattern, reason):
    assert reason in validate.pattern_problem(pattern)


def test_refused_pattern_is_reported_on_its_line(tmp_path):
    found = check(tmp_path, edit("pattern: '[0-9]{7}'", "pattern: '^[0-9]{7}$'"))
    assert codes(found) == ["pattern.subset"]
    assert "pattern: '^[0-9]{7}$'" in edit("pattern: '[0-9]{7}'", "pattern: '^[0-9]{7}$'").splitlines()[found[0].line - 1]


# --- folders -------------------------------------------------------------------------

def test_file_name_must_match_id(tmp_path):
    assert codes(check(tmp_path, TEXT, name="other.yaml")) == ["id.file_name"]


def test_duplicate_ids_in_a_folder(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    for d in ("a", "b"):
        (tmp_path / d / f"{RULE_ID}.yaml").write_text(TEXT, encoding="utf-8")
    assert codes(validate.validate_paths([tmp_path])) == ["id.duplicate"]


def test_yml_extension_is_refused(tmp_path):
    (tmp_path / "x.yml").write_text(TEXT, encoding="utf-8")
    assert codes(validate.validate_paths([tmp_path])) == ["file.extension"]


# --- documentation -------------------------------------------------------------------

def test_readme_and_leiame_match():
    """README.md and LEIAME.md: same heading structure, code blocks and cross links."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    leiame = (ROOT / "LEIAME.md").read_text(encoding="utf-8")

    def outline(text):
        lines, fenced = [], False
        for line in text.splitlines():
            if line.startswith("```"):
                fenced = not fenced
                lines.append("```")
            elif not fenced and re.match(r"#{1,6} ", line):
                lines.append(line.split(" ")[0])
        return lines

    assert outline(readme) == outline(leiame)
    assert "(LEIAME.md)" in readme and "(README.md)" in leiame
