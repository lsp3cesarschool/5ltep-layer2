"""Layer 2 validation tests. Each case edits the example rule and checks the finding it must produce."""

import json
import re
from pathlib import Path

import pytest

import main
from src import validate

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
EXAMPLE = FIXTURES / "municipality-state.yaml"       # a copy of an IBAMA rule: the tests do not depend on rules/
TEXT = EXAMPLE.read_text(encoding="utf-8")
RULE_ID = "municipality-state"


def check(tmp_path, text, name=RULE_ID + ".yaml"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return validate.validate_paths([path])


def edit(old, new, text=TEXT, count=1):
    assert text.count(old) == count, old
    return text.replace(old, new)


def codes(findings, level=None):
    return [f.code for f in findings if level is None or f.level == level]


def line_of(text, fragment):
    return next(i for i, line in enumerate(text.splitlines(), 1) if fragment in line)


# --- the example ---------------------------------------------------------------------

def test_example_rule_is_valid():
    assert validate.validate_paths([FIXTURES]) == []


def test_rules_of_this_instance_are_valid():
    assert [f for f in validate.validate_paths([ROOT / "rules"]) if f.level == "error"] == []


def test_root_copy_matches_the_rule():
    copy = ROOT.parent / "exemploderegra.yaml"
    if not copy.exists() or not (ROOT / "rules" / "territory" / "municipality-state.yaml").exists():
        pytest.skip("cópia da raiz só existe na pasta local do projeto")
    body = [line for line in copy.read_text(encoding="utf-8").splitlines() if not line.startswith("#")]
    assert body == TEXT.splitlines()


def test_schema_is_a_valid_draft_2020_12_schema():
    validate.Draft202012Validator.check_schema(validate.load_schema())


def test_cli_exit_codes(tmp_path):
    assert main.main(["validate", str(FIXTURES)]) == 0
    bad = tmp_path / f"{RULE_ID}.yaml"
    bad.write_text(edit("origin: cross_reference", "origin: cruzamento"), encoding="utf-8")
    assert main.main(["validate", str(bad)]) == 1


def test_cli_json_output(tmp_path, capsys):
    bad = tmp_path / f"{RULE_ID}.yaml"
    bad.write_text(edit("origin: cross_reference", "origin: cruzamento"), encoding="utf-8")
    main.main(["validate", str(bad), "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert data[0]["code"] == "schema.enum" and data[0]["path"] == "origin"
    assert data[0]["line"] == line_of(TEXT, "origin:")


# --- safe YAML -----------------------------------------------------------------------

@pytest.mark.parametrize("old, new, code", [
    ("origin: cross_reference\n", "origin: cross_reference\norigin: expert\n", "yaml.duplicate_key"),
    ("origin: cross_reference", "origin: &o cross_reference", "yaml.anchor"),
    ('rule_version: "0.4.0"', "rule_version: !!str 0.4.0", "yaml.tag"),
    ('schema_version: "1.0"\n', 'schema_version: "1.0"\nextra: {<<: {a: 1}}\n', "yaml.merge_key"),
])
def test_unsafe_yaml_is_refused(tmp_path, old, new, code):
    assert codes(check(tmp_path, edit(old, new))) == [code]


def test_version_directive_and_multiple_documents_are_refused(tmp_path):
    assert codes(check(tmp_path, "%YAML 1.1\n---\n" + TEXT)) == ["yaml.version_directive"]
    assert codes(check(tmp_path, TEXT + "---\na: 1\n")) == ["yaml.multiple_documents"]


def test_unquoted_version_is_refused(tmp_path):
    found = check(tmp_path, edit('rule_version: "0.4.0"', "rule_version: 0.4"))
    assert codes(found) == ["schema.type"]


def test_not_utf8_is_refused(tmp_path):
    path = tmp_path / f"{RULE_ID}.yaml"
    path.write_bytes(TEXT.encode("utf-8") + b"# C\xf3digo em Latin-1\n")
    assert codes(validate.validate_paths([path])) == ["file.encoding"]


# --- schema --------------------------------------------------------------------------

def test_schema_version_is_required(tmp_path):
    found = check(tmp_path, edit('schema_version: "1.0"\n', ""))
    assert [(f.code, f.message) for f in found] == [("schema.required", 'falta o campo obrigatório "schema_version"')]


def test_portuguese_token_is_refused_with_line(tmp_path):
    found = check(tmp_path, edit("origin: cross_reference", "origin: cruzamento"))
    assert [(f.code, f.path) for f in found] == [("schema.enum", "origin")]
    assert '"cross_reference"' in found[0].message


@pytest.mark.parametrize("field", ["status: example", "seed_ids: [IB-13]", "classification: {category: DC}",
                                   "id: municipality-state", "version: \"0.4.0\""])
def test_removed_fields_are_refused(tmp_path, field):
    found = check(tmp_path, edit("origin: cross_reference\n", f"origin: cross_reference\n{field}\n"))
    assert codes(found) == ["schema.unknown_field"]


def test_unknown_source_field_points_to_its_line(tmp_path):
    text = edit("    dataset: fiscalizacao-auto-de-infracao\n",
                "    dataset: fiscalizacao-auto-de-infracao\n    colums: {}\n")
    found = check(tmp_path, text)
    assert [(f.code, f.path) for f in found] == [("schema.unknown_field", "sources.ibama_autos.colums")]
    assert found[0].line == line_of(text, "colums:")


def test_template_without_contract_is_refused(tmp_path):
    assert "schema.enum" in codes(check(tmp_path, edit("template: lookup-equals", "template: point-in-area")))


def test_check_parameters_are_closed(tmp_path):
    text = edit("  template: lookup-equals\n", "  template: lookup-equals\n  sql: \"select 1\"\n")
    found = check(tmp_path, text)
    assert codes(found) == ["schema.unknown_field"] and found[0].path == "check.sql"


@pytest.mark.parametrize("old, new", [
    ("encoding: latin-1", "encoding: iso-8859-15"),
    ('delimiter: ";"}\n    columns:\n      CD_', 'delimiter: ";;"}\n    columns:\n      CD_'),
    ('archive: {type: zip, members: "municipio', 'archive: {type: rar, members: "municipio'),
    ("format: csv, encoding: utf-8", "format: xlsx, encoding: utf-8"),
])
def test_file_reading_tokens_are_closed(tmp_path, old, new):
    assert codes(check(tmp_path, edit(old, new))) == ["schema.enum"]


def test_portal_must_be_https(tmp_path):
    text = edit("portal: https://dadosabertos.tse.jus.br", "portal: http://dadosabertos.tse.jus.br")
    assert codes(check(tmp_path, text)) == ["schema.pattern"]


def test_archive_is_optional(tmp_path):
    text = edit('    archive: {type: zip, members: "municipio_tse_ibge.csv"}\n', "")
    assert check(tmp_path, text) == []


def test_examples_are_required(tmp_path):
    start = TEXT.index("  examples:\n")
    end = TEXT.index("\nsources:")
    found = check(tmp_path, TEXT[:start] + TEXT[end + 1:])
    assert [(f.code, f.message) for f in found] == [("schema.required", 'falta o campo obrigatório "examples"')]


# --- cross references ----------------------------------------------------------------

def test_check_column_must_be_declared(tmp_path):
    found = check(tmp_path, edit("compare: {from: ibama_autos.UF,", "compare: {from: ibama_autos.SG_UF,"))
    assert ("ref.undeclared_column", "check.compare.from") in [(f.code, f.path) for f in found]
    assert ("warning", "ref.unused_column") in [(f.level, f.code) for f in found]   # UF is now unused


def test_check_source_must_exist(tmp_path):
    found = check(tmp_path, edit("to: tse_municipios.SG_UF", "to: tse.SG_UF"))
    assert ("ref.unknown_source", "check.compare.to") in [(f.code, f.path) for f in found]


def test_key_and_compare_come_from_the_same_sources(tmp_path):
    text = edit("compare: {from: ibama_autos.UF,", "compare: {from: tse_municipios.SG_UF,")
    assert "check.mixed_sources" in codes(check(tmp_path, text), "error")


def test_unused_column_is_a_warning(tmp_path):
    text = edit('      UF: "Sigla da UF do auto"\n',
                '      UF: "Sigla da UF do auto"\n      MUNICIPIO: "Nome do município"\n')
    found = check(tmp_path, text)
    assert [(f.level, f.code, f.path) for f in found] == [
        ("warning", "ref.unused_column", "sources.ibama_autos.columns.MUNICIPIO")]


def test_unicode_headers_are_kept_exactly(tmp_path):
    text = TEXT.replace("COD_MUNICIPIO", "Código do município")
    assert check(tmp_path, text) == []


# --- folders -------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["Municipio-UF.yaml", "municipio_uf.yaml", "territory.municipio.yaml",
                                  "municipio--uf.yaml", "-municipio.yaml", "municipio uf.yaml",
                                  "municı́pio.yaml".replace("ı́", "í")])   # NFD
def test_file_name_is_the_identifier(tmp_path, name):
    assert codes(check(tmp_path, TEXT, name=name)) == ["file.name"]


@pytest.mark.parametrize("name", ["município-uf.yaml", "市町村-州.yaml", "муниципалитет-1.yaml", "λ-2.yaml"])
def test_file_names_in_any_language(tmp_path, name):
    assert check(tmp_path, TEXT, name=name) == []


def test_names_equal_after_normalising_are_duplicates(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "município-uf.yaml").write_text(TEXT, encoding="utf-8")
    (tmp_path / "b" / "município-uf.yaml").write_text(TEXT, encoding="utf-8")
    assert codes(validate.validate_paths([tmp_path])) == ["file.duplicate_name"]


def test_title_translations(tmp_path):
    assert "title_translations" in TEXT
    text = edit('    en: "Municipality', '    es: "Código del municipio"\n    en: "Municipality')
    assert check(tmp_path, text) == []
    assert codes(check(tmp_path, edit('    en: "Municipality', '    english: "Municipality'))) == ["schema.pattern"]


def test_any_subfolder_depth(tmp_path):
    deep = tmp_path / "a" / "b" / "c"
    deep.mkdir(parents=True)
    (deep / f"{RULE_ID}.yaml").write_text(TEXT, encoding="utf-8")
    assert validate.validate_paths([tmp_path]) == []


def test_duplicate_ids_in_a_folder(tmp_path):
    for d in ("a", "b"):
        (tmp_path / d).mkdir()
        (tmp_path / d / f"{RULE_ID}.yaml").write_text(TEXT, encoding="utf-8")
    assert codes(validate.validate_paths([tmp_path])) == ["file.duplicate_name"]


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
