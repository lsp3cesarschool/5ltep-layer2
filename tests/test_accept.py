"""The publish job's check of the artifact (main.py accept)."""

import json
import shutil
from pathlib import Path

import pytest

from src import accept, engine, outputs
from src.fetch import Fetched

ROOT = Path(__file__).resolve().parent.parent


def unreachable(key, folder):
    f = Fetched(key)
    f.status, f.reason = "portal_unreachable", "portal não respondeu: tempo esgotado (60 s)"
    return f


@pytest.fixture
def artifact(tmp_path, monkeypatch):
    """Outputs of a run whose sources are unreachable (no network), as the evaluate job uploads them."""
    monkeypatch.setattr(engine, "fetch", unreachable)
    run = engine.run([ROOT / "rules"], tmp_path / "work", log=lambda *a: None)
    out = tmp_path / "artifact"
    outputs.write(run, out, ROOT / "rules")
    return out


def test_first_run_is_accepted_and_copied(artifact, tmp_path):
    repo = tmp_path / "repo"
    files = accept.apply(artifact, repo)
    assert "docs/data/layer2.json" in files
    assert (repo / "results" / "history.json").exists()
    lines = [json.loads(x) for x in (repo / "results" / "run_log.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [x["stage"] for x in lines].count("download_speed") == 1
    assert {x["stage"] for x in lines} == {"fetch", "download_speed", "rule"}


def test_run_log_is_appended(artifact, tmp_path):
    repo = tmp_path / "repo"
    (repo / "results").mkdir(parents=True)
    (repo / "results" / "run_log.jsonl").write_text('{"old": 1}\n', encoding="utf-8")
    accept.apply(artifact, repo)
    assert (repo / "results" / "run_log.jsonl").read_text(encoding="utf-8").startswith('{"old": 1}\n')


def test_unexpected_file_is_refused(artifact, tmp_path):
    (artifact / "docs" / "index.html").write_text("<script>", encoding="utf-8")
    with pytest.raises(accept.Refused, match="não esperado"):
        accept.check(artifact, tmp_path / "repo")


def test_record_lists_must_hold_numbers_only(artifact, tmp_path):
    target = artifact / "docs" / "data" / "rules" / "municipality-state.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"rule": "municipality-state",
                                  "records": {"mismatch": {"auto_infracao_1986.csv": ["217"]}}}), encoding="utf-8")
    with pytest.raises(accept.Refused, match="número de registro"):
        accept.check(artifact, tmp_path / "repo")


def test_record_lists_cannot_carry_other_fields(artifact, tmp_path):
    target = artifact / "docs" / "data" / "rules" / "municipality-state.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"rule": "x", "values": ["2611606"]}), encoding="utf-8")
    with pytest.raises(accept.Refused, match="campos não esperados"):
        accept.check(artifact, tmp_path / "repo")


def test_history_must_keep_earlier_runs(artifact, tmp_path):
    repo = tmp_path / "repo"
    (repo / "results").mkdir(parents=True)
    (repo / "results" / "history.json").write_text(json.dumps([{"run_id": "1", "rules": {}}]), encoding="utf-8")
    with pytest.raises(accept.Refused, match="history"):
        accept.check(artifact, repo)


def test_invalid_json_is_refused(artifact, tmp_path):
    (artifact / "docs" / "data" / "status.json").write_text("{", encoding="utf-8")
    with pytest.raises(accept.Refused, match="JSON inválido"):
        accept.check(artifact, tmp_path / "repo")


def test_rules_folders_are_replaced(artifact, tmp_path):
    repo = tmp_path / "repo"
    stale = repo / "docs" / "data" / "rules" / "removed.rule.json"
    stale.parent.mkdir(parents=True)
    stale.write_text("{}", encoding="utf-8")
    accept.apply(artifact, repo)
    assert not stale.exists()


def test_signals_md_is_written_with_counts_only(artifact, tmp_path):
    repo = tmp_path / "repo"
    accept.apply(artifact, repo)
    text = (repo / "signals.md").read_text(encoding="utf-8")
    assert text.startswith("# Signals in ")
    assert "## Rules (most signals first)" in text and "## Source health" in text
    assert "not evaluated" in text  # unreachable sources: every rule is not evaluated, with its reason
