# Signals in https://dadosabertos.ibama.gov.br

Plain-text summary of the latest run of Layer 2 (semantic policies), for readers that do not run
the JavaScript of the [dashboard](https://lsp3cesarschool.github.io/5ltep-layer2/).
Generated automatically by the publish job from the checked results; do not edit by hand. A signal is a record to review, never a verdict on the data. Only counts are
shown here: the record numbers are on the dashboard and in [`docs/data/rules/`](docs/data/rules/),
and no value read from the portals is published. Times are UTC.

- **Run:** [37936431563](https://github.com/lsp3cesarschool/5ltep-layer2/actions/runs/37936431563), finished 2026-10-09 13:26 UTC (github-actions)
- **Rules:** 35 (35 evaluated, 0 not evaluated)
- **Sources:** 20 CKAN resources (20 available)
- **Records flagged:** 1,923,185

Signal types: `mismatch` (the check failed), `key not found` (no matching record in the other
source), `missing value`, `invalid value` (unreadable as the declared type), `ambiguous key` (more
than one match). Records outside a rule's scope (`where`) are not signals.

## Rules (most signals first)

| Rule | Records read | Signals | Previous run | Signal types |
|---|---:|---:|---:|---|
| [Harvested volume above the authorised volume](rules/forest/explored-volume-above-authorized.yaml) | 2,386,115 | 872,408 | 872,408 | mismatch 872,408 |
| [Harvested species missing from the list of commercial timber species](rules/forest/species-not-in-commercial-timber-list.yaml) | 2,386,115 | 804,801 | 804,801 | key not found 804,797; missing value 4 |
| [Harvest outside the authorisation's validity](rules/forest/exploration-outside-validity.yaml) | 2,386,115 | 60,091 | 60,091 | mismatch 60,091 |
| [Permanent protection and net legal reserve above the property area](rules/land/declared-areas-above-property.yaml) | 6,206,666 | 46,506 | 46,506 | mismatch 29,980; missing value 16,526 |
| [Legal basis record without a matching infraction notice](rules/infraction/legal-basis-without-infraction.yaml) | 689,929 | 34,751 | 34,751 | key not found 24,148; missing value 10,603 |
| [Infraction notice without coordinates or at (0,0)](rules/infraction/infraction-coordinates-missing-or-zero.yaml) | 711,926 | 28,345 | 28,345 | mismatch 28,345 |
| [Biome record without a matching infraction notice](rules/infraction/biomes-without-infraction.yaml) | 294,563 | 23,233 | 23,233 | key not found 14,462; missing value 8,771 |
| [Embargo term cited by the notice but not published](rules/infraction/embargo-link-without-term.yaml) | 711,926 | 21,538 | 21,538 | key not found 21,538 |
| [Seizure term cited by the notice but not published](rules/infraction/seizure-link-without-term.yaml) | 711,926 | 10,633 | 10,633 | key not found 10,633 |
| [Seizure term without coordinates or at (0,0)](rules/seizure/seizure-coordinates-missing-or-zero.yaml) | 157,955 | 4,103 | 4,103 | mismatch 4,103 |
| [Specimen record without a matching infraction notice](rules/infraction/species-without-infraction.yaml) | 38,056 | 3,395 | 3,395 | key not found 7; missing value 3,388 |
| [Active ingredient sold without a registered technical product in AGROFIT](rules/pesticides/ingredient-without-registered-technical-product.yaml) | 124,299 | 2,304 | 2,304 | key not found 2,247; missing value 57 |
| [Offence dated after the infraction notice was issued](rules/infraction/fact-after-issue.yaml) | 711,926 | 2,108 | 2,108 | mismatch 2,108 |
| [Commercial CITES permit for a wild specimen of a threatened Brazilian fauna species](rules/cites/wild-commercial-threatened-species.yaml) | 258,580 | 1,714 | 1,714 | mismatch 1,714 |
| [Notice issued more than five years after the offence](rules/infraction/issued-over-five-years-after-fact.yaml) | 711,926 | 1,596 | 1,596 | mismatch 1,596 |
| [Offender notified before the notice was issued](rules/infraction/notice-before-issue.yaml) | 711,926 | 1,093 | 1,093 | mismatch 1,093 |
| [Municipality code consistent with the state of the same place](rules/territory/municipality-state.yaml) | 711,926 | 814 | 814 | key not found 547; missing value 267 |
| [Payment dated before the infraction notice](rules/payment/payment-before-infraction.yaml) | 1,588,335 | 785 | 785 | mismatch 785 |
| [Amount paid more than 10 times the original fine](rules/payment/paid-ten-times-original.yaml) | 1,588,335 | 780 | 780 | mismatch 780 |
| [Fire incident milestones out of order](rules/fire/incident-milestones-order.yaml) | 418,525 | 718 | 718 | mismatch 359; missing value 359 |
| [Unequivocal act ending before it starts](rules/infraction/act-end-before-start.yaml) | 711,926 | 634 | 634 | mismatch 634 |
| [CITES permit for an Appendix I species of wild origin for commercial purposes](rules/cites/appendix-i-wild-commercial.yaml) | 258,580 | 403 | 403 | mismatch 403 |
| [Appeal judgment dated before the first-instance judgment](rules/payment/appeal-before-main-judgment.yaml) | 2,917 | 186 | 186 | mismatch 115; missing value 71 |
| [Cutting intensity above 30 m³/ha in forest management with mechanized skidding](rules/forest/pmfs-intensity-mechanized-over-30.yaml) | 10,099 | 87 | 87 | mismatch 87 |
| [Licence expiring before it was issued](rules/licensing/expiry-before-issue.yaml) | 14,302 | 60 | 60 | mismatch 52; missing value 8 |
| [Seizure term linked to an unpublished infraction notice](rules/seizure/term-without-infraction.yaml) | 157,955 | 29 | 29 | key not found 29 |
| [Cutting intensity above 10 m³/ha in forest management without machines for skidding](rules/forest/pmfs-intensity-manual-over-10.yaml) | 10,099 | 28 | 28 | mismatch 28 |
| [Embargo lifted before it was imposed](rules/embargo/lifted-before-embargo.yaml) | 116,763 | 16 | 16 | mismatch 16 |
| [Embargo date outside a plausible range](rules/embargo/embargo-date-implausible.yaml) | 116,763 | 8 | 8 | mismatch 8 |
| [Preliminary licence valid for more than 5 years](rules/licensing/preliminary-licence-over-five-years.yaml) | 14,302 | 8 | 8 | mismatch 8 |
| [Installation licence valid for more than 6 years](rules/licensing/installation-licence-over-six-years.yaml) | 14,302 | 5 | 5 | mismatch 5 |
| [First-instance judgment dated before the notice](rules/payment/main-judgment-before-infraction.yaml) | 2,917 | 3 | 3 | mismatch 3 |
| [Operating licence valid for more than 10 years](rules/licensing/operation-licence-over-ten-years.yaml) | 14,302 | 2 | 2 | mismatch 2 |
| [Infraction notice date outside a plausible range](rules/infraction/notice-date-implausible.yaml) | 711,926 | 0 | 0 | none |
| [Breeding stock balance does not add up](rules/fauna/stock-balance.yaml) | 173,747 | 0 | 0 | none |

## Source health

| Resource | Role | Status | Size | Download | Used by |
|---|---|---|---:|---:|---|
| dadosabertos.ibama.gov.br › siscites-licencas-de-fauna-e-flora-emitidas › Siscites | primary | available | 106.8 MB | 9.2 s | appendix-i-wild-commercial, wild-commercial-threatened-species |
| dados.mma.gov.br › especies-ameacadas › FAUNA - Lista de Espécies Ameaçadas - 2021.csv | secondary | available | 0.2 MB | 1.1 s | wild-commercial-threatened-species |
| dadosabertos.ibama.gov.br › fiscalizacao-termo-de-embargo › Termos de embargo | primary | available | 209.8 MB | 9.2 s | embargo-date-implausible, embargo-link-without-term, lifted-before-embargo |
| dadosabertos.ibama.gov.br › sisfauna-plantel-exato › Sisfauna - Plantel Exato | primary | available | 73.3 MB | 0.4 s | stock-balance |
| dadosabertos.ibama.gov.br › sisfogo-roi › ROI formato csv | primary | available | 284.1 MB | 1.4 s | incident-milestones-order |
| dadosabertos.ibama.gov.br › volumes-explorados-if-100 › Volumes Explorados - IF 100% | primary | available | 51.3 MB | 2.4 s | exploration-outside-validity, explored-volume-above-authorized, species-not-in-commercial-timber-list |
| dadosabertos.ibama.gov.br › sinaflor-pmfs-amazonia-legal › PMFS Amazônia Legal | primary | available | 5.8 MB | 0.4 s | pmfs-intensity-manual-over-10, pmfs-intensity-mechanized-over-30 |
| dados.florestal.gov.br › especies-florestais-madeireiras-comerciais › Dados_abertos_especies_madeireiras_SNIF_fonte_LPF_SFB | secondary | available | 0.1 MB | 0.6 s | species-not-in-commercial-timber-list |
| dadosabertos.ibama.gov.br › fiscalizacao-auto-de-infracao › Autos de infração | primary | available | 122.9 MB | 5.4 s | act-end-before-start, biomes-without-infraction, embargo-link-without-term, fact-after-issue, infraction-coordinates-missing-or-zero, issued-over-five-years-after-fact, legal-basis-without-infraction, municipality-state, notice-before-issue, notice-date-implausible, seizure-link-without-term, species-without-infraction, term-without-infraction |
| dadosabertos.ibama.gov.br › fiscalizacao-auto-de-infracao › Autos de infração - biomas | primary | available | 14.3 MB | 0.8 s | biomes-without-infraction |
| dadosabertos.ibama.gov.br › fiscalizacao-auto-de-infracao › Autos de infração - enquadramento legal | primary | available | 8.2 MB | 0.4 s | legal-basis-without-infraction |
| dadosabertos.ibama.gov.br › fiscalizacao-termo-de-apreensao › Termo de apreensão | primary | available | 29.8 MB | 0.4 s | seizure-coordinates-missing-or-zero, seizure-link-without-term, term-without-infraction |
| dadosabertos.ibama.gov.br › fiscalizacao-auto-de-infracao › Autos de infração - espécimes | primary | available | 5.3 MB | 0.4 s | species-without-infraction |
| dadosabertos.ibama.gov.br › ato-declaratorio-ambiental-ada › Ato Declaratório Ambiental (ADA) | primary | available | 401.2 MB | 17.8 s | declared-areas-above-property |
| dadosabertos.ibama.gov.br › licencas-ambientais-de-atividades-e-empreendimentos-licenciados-pelo-ibama › Licenças ambientais de atividades e ... | primary | available | 3.3 MB | 0.2 s | expiry-before-issue, installation-licence-over-six-years, operation-licence-over-ten-years, preliminary-licence-over-five-years |
| dadosabertos.ibama.gov.br › julgamentos-de-auto-de-infracao-realizado-no-ambito-do-ibama › Volume de Julgamento de Auto de Infração | primary | available | 0.6 MB | 0.1 s | appeal-before-main-judgment, main-judgment-before-infraction |
| dadosabertos.ibama.gov.br › arrecadacao-de-multas-ambientais-bens-tutelados › Arrecadação de Multas por Bens Tutelados | primary | available | 27.9 MB | 1.4 s | paid-ten-times-original, payment-before-infraction |
| dadosabertos.ibama.gov.br › relatorios-de-comercializacao-de-agrotoxicos › Dados - CSV | primary | available | 13.6 MB | 0.8 s | ingredient-without-registered-technical-product |
| dados.agricultura.gov.br › sistema-de-agrotoxicos-fitossanitarios-agrofit › Produto Técnico | secondary | available | 0.7 MB | 0.7 s | ingredient-without-registered-technical-product |
| dadosabertos.tse.jus.br › codigos-oficiais-de-uf-e-municipios-segundo-o-tse-e-o-ibge › Códigos oficiais de UF e municípios segundo o TSE e o IBGE | secondary | available | 0.1 MB | 0.3 s | municipality-state |
