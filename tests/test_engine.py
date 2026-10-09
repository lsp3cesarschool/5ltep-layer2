"""Engine tests on excerpts of the real sources of IB-13.

The TSE lines are copied from municipio_tse_ibge.csv (dadosabertos.tse.jus.br, generated
04/10/2026). The IBAMA pairs (COD_MUNICIPIO, UF) are values found in auto_infracao_1986.csv and
other members of the IBAMA resource on 08/10/2026, with the other columns left out. The only pair
that is not in the data is the rule's own documented example of a signal (Recife with AL): the
real data had no mismatch on 08/10/2026.

The full run against the portals is `test_full_run_against_the_portals`, skipped unless
L2_NETWORK=1 (it downloads about 120 MB).
"""

import io
import json
import os
import zipfile
from pathlib import Path

import pytest

from src import engine, outputs
from src.fetch import Fetched, ResourceKey
from src.loader import load_rule

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
RULE = load_rule(FIXTURES / "municipality-state.yaml").data

TSE = (
    '"DT_GERACAO";"HH_GERACAO";"CD_UF_TSE";"CD_UF_IBGE";"SG_UF";"NM_UF";"CD_MUNICIPIO_TSE";'
    '"NM_MUNICIPIO_TSE";"CD_MUNICIPIO_IBGE";"NM_MUNICIPIO_IBGE"\r\n'
    '"04/10/2026";"09:00:06";2;31;"MG";"Minas Gerais";"45217";"Formiga";3126109;"Formiga"\r\n'
    '"04/10/2026";"09:00:06";8;26;"PE";"Pernambuco";"25313";"Recife";2611606;"Recife"\r\n'
    '"04/10/2026";"09:00:06";1;35;"SP";"São Paulo";"71676";"Tambaú";3553302;"Tambaú"\r\n'
)

IBAMA_1986 = "COD_MUNICIPIO;UF\n3126109;MG\n9999999;DF\n3553302;SP\n"     # records 1, 2, 3
IBAMA_1987 = "COD_MUNICIPIO;UF\n431173;RS\n;\n2611606;PE\n2611606;AL\n"   # records 1, 2, 3, 4


def zip_file(path: Path, members: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
    return path


def fetched(path: Path, source: dict) -> Fetched:
    f = Fetched(ResourceKey.of(source), path=path)
    f.download = {"sha256": "test"}
    return f


@pytest.fixture
def reads(tmp_path):
    ibama = zip_file(tmp_path / "ibama.zip", {"auto_infracao_1986.csv": IBAMA_1986.encode("utf-8"),
                                               "auto_infracao_1987.csv": IBAMA_1987.encode("utf-8"),
                                               "leiame.pdf": b"%PDF"})
    tse = zip_file(tmp_path / "tse.zip", {"municipio_tse_ibge.csv": TSE.encode("latin-1")})
    src = RULE["sources"]
    return {"ibama_autos": engine.read_source(fetched(ibama, src["ibama_autos"]), src["ibama_autos"], tmp_path / "a.csv"),
            "tse_municipios": engine.read_source(fetched(tse, src["tse_municipios"]), src["tse_municipios"], tmp_path / "t.csv")}


def test_members_are_read_in_order_and_numbered_per_file(reads):
    assert reads["ibama_autos"].members == [{"name": "auto_infracao_1986.csv", "records": 3},
                                            {"name": "auto_infracao_1987.csv", "records": 4}]
    assert reads["tse_municipios"].records == 3          # latin-1 decoded, quoted fields


def test_lookup_equals_outcomes_and_record_numbers(reads):
    result = engine.evaluate(RULE, reads)
    assert result["counts"] == {"match": 3, "mismatch": 1, "key_not_found": 2, "missing_value": 1, "invalid_value": 0,
                                "ambiguous_key": 0, "out_of_scope": 0}
    assert result["total"] == 7 == sum(result["counts"].values())
    assert result["records"] == {
        "key_not_found": {"auto_infracao_1986.csv": [2], "auto_infracao_1987.csv": [1]},
        "missing_value": {"auto_infracao_1987.csv": [2]},
        "mismatch": {"auto_infracao_1987.csv": [4]},
    }


def test_only_declared_columns_reach_the_work_file(tmp_path):
    text = "COD_MUNICIPIO;MUNICIPIO;UF\n3126109;FORMIGA;MG\n"            # MUNICIPIO is not declared
    path = zip_file(tmp_path / "i.zip", {"auto_infracao_1986.csv": text.encode()})
    source = RULE["sources"]["ibama_autos"]
    read = engine.read_source(fetched(path, source), source, tmp_path / "a.csv")
    content = read.path.read_text(encoding="utf-8")
    assert content.splitlines() == ["__member,__record,COD_MUNICIPIO,UF", "auto_infracao_1986.csv,1,3126109,MG"]


@pytest.mark.parametrize("members, code", [
    ({"outro.csv": b"COD_MUNICIPIO;UF\n"}, "member_missing"),
    ({"auto_infracao_1986.csv": b"COD_MUN;UF\n1;MG\n"}, "column_missing"),
    ({"auto_infracao_1986.csv": "COD_MUNICIPIO;UF\n3126109;São\n".encode("latin-1")}, "decode_error"),
])
def test_read_problems_are_reported(tmp_path, members, code):
    source = RULE["sources"]["ibama_autos"]
    path = zip_file(tmp_path / "i.zip", members)
    with pytest.raises(engine.ReadError) as exc:
        engine.read_source(fetched(path, source), source, tmp_path / "a.csv")
    assert exc.value.code == code


def test_failed_source_makes_the_rule_not_evaluated(tmp_path, monkeypatch):
    def unreachable(key, folder):
        f = Fetched(key)
        f.status, f.reason = "portal_unreachable", "portal não respondeu: tempo esgotado (60 s)"
        return f
    monkeypatch.setattr(engine, "fetch", unreachable)
    run = engine.run([ROOT / "rules"], tmp_path, log=lambda *a: None)
    entry = run["rules"][0]
    assert entry["status"] == "not_evaluated" and entry["reason_code"] == "source_portal_unreachable"
    assert "counts" not in entry
    totals = outputs.write(run, tmp_path / "out", ROOT / "rules")
    assert totals["evaluated"] == 0 and totals["sources_ok"] == 0
    page = json.loads((tmp_path / "out" / "docs" / "data" / "layer2.json").read_text(encoding="utf-8"))
    assert page["rules"][0]["status"] == "not_evaluated"
    assert not (tmp_path / "out" / "docs" / "data" / "rules" / "municipality-state.json").exists()


@pytest.mark.skipif(os.environ.get("L2_NETWORK") != "1", reason="downloads ~120 MB; set L2_NETWORK=1")
def test_full_run_against_the_portals(tmp_path):
    run = engine.run([ROOT / "rules"], tmp_path, log=lambda *a: None)
    entry = run["rules"][0]
    assert entry["status"] == "evaluated", entry.get("reason")
    assert entry["total"] == sum(entry["counts"].values()) > 0
    outputs.write(run, tmp_path / "out", ROOT / "rules")
    for f in (tmp_path / "out").rglob("*.json"):
        assert "NOME_INFRATOR" not in f.read_text(encoding="utf-8")


def test_interval_only_rule_leaves_order_to_another_rule(tmp_path):
    """IB-12c with check_order: false, on the cases documented in the rule (plus the reverse order)."""
    rule = load_rule(FIXTURES / "issued-over-five-years-after-fact.yaml").data
    text = ("DT_FATO_INFRACIONAL;DAT_HORA_AUTO_INFRACAO\n"
            "2010-01-01;2014-12-31 10:00:00\n"      # documented: conforme
            "2010-01-01;2016-01-02\n"               # documented: sinalizar (more than five years)
            "2016-01-02;2010-01-01\n"               # fact after the notice: counted by fact-after-issue
            ";2016-01-02\n")                        # no fact date: out of scope (where)
    path = zip_file(tmp_path / "a.zip", {"auto_infracao_2010.csv": text.encode()})
    source = rule["sources"]["ibama_autos"]
    read = engine.read_source(fetched(path, source), source, tmp_path / "a.csv")
    result = engine.evaluate(rule, {"ibama_autos": read})
    assert {k: v for k, v in result["counts"].items() if v} == {"match": 1, "mismatch": 1, "out_of_scope": 2}
    assert result["records"] == {"mismatch": {"auto_infracao_2010.csv": [2]}}


def test_counts_only_exposure_publishes_no_record_numbers(tmp_path, monkeypatch):
    """A rule with exposure: counts publishes counts and charts, never record numbers."""
    rules = tmp_path / "rules"
    rules.mkdir()
    text = (FIXTURES / "municipality-state.yaml").read_text(encoding="utf-8")
    (rules / "municipality-state.yaml").write_text(text.replace('origin: cross_reference\n',
                                                               'origin: cross_reference\nexposure: counts\n'), encoding="utf-8")
    run = {"started_at": "x", "finished_at": "y", "fetched": [], "problems": [], "timings": {},
           "rules": [{"id": "municipality-state", "file": rules / "municipality-state.yaml", "rule_text": b"",
                      "data": load_rule(rules / "municipality-state.yaml").data, "status": "evaluated",
                      "evaluated_at": "y", "counts": {**dict.fromkeys(engine.OUTCOMES, 0), "match": 1, "mismatch": 1}, "total": 2,
                      "records": {"mismatch": {"a.csv": [2]}}, "members": [], "by_member": {}, "by_period": {},
                      "sources": {}}]}
    outputs.write(run, tmp_path / "out", rules)
    data = json.loads((tmp_path / "out" / "docs" / "data" / "rules" / "municipality-state.json").read_text(encoding="utf-8"))
    assert data["records"] == {} and data["counts"]["mismatch"] == 1
