# 5LTEP-L2: 5L-TEP Layer 2 Semantic Policies Toolkit

[![Tests](https://github.com/lsp3cesarschool/5ltep-layer2/actions/workflows/tests.yml/badge.svg)](https://github.com/lsp3cesarschool/5ltep-layer2/actions/workflows/tests.yml) [![Layer 2](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Flsp3cesarschool%2F5ltep-layer2%2Fmain%2Fdocs%2Fdata%2Fstatus.json)](https://github.com/lsp3cesarschool/5ltep-layer2/actions/workflows/layer2.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**English** · [Português](LEIAME.md)

**Domain rules, written by people after the data exists, that cross CKAN open data portals: 35
rules on the portal of IBAMA, Brazil's federal environmental agency.** Every week each rule reads the published files, counts the records
that deserve a second look and shows them on a dashboard. A signal is something to review, never a
verdict on the data.

| Resource | What you find there |
|---|---|
| 📊 **Dashboard** | [lsp3cesarschool.github.io/5ltep-layer2](https://lsp3cesarschool.github.io/5ltep-layer2/?lang=en): every rule with its signals, charts and record numbers, source health, download and processing speed, history, provenance |
| 📏 **Rules** | [`rules/`](rules/): one file per check, in plain YAML |
| 📁 **Results** | [`results/`](results/) and [`docs/data/`](docs/data/): written by each run (counts, record numbers, hashes) |
| 🔁 **Control experiments** | [5ltep-layer2-aneel](https://github.com/lsp3cesarschool/5ltep-layer2-aneel) ([dashboard](https://lsp3cesarschool.github.io/5ltep-layer2-aneel/?lang=en)) and [5ltep-layer2-recife](https://github.com/lsp3cesarschool/5ltep-layer2-recife) ([dashboard](https://lsp3cesarschool.github.io/5ltep-layer2-recife/?lang=en)): the same code on the portals of ANEEL and Recife |

> **Status: research demonstration.** This repository is part of a master's research project and is
> maintained by its author. It is not operated by, affiliated with or endorsed by IBAMA or any other
> publisher; it only reads open data from CKAN portals. The rules are examples written by the author.

## Use case in one paragraph

A researcher maps environmental infractions by municipality from IBAMA's infraction notices.
Each notice carries a municipality code and a state, and the map trusts that they agree. One rule of
this repository looks every municipality code up in the table of municipalities that Brazil's
electoral court (TSE) publishes on its own CKAN portal and compares the state; others check the order
of the dates of a notice, whether coordinates are missing or at (0,0), whether linked records exist in
the other extracts, or whether a CITES permit combines Appendix I, wild origin and commercial purpose.
Before drawing the map, the researcher sees on the dashboard which records deserve a second look, in
which file and line, without this repository publishing any value of those records.

## Key terms

| Term | Meaning here |
|---|---|
| **Rule** | One YAML file in `rules/`: a description for people and a check for the engine. A file in `rules/` is active; subfolders only organise. |
| **Source** | A CKAN resource (portal, dataset, exact resource name and format), or several resources of one dataset matched by a name pattern, with how to open the file and which columns to read. |
| **Template** | The fixed check a rule fills in: `lookup-equals`, `lookup-exists`, `temporal-order`, `field-comparison`, `flag-when`. Rules never carry SQL or code. |
| **Signal** | A record that failed the check, or could not be checked (value missing or unreadable, key not found). Something to review, not a verdict. |
| **Record number** | The line of the record in the published file (1 = first line after the header), valid for the bytes whose SHA-256 the run records. |
| **Source health** | Whether each portal answered and each resource downloaded in a run; a rule whose source failed is "not evaluated", never partially evaluated. |

## How a rule looks

```
schema_version: "1.0"
rule_version: "0.3.0"
origin: cross_reference
description:  {language, title, text, justification, exceptions, examples}
sources:      {name: {portal, dataset, resource, archive, file, columns}}
check:        {template, parameters, where, timeline}
```

The file name is the rule's identifier. [`schema/rule-v1.schema.json`](schema/rule-v1.schema.json)
is the contract of the format, one file for every rule; `python main.py validate` checks the schema
and that every column a check uses is declared. The rule manual of the main repository explains
each field.

## How a run works

[`.github/workflows/layer2.yml`](.github/workflows/layer2.yml) runs every Wednesday at 04:30 UTC (or
by hand). The **evaluate** job, with a read-only token, downloads each CKAN resource once (however
many rules use it), records whether each portal and resource was available, reads only the declared
columns, evaluates every rule with DuckDB without external access and uploads its outputs as an
artifact. The **publish** job checks the artifact (`python main.py accept`: expected files only,
valid JSON, record lists made of numbers, earlier history kept) and commits `results/` and
`docs/data/`. Each run also records the download speed of this portal and of the others, and the
time of each phase.

## Data handling and privacy

The files are downloaded during the run and deleted at its end; on GitHub the runner itself is
discarded after the job. The engine reads only the columns a rule declares. What is published are
counts, record numbers, SHA-256 hashes and metadata published by CKAN, never a value read from the
portals. Rules on health or education data use `exposure: counts`: they publish counts and charts
only, never record numbers. The datasets keep the licences of their publishers, shown with links on
the dashboard.

## Run it locally

```
python -m pip install -r requirements.txt
python main.py validate
python -m pytest
python main.py run        # local test run: downloads the sources, outputs in work/out
```

A local run is a test: published results come only from GitHub Actions.

## Repository layout

```
main.py            command line (validate, run, accept)
src/               loader, validator, templates, fetch, engine, outputs, accept
schema/            JSON Schema of the rule format
rules/             one file per rule, in subfolders
portal.json        the portal of this instance
docs/              dashboard (data/ is written by the runs)
results/           results of the runs
tests/             automated tests
```

## License and citation

Code under the [MIT License](LICENSE). Citation metadata in [`CITATION.cff`](CITATION.cff).
