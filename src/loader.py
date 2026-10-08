"""Safe reading of rule files.

A rule file is one YAML 1.2 document of plain mappings, lists and scalars. Anything that can make
two readers see different content, or that YAML 1.1 parsers interpret differently, is refused
before validation: duplicate keys, anchors, aliases, merge keys, explicit tags, version directives
and several documents in one file. Line numbers are kept so messages can point to the author's text.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.error import MarkedYAMLError, YAMLError
from ruamel.yaml.events import AliasEvent, CollectionStartEvent, DocumentStartEvent, ScalarEvent


class RuleLoadError(Exception):
    """The file cannot be read as a rule; `line` is 1-based when known."""

    def __init__(self, code: str, message: str, line: int | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.line = line


@dataclass
class LoadedRule:
    path: Path
    data: dict                      # plain Python values (dict, list, str, int, float, bool, None)
    tree: CommentedMap = field(repr=False)  # round-trip tree, used only to find line numbers

    def line_of(self, path) -> int | None:
        """1-based line of the deepest existing node on `path` (a sequence of keys/indexes)."""
        node, line = self.tree, 1
        for step in path:
            try:
                if isinstance(node, CommentedMap) and step in node:
                    line = node.lc.key(step)[0] + 1
                    node = node[step]
                elif isinstance(node, CommentedSeq) and isinstance(step, int) and 0 <= step < len(node):
                    line = node.lc.item(step)[0] + 1
                    node = node[step]
                else:
                    break
            except (AttributeError, KeyError, TypeError):
                break
        return line


def _yaml() -> YAML:
    yaml = YAML(typ="rt")
    yaml.version = (1, 2)
    yaml.allow_duplicate_keys = False
    return yaml


def _check_events(text: str) -> None:
    documents = 0
    for event in _yaml().parse(io.StringIO(text)):
        line = event.start_mark.line + 1 if event.start_mark else None
        if isinstance(event, DocumentStartEvent):
            documents += 1
            if documents > 1:
                raise RuleLoadError("yaml.multiple_documents", "o arquivo deve conter um único documento YAML", line)
            if getattr(event, "version", None):
                raise RuleLoadError("yaml.version_directive", "diretiva %YAML não é aceita; o formato usa YAML 1.2", line)
            if getattr(event, "tags", None):
                raise RuleLoadError("yaml.tag_directive", "diretiva %TAG não é aceita", line)
        if isinstance(event, AliasEvent):
            raise RuleLoadError("yaml.alias", f"alias *{event.anchor} não é aceito; repita o conteúdo explicitamente", line)
        if isinstance(event, ScalarEvent) and event.value == "<<" and event.style is None:
            raise RuleLoadError("yaml.merge_key", "chave de mesclagem << não é aceita", line)
        if isinstance(event, (ScalarEvent, CollectionStartEvent)):
            if event.anchor:
                raise RuleLoadError("yaml.anchor", f"âncora &{event.anchor} não é aceita", line)
            if event.tag:
                raise RuleLoadError("yaml.tag", f"tag explícita {event.tag} não é aceita", line)


def _plain(node, path=()):
    """Copy the round-trip tree into plain values; refuse merge keys."""
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if key == "<<":
                raise RuleLoadError("yaml.merge_key", "chave de mesclagem << não é aceita")
            if not isinstance(key, str):
                raise RuleLoadError("yaml.key_type", f"chave {key!r} precisa ser texto; use aspas")
            out[str(key)] = _plain(value, path + (key,))
        return out
    if isinstance(node, list):
        return [_plain(value, path + (i,)) for i, value in enumerate(node)]
    if isinstance(node, bool) or node is None:
        return node
    if isinstance(node, str):
        return str(node)
    if isinstance(node, int):
        return int(node)
    if isinstance(node, float):
        return float(node)
    return node  # dates and other types are kept so the schema reports them as the wrong type


def load_rule(path: Path) -> LoadedRule:
    try:
        text = Path(path).read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuleLoadError("file.encoding", f"o arquivo precisa estar em UTF-8 ({exc.reason})") from exc
    if text.startswith("﻿"):
        text = text[1:]
    try:
        _check_events(text)
        tree = _yaml().load(text)
    except RuleLoadError:
        raise
    except MarkedYAMLError as exc:
        line = exc.problem_mark.line + 1 if exc.problem_mark else None
        code = "yaml.duplicate_key" if "duplicate key" in str(exc) else "yaml.syntax"
        problem = exc.problem or str(exc)
        message = "chave repetida no mesmo mapa" if code == "yaml.duplicate_key" else f"YAML inválido: {problem}"
        raise RuleLoadError(code, message, line) from exc
    except YAMLError as exc:
        raise RuleLoadError("yaml.syntax", f"YAML inválido: {exc}") from exc
    if not isinstance(tree, CommentedMap):
        raise RuleLoadError("yaml.root", "a raiz do arquivo deve ser um mapa de campos", 1)
    return LoadedRule(path=Path(path), data=_plain(tree), tree=tree)
