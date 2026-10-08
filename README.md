# 5LTEP-L2: 5L-TEP Layer 2 Semantic Policies Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**English** · [Português](LEIAME.md)

**Domain rules, written by people after the data exists, checked against open data portals.**
Layer 2 of the Five-Layer Trust Engineering Pyramid (5L-TEP, SOFTENG 2026) turns knowledge that a
schema cannot hold (a municipality code must belong to the state it is paired with; a licence cannot
expire before it is issued) into rule files that anyone can read, review and adapt to another
CKAN portal.

> **Status: early research prototype.** This repository currently contains the rule authoring
> format 1.0, its JSON Schema and a validator. The engine that resolves CKAN resources and evaluates
> the rules is not implemented yet, so there are **no results** here. The rules are examples with
> their foundations and open questions recorded; they are not official rules of any agency, and a
> future signal will be something to review, never a verdict on the data.

## What a rule looks like

Each file holds one atomic check, in three parts:

| Part | For whom | Content |
|---|---|---|
| `description` | people | intention, justification, meaning of each column, exceptions, examples and sources, in any language declared by a BCP 47 tag |
| `classification` | summaries and export | form of the check (`AR`, `TC`, `DC`, `DM`), areas of knowledge, severity, quality dimension, nature of the limit |
| `execution` | the engine | an allowed template and its parameters, applied to exact portals, datasets, resources and column headers |

Only `execution` defines what is computed. Free SQL, code or expressions are never accepted: a rule
fills the parameters of a template that the engine implements. An application stays
`pending_mapping` until a person confirms what its columns mean; missing input, an unmatched
reference or a missing column are recorded as indeterminate or inapplicable, never as a pass.

The example [`rules/territory/territory.municipality-state.yaml`](rules/territory/territory.municipality-state.yaml)
checks that an IBGE municipality code starts with the code of the state it is paired with, when
both describe the same place.

## Validate rules

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Linux/macOS: .venv/bin/python
python main.py validate                                   # every rules/**/*.yaml
python main.py validate rules/territory --format json
python -m pytest
```

The validator reports file, line, path and a stable code for each problem (messages are in
Portuguese, the initial interface language). It checks:

- **safe YAML 1.2:** one document; no duplicate keys, anchors, aliases, merge keys or explicit tags;
  UTF-8;
- **the schema** [`schema/rule-v1.schema.json`](schema/rule-v1.schema.json): required fields, closed
  sets of fields and tokens, parameters of each template;
- **cross references:** every source and column named by parameters, identity and field meanings is
  declared in the same application; declared but unused columns are warnings;
- **enabling:** an `enabled` application needs a confirmed mapping review and prepared references
  (version, SHA-256, licence, coverage);
- **patterns:** `pattern` stays inside a subset of I-Regexp (RFC 9485) and matches the whole value;
- **folders:** one `<id>.yaml` per rule and unique ids.

## Write a rule

Copy the example, give it a new `id` and file name, and edit it. Editors that use the YAML language
server (VS Code with the YAML extension, for instance) read the first line of the example and offer
completion and inline checks from the schema. Quote dates, versions and codes. Version 1.0
specifies one template, `hierarchical-code`; the other candidate families need their own parameter
contract before a rule can use them.

## Repository layout

```
main.py            command line (validate)
src/loader.py      safe YAML reading with line numbers
src/validate.py    schema, cross references and pattern subset
schema/            JSON Schema of the authoring format
rules/             one file per rule, grouped by namespace
tests/             automated tests
```

## Next steps

Planned, not implemented: resolution of CKAN resources by explicit selectors, preparation of
versioned references, evaluation with DuckDB without external access, a deterministic preview of
what each application will compute, structured logs and a run manifest, issue forms for authors
who do not write YAML, and the control instances for ANEEL and the city of Recife.

## License and citation

Code under the [MIT License](LICENSE). Citation metadata in [`CITATION.cff`](CITATION.cff).
