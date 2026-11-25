# Signals in https://dadosabertos.ibama.gov.br

Plain-text summary of the latest run of Layer 2 (semantic policies), for readers that do not run
the JavaScript of the [dashboard](https://lsp3cesarschool.github.io/5ltep-layer2/).
Generated automatically by the publish job from the checked results; do not edit by hand. A signal is a record to review, never a verdict on the data. Only counts are
shown here: the record numbers are on the dashboard and in [`docs/data/rules/`](docs/data/rules/),
and no value read from the portals is published. Times are UTC.

- **Run:** [45637533855](https://github.com/lsp3cesarschool/5ltep-layer2/actions/runs/45637533855), finished 2026-11-25 14:49 UTC (github-actions)
- **Rules:** 35 (28 evaluated, 7 not evaluated)
- **Sources:** 20 CKAN resources (19 available)
- **Records flagged:** 1,071,407
- **L2 pass rate:** 93.41% (checks without a signal / 16,281,544 checks in scope; one check per record and rule)

Signal types: `mismatch` (the check failed), `key not found` (no matching record in the other
source), `missing value`, `invalid value` (unreadable as the declared type), `ambiguous key` (more
than one match). Records outside a rule's scope (`where`) are not signals.

## Rules (most signals first)

| Rule | Records read | Signals | Previous run | Signal types |
|---|---:|---:|---:|---|
| [Harvested species missing from the list of commercial timber species](rules/forest/species-not-in-commercial-timber-list.yaml) | 2,456,925 | 826,222 | 823,715 | key not found 826,218; missing value 4 |
| [Harvest outside the authorisation's validity](rules/forest/exploration-outside-validity.yaml) | 2,456,925 | 71,161 | 69,783 | mismatch 71,161 |
| [Permanent protection and net legal reserve above the property area](rules/land/declared-areas-above-property.yaml) | 6,206,860 | 46,506 | 46,506 | mismatch 29,980; missing value 16,526 |
| [Legal basis record without a matching infraction notice](rules/infraction/legal-basis-without-infraction.yaml) | 692,775 | 35,923 | 35,908 | key not found 24,459; missing value 11,464 |
| [Infraction notice without coordinates or at (0,0)](rules/infraction/infraction-coordinates-missing-or-zero.yaml) | 713,895 | 28,362 | 28,362 | mismatch 28,362 |
| [Biome record without a matching infraction notice](rules/infraction/biomes-without-infraction.yaml) | 296,909 | 24,132 | 24,131 | key not found 14,655; missing value 9,477 |
| [Embargo term cited by the notice but not published](rules/infraction/embargo-link-without-term.yaml) | 713,895 | 21,950 | 21,889 | key not found 21,950 |
| [Specimen record without a matching infraction notice](rules/infraction/species-without-infraction.yaml) | 38,599 | 3,938 | 3,964 | key not found 7; missing value 3,931 |
| [Active ingredient sold without a registered technical product in AGROFIT](rules/pesticides/ingredient-without-registered-technical-product.yaml) | 124,311 | 2,307 | 2,307 | key not found 2,250; missing value 57 |
| [Offence dated after the infraction notice was issued](rules/infraction/fact-after-issue.yaml) | 713,895 | 2,144 | 2,138 | mismatch 2,144 |
| [Commercial CITES permit for a wild specimen of a threatened Brazilian fauna species](rules/cites/wild-commercial-threatened-species.yaml) | 259,855 | 1,714 | 1,714 | mismatch 1,714 |
| [Notice issued more than five years after the offence](rules/infraction/issued-over-five-years-after-fact.yaml) | 713,895 | 1,659 | 1,653 | mismatch 1,659 |
| [Simple fine outside the legal limits (BRL 50.00 to BRL 50,000,000.00)](rules/infraction/fine-outside-legal-limits.yaml) | 713,895 | 1,490 | 1,490 | mismatch 1,490 |
| [Offender notified before the notice was issued](rules/infraction/notice-before-issue.yaml) | 713,895 | 1,109 | 1,106 | mismatch 1,109 |
| [Municipality code consistent with the state of the same place](rules/territory/municipality-state.yaml) | 713,895 | 814 | 814 | key not found 547; missing value 267 |
| [Fire incident milestones out of order](rules/fire/incident-milestones-order.yaml) | 418,525 | 718 | 718 | mismatch 359; missing value 359 |
| [Unequivocal act ending before it starts](rules/infraction/act-end-before-start.yaml) | 713,895 | 639 | 638 | mismatch 639 |
| [CITES permit for an Appendix I species of wild origin for commercial purposes](rules/cites/appendix-i-wild-commercial.yaml) | 259,855 | 403 | 403 | mismatch 403 |
| [Cutting intensity above 30 m³/ha in forest management with mechanized skidding](rules/forest/pmfs-intensity-mechanized-over-30.yaml) | 10,372 | 87 | 87 | mismatch 87 |
| [Licence expiring before it was issued](rules/licensing/expiry-before-issue.yaml) | 14,418 | 62 | 61 | mismatch 54; missing value 8 |
| [Cutting intensity above 10 m³/ha in forest management without machines for skidding](rules/forest/pmfs-intensity-manual-over-10.yaml) | 10,372 | 28 | 28 | mismatch 28 |
| [Embargo lifted before it was imposed](rules/embargo/lifted-before-embargo.yaml) | 117,424 | 16 | 16 | mismatch 16 |
| [Embargo date outside a plausible range](rules/embargo/embargo-date-implausible.yaml) | 117,424 | 8 | 8 | mismatch 8 |
| [Preliminary licence valid for more than 5 years](rules/licensing/preliminary-licence-over-five-years.yaml) | 14,418 | 8 | 8 | mismatch 8 |
| [Installation licence valid for more than 6 years](rules/licensing/installation-licence-over-six-years.yaml) | 14,418 | 5 | 5 | mismatch 5 |
| [Operating licence valid for more than 10 years](rules/licensing/operation-licence-over-ten-years.yaml) | 14,418 | 2 | 2 | mismatch 2 |
| [Appeal judgment dated before the first-instance judgment](rules/payment/appeal-before-main-judgment.yaml) | – | – | – | not evaluated: julgamentos_auto_infracao_realizado_ambito_ibama_csv.zip: bytes inválidos para utf-8 perto do registro 1 (invalid start byte) |
| [First-instance judgment dated before the notice](rules/payment/main-judgment-before-infraction.yaml) | – | – | – | not evaluated: julgamentos_auto_infracao_realizado_ambito_ibama_csv.zip: bytes inválidos para utf-8 perto do registro 1 (invalid start byte) |
| [Infraction notice date outside a plausible range](rules/infraction/notice-date-implausible.yaml) | 713,895 | 0 | 0 | none |
| [Amount paid more than 10 times the original fine](rules/payment/paid-ten-times-original.yaml) | – | – | – | not evaluated: fonte "ibama_arrecadacao" (dadosabertos.ibama.gov.br › arrecadacao-de-multas-ambientais-bens-tutelados › Arrecadação de Multas por Bens Tutelados): 0 recursos com nome 'Arrecadação de Multas por Bens Tutelados' e formato CSV; disponíveis: ['Arrecadação de multas ambientais por bens (CSV)', 'Arrecadação de multas ambientais por bens (JSON)', 'Arrecadação de multas ambientais por bens  (XML)', 'Metadados - Arrecadação de Multas Ambientais por Bens (CSV)'] |
| [Payment dated before the infraction notice](rules/payment/payment-before-infraction.yaml) | – | – | – | not evaluated: fonte "ibama_arrecadacao" (dadosabertos.ibama.gov.br › arrecadacao-de-multas-ambientais-bens-tutelados › Arrecadação de Multas por Bens Tutelados): 0 recursos com nome 'Arrecadação de Multas por Bens Tutelados' e formato CSV; disponíveis: ['Arrecadação de multas ambientais por bens (CSV)', 'Arrecadação de multas ambientais por bens (JSON)', 'Arrecadação de multas ambientais por bens  (XML)', 'Metadados - Arrecadação de Multas Ambientais por Bens (CSV)'] |
| [Seizure term without coordinates or at (0,0)](rules/seizure/seizure-coordinates-missing-or-zero.yaml) | – | – | – | not evaluated: termo_de_apreensao.csv: o recurso não é um zip válido |
| [Seizure term cited by the notice but not published](rules/infraction/seizure-link-without-term.yaml) | – | – | – | not evaluated: termo_de_apreensao.csv: o recurso não é um zip válido |
| [Breeding stock balance does not add up](rules/fauna/stock-balance.yaml) | 173,747 | 0 | 0 | none |
| [Seizure term linked to an unpublished infraction notice](rules/seizure/term-without-infraction.yaml) | – | – | – | not evaluated: termo_de_apreensao.csv: o recurso não é um zip válido |

## Source health

| Resource | Role | Status | Size | Download | Used by |
|---|---|---|---:|---:|---|
| dadosabertos.ibama.gov.br › siscites-licencas-de-fauna-e-flora-emitidas › Siscites | primary | available | 107.4 MB | 11.9 s | appendix-i-wild-commercial, wild-commercial-threatened-species |
| dados.mma.gov.br › especies-ameacadas › FAUNA - Lista de Espécies Ameaçadas - 2021.csv | secondary | available | 0.2 MB | 0.7 s | wild-commercial-threatened-species |
| dadosabertos.ibama.gov.br › fiscalizacao-termo-de-embargo › Termos de embargo | primary | available | 215.4 MB | 22.7 s | embargo-date-implausible, embargo-link-without-term, lifted-before-embargo |
| dadosabertos.ibama.gov.br › sisfauna-plantel-exato › Sisfauna - Plantel Exato | primary | available | 73.3 MB | 2.8 s | stock-balance |
| dadosabertos.ibama.gov.br › sisfogo-roi › ROI formato csv | primary | available | 283.6 MB | 31.9 s | incident-milestones-order |
| dadosabertos.ibama.gov.br › volumes-explorados-if-100 › Volumes Explorados - IF 100% | primary | available | 52.8 MB | 7.4 s | exploration-outside-validity, species-not-in-commercial-timber-list |
| dadosabertos.ibama.gov.br › sinaflor-pmfs-amazonia-legal › PMFS Amazônia Legal | primary | available | 6.0 MB | 0.8 s | pmfs-intensity-manual-over-10, pmfs-intensity-mechanized-over-30 |
| dados.florestal.gov.br › especies-florestais-madeireiras-comerciais › Dados_abertos_especies_madeireiras_SNIF_fonte_LPF_SFB | secondary | available | 0.1 MB | 0.6 s | species-not-in-commercial-timber-list |
| dadosabertos.ibama.gov.br › fiscalizacao-auto-de-infracao › Autos de infração | primary | available | 123.9 MB | 11.3 s | act-end-before-start, biomes-without-infraction, embargo-link-without-term, fact-after-issue, fine-outside-legal-limits, infraction-coordinates-missing-or-zero, issued-over-five-years-after-fact, legal-basis-without-infraction, municipality-state, notice-before-issue, notice-date-implausible, seizure-link-without-term, species-without-infraction, term-without-infraction |
| dadosabertos.ibama.gov.br › fiscalizacao-auto-de-infracao › Autos de infração - biomas | primary | available | 14.4 MB | 0.8 s | biomes-without-infraction |
| dadosabertos.ibama.gov.br › fiscalizacao-auto-de-infracao › Autos de infração - enquadramento legal | primary | available | 8.2 MB | 0.4 s | legal-basis-without-infraction |
| dadosabertos.ibama.gov.br › fiscalizacao-termo-de-apreensao › Termo de apreensão | primary | available | 117.4 MB | 10.1 s | seizure-coordinates-missing-or-zero, seizure-link-without-term, term-without-infraction |
| dadosabertos.ibama.gov.br › fiscalizacao-auto-de-infracao › Autos de infração - espécimes | primary | available | 5.4 MB | 0.7 s | species-without-infraction |
| dadosabertos.ibama.gov.br › ato-declaratorio-ambiental-ada › Ato Declaratório Ambiental (ADA) | primary | available | 401.2 MB | 46.5 s | declared-areas-above-property |
| dadosabertos.ibama.gov.br › licencas-ambientais-de-atividades-e-empreendimentos-licenciados-pelo-ibama › Licenças ambientais de atividades e ... | primary | available | 3.4 MB | 0.4 s | expiry-before-issue, installation-licence-over-six-years, operation-licence-over-ten-years, preliminary-licence-over-five-years |
| dadosabertos.ibama.gov.br › julgamentos-de-auto-de-infracao-realizado-no-ambito-do-ibama › Volume de Julgamento de Auto de Infração | primary | available | 12.0 MB | 1.2 s | appeal-before-main-judgment, main-judgment-before-infraction |
| dadosabertos.ibama.gov.br › arrecadacao-de-multas-ambientais-bens-tutelados › Arrecadação de Multas por Bens Tutelados | primary | failed: 0 recursos com nome 'Arrecadação de Multas por Bens Tutelados' e formato CSV; disponíveis: ['Arrecadação de multas ambientais por bens (CSV)', 'Arrecadação de multas ambientais por bens (JSON)', 'Arrecadação de multas ambientais por bens  (XML)', 'Metadados - Arrecadação de Multas Ambientais por Bens (CSV)'] | – | – | paid-ten-times-original, payment-before-infraction |
| dadosabertos.ibama.gov.br › relatorios-de-comercializacao-de-agrotoxicos › Dados - CSV | primary | available | 13.6 MB | 1.2 s | ingredient-without-registered-technical-product |
| dados.agricultura.gov.br › sistema-de-agrotoxicos-fitossanitarios-agrofit › Produto Técnico | secondary | available | 0.7 MB | 0.8 s | ingredient-without-registered-technical-product |
| dadosabertos.tse.jus.br › codigos-oficiais-de-uf-e-municipios-segundo-o-tse-e-o-ibge › Códigos oficiais de UF e municípios segundo o TSE e o IBGE | secondary | available | 0.1 MB | 0.4 s | municipality-state |
