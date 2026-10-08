# 5LTEP-L2: 5L-TEP Layer 2 Semantic Policies Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**English** · [Português](LEIAME.md)

**Domain rules, written by people after the data exists, checked against open data portals.**
Layer 2 of the Five-Layer Trust Engineering Pyramid (5L-TEP, SOFTENG 2026) turns knowledge that a
schema cannot hold (a municipality code must belong to the state it is paired with; a licence cannot
expire before it is issued) into rule files that anyone can read, review and adapt to another
CKAN portal.

> **Status: early research prototype.** This repository currently contains the rule format 1.0,
> its JSON Schema and a validator. The engine that downloads the CKAN resources and evaluates the
> rules runs locally; there are **no published results** here yet. The rules are examples with
> their foundations and open questions recorded; they are not official rules of any agency, and a
> future signal will be something to review, never a verdict on the data.

## What a rule looks like

Each file in `rules/` holds one check that crosses data from one or more **CKAN** portals. A file in
`rules/` is active; subfolders are free and only organise the rules.

| Part | For whom | Content |
|---|---|---|
| `schema_version`, `id`, `version`, `origin` | everyone | format version, stable identifier, rule version, who proposed it |
| `description` | people (dashboard) | title, what is checked, justification, exceptions and examples, in a language declared by a BCP 47 tag |
| `sources` | the engine | for each CKAN resource: portal, dataset, exact resource name and format, how to unpack it (`archive`), how to read it (`file`) and the columns read, each with its meaning |
| `check` | the engine | an allowed template and its parameters, written as `source.column` |

Only `sources` and `check` define what is computed. Free SQL, code or expressions are never
accepted. The example [`rules/territory/territory.municipality-state.yaml`](rules/territory/territory.municipality-state.yaml)
looks up each infraction notice's municipality code (IBAMA portal) in the table of municipalities
published by the Brazilian electoral court (TSE portal) and compares the state.

## Validate rules

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Linux/macOS: .venv/bin/python
python main.py validate                                   # every rules/**/*.yaml
python main.py validate rules/territory --format json
python -m pytest
python main.py run                                        # local test run: downloads the sources, outputs in work/out
```

The validator reports file, line, path and a stable code for each problem (messages are in
Portuguese, the initial interface language). It checks:

- **safe YAML 1.2:** one document; no duplicate keys, anchors, aliases, merge keys or explicit tags;
  UTF-8;
- **the schema** [`schema/rule-v1.schema.json`](schema/rule-v1.schema.json), one file for every rule:
  required fields, closed sets of fields and tokens, parameters of each template;
- **cross references:** every `source.column` used by `check` is declared in `sources`; declared but
  unused sources or columns are warnings;
- **folders:** one `<id>.yaml` per rule, at any subfolder depth, and unique ids.

## Write a rule

Copy the example, give it a new `id` and file name, and edit it. Find the exact dataset and resource
names in `<portal>/api/3/action/package_show?id=<dataset>`, and download the file once to check what
is inside the archive, its encoding, delimiter and headers. Quote versions and codes. Version 1.0
specifies one template, `lookup-equals`; other templates are added to the same schema as they get a
parameter contract.

Optional, per editor: VS Code with the YAML extension reads [`.vscode/settings.json`](.vscode/settings.json),
which maps the schema to every `rules/**/*.yaml` and gives completion and inline checks. In other
editors, map the same schema to the same pattern (JetBrains: *JSON Schema Mappings*; Neovim, Helix,
Zed: the `yaml-language-server` settings). Nothing in the rule files depends on the editor.

## Repository layout

```
main.py            command line (validate, run)
src/loader.py      safe YAML reading with line numbers
src/validate.py    schema and cross references
src/fetch.py       CKAN resolution and download, with integrity of each source
src/engine.py      reading of the declared columns, DuckDB, templates
src/outputs.py     results/ and docs/data/ (counts and record numbers only)
src/accept.py      the publish job's check of a run's artifact
docs/              dashboard (index.html, app.js, style.css; data/ is written by the runs)
.github/workflows/ layer2.yml (weekly run), tests.yml
schema/            JSON Schema of the authoring format
rules/             one file per rule, grouped by namespace
tests/             automated tests
```

## How a run works

`.github/workflows/layer2.yml` runs every Wednesday at 04:30 UTC (or by hand). The **evaluate** job,
with a read-only token, downloads each CKAN resource once, records whether each portal and resource
was available (HTTP status, SHA-256 of the bytes, columns found), crosses the data with DuckDB
without external access and uploads its outputs as an artifact. The **publish** job checks the
artifact (`python main.py accept`: expected files only, valid JSON, record lists made of numbers,
earlier history kept) and commits `results/` and `docs/data/`. The dashboard in `docs/` (GitHub
Pages from `/docs`) shows the rules, the health of each source, the history and the provenance; each
visitor can order the rule cards, and that order is kept in their browser only. Only counts and
record numbers are published, never values from the portals.

## Next steps

Issue forms for authors who do not write YAML, more templates, and the control instances for ANEEL
and the city of Recife.

## License and citation

Code under the [MIT License](LICENSE). Citation metadata in [`CITATION.cff`](CITATION.cff).
