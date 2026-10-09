# 5LTEP-L2: Kit de Políticas Semânticas da Camada 2 do 5L-TEP

[![Testes](https://github.com/lsp3cesarschool/5ltep-layer2/actions/workflows/tests.yml/badge.svg)](https://github.com/lsp3cesarschool/5ltep-layer2/actions/workflows/tests.yml) [![Camada 2](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Flsp3cesarschool%2F5ltep-layer2%2Fmain%2Fdocs%2Fdata%2Fstatus.pt.json)](https://github.com/lsp3cesarschool/5ltep-layer2/actions/workflows/layer2.yml) [![Licença: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[English](README.md) · **Português**

**35 regras de domínio que cruzam portais de dados abertos CKAN, aplicadas ao portal do IBAMA, o
órgão ambiental federal.** As regras são escritas por pessoas depois que os dados são publicados,
uma verificação por arquivo. Toda semana o motor desta camada avalia cada regra: lê os arquivos
publicados, sinaliza os registros que merecem um segundo olhar e os mostra num dashboard. Um sinal é
um convite à revisão, nunca um veredito sobre os dados.

| Recurso | O que há lá |
|---|---|
| 📊 **Dashboard** | [lsp3cesarschool.github.io/5ltep-layer2](https://lsp3cesarschool.github.io/5ltep-layer2/?lang=pt): cada regra com seus sinais, gráficos e números de registro; saúde das fontes, velocidade de download e de processamento, histórico e proveniência |
| 📏 **Regras** | [`rules/`](rules/): uma verificação por arquivo, em YAML legível |
| 📁 **Resultados** | [`results/`](results/) e [`docs/data/`](docs/data/): o que cada rodada grava (contagens, números de registro, hashes) |
| 🔁 **Experimentos de controle** | [5ltep-layer2-aneel](https://github.com/lsp3cesarschool/5ltep-layer2-aneel) ([dashboard](https://lsp3cesarschool.github.io/5ltep-layer2-aneel/?lang=pt)) e [5ltep-layer2-recife](https://github.com/lsp3cesarschool/5ltep-layer2-recife) ([dashboard](https://lsp3cesarschool.github.io/5ltep-layer2-recife/?lang=pt)): o mesmo código nos portais da ANEEL e da Prefeitura do Recife |

> **Estado: demonstração de pesquisa.** Este repositório faz parte de um projeto de mestrado e é
> mantido pelo autor. Não é operado, afiliado nem endossado pelo IBAMA nem por outro publicador;
> só lê dados abertos de portais CKAN. As regras são exemplos escritos pelo autor.

## Caso de uso em um parágrafo

Uma pesquisadora quer mapear as infrações ambientais por município a partir dos autos de infração do
IBAMA. Cada auto traz um código de município e uma UF, e o mapa parte do princípio de que os dois
concordam. Uma regra deste repositório pega cada código, procura-o na tabela de municípios que o TSE
publica no próprio portal CKAN e compara a UF. Outras regras conferem se as datas do auto seguem uma
ordem plausível, se a coordenada não está ausente nem em (0,0), se os registros vinculados existem
nos outros extratos e se alguma licença CITES combina Apêndice I, origem silvestre e finalidade
comercial. Antes de desenhar o mapa, a pesquisadora abre o dashboard e vê quais registros merecem um
segundo olhar, em que arquivo e em que linha, sem que este repositório publique nenhum dos valores
deles.

## Termos-chave

| Termo | Significado aqui |
|---|---|
| **Regra** | Um arquivo YAML em `rules/` com uma descrição para pessoas e uma verificação para o motor. Todo arquivo em `rules/` está ativo; as subpastas só organizam. |
| **Fonte** | O recurso CKAN que a regra lê (portal, dataset, nome e formato exatos do recurso), ou vários recursos de um dataset reunidos por um padrão de nome, junto com o modo de abrir o arquivo e as colunas a ler. |
| **Modelo** | A verificação fixa que a regra preenche: `lookup-equals`, `lookup-exists`, `temporal-order`, `field-comparison` ou `flag-when`. Regras nunca contêm SQL nem código. |
| **Sinal** | Registro que não passou na verificação ou que não pôde ser verificado (valor ausente ou ilegível, chave não encontrada). Algo a revisar, não um veredito. |
| **Número de registro** | A linha do registro no arquivo publicado (1 é a primeira linha após o cabeçalho), válida para os bytes cujo SHA-256 a rodada registra. |
| **Saúde das fontes** | Se cada portal respondeu e cada recurso foi baixado durante a rodada. Regra com fonte em falha fica "não avaliada"; nunca é avaliada pela metade. |

## Como é uma regra

```
schema_version: "1.0"
rule_version: "0.3.0"
origin: cross_reference
description:  {language, title, text, justification, exceptions, examples}
sources:      {name: {portal, dataset, resource, archive, file, columns}}
check:        {template, parameters, where, timeline}
```

O nome do arquivo é o identificador da regra. Um único contrato,
[`schema/rule-v1.schema.json`](schema/rule-v1.schema.json), descreve o formato de todas as regras, e
`python main.py validate` confere cada arquivo com ele e verifica se toda coluna usada pela
verificação foi declarada. O manual de regras do repositório principal explica cada campo.

## Como funciona uma rodada

[`.github/workflows/layer2.yml`](.github/workflows/layer2.yml) roda toda quarta-feira às 04:30 UTC e
também pode ser disparado manualmente. O job **evaluate**, que tem token só de leitura, baixa cada
recurso CKAN uma única vez, não importa quantas regras o usem, e registra se cada portal e recurso
estava disponível. Em seguida lê só as colunas declaradas, avalia cada regra com DuckDB sem acesso
externo e envia as saídas como artefato. O job **publish** confere esse artefato com `python main.py
accept` (só os arquivos esperados, JSON válido, listas compostas só de números, histórico anterior
preservado) e faz o commit de `results/` e `docs/data/`. Cada rodada registra também a velocidade de
download deste portal e dos demais, e quanto tempo levou cada etapa.

## Tratamento de dados e privacidade

Este repositório foi desenhado para respeitar a Lei Geral de Proteção de Dados (LGPD, Lei
13.709/2018), inclusive sobre dados que os portais já publicam abertamente. Na prática: Os arquivos
são baixados durante a rodada e apagados quando ela termina; no GitHub, o próprio runner é
descartado depois do job. O motor lê só as colunas que a regra declara e publica apenas contagens,
números de registro, hashes SHA-256 e metadados que o CKAN já publica, nunca um valor lido dos
portais. Regras sobre dados de saúde ou educação usam `exposure: counts`, e por isso publicam
contagens e gráficos, mas não números de registro. Os datasets mantêm as licenças de seus
publicadores, que o dashboard lista com link.

## Como rodar localmente

```
python -m pip install -r requirements.txt
python main.py validate
python -m pytest
python main.py run        # ensaio local: baixa as fontes, saídas em work/out
```

Rodada local é só ensaio: os resultados publicados vêm apenas do GitHub Actions.

## Organização do repositório

```
main.py            linha de comando (validate, run, accept)
src/               leitor, validador, modelos, download, motor, saídas, aceite
schema/            JSON Schema do formato de regra
rules/             um arquivo por regra, em subpastas
portal.json        o portal desta instância
docs/              dashboard (data/ é gravado pelas rodadas)
results/           resultados das rodadas
tests/             testes automáticos
```

## Licença e citação

O código está sob a [Licença MIT](LICENSE). Os metadados de citação estão em
[`CITATION.cff`](CITATION.cff).

