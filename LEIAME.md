# 5LTEP-L2: Kit de Políticas Semânticas da Camada 2 do 5L-TEP

[![Licença: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[English](README.md) · **Português**

**Regras de domínio, escritas por pessoas depois que os dados existem, conferidas em portais de dados abertos.**
A Camada 2 da Pirâmide de Engenharia da Confiança em Cinco Camadas (5L-TEP, SOFTENG 2026) transforma
conhecimento que um esquema não comporta (o código de um município precisa pertencer à UF com que
está pareado; uma licença não pode vencer antes de ser emitida) em arquivos de regra que qualquer
pessoa pode ler, revisar e adaptar a outro portal CKAN.

> **Estado: protótipo inicial de pesquisa.** Este repositório contém, por enquanto, o formato de
> regras 1.0, seu JSON Schema e um validador. O motor que baixa os recursos CKAN e avalia as regras
> já roda localmente; **ainda não há resultados publicados** aqui. As regras são exemplos
> com fundamentos e pendências registrados; não são regras oficiais de nenhum órgão, e um sinal
> futuro será algo a revisar, nunca um veredito sobre os dados.

## Como é uma regra

Cada arquivo em `rules/` contém uma verificação que cruza dados de um ou mais portais **CKAN**.
Arquivo em `rules/` está ativo; as subpastas são livres e só organizam as regras.

| Parte | Para quem | Conteúdo |
|---|---|---|
| `schema_version`, `version`, `origin` | todos | versão do formato, versão da regra, quem a propôs; o nome do arquivo é o identificador da regra |
| `description` | pessoas (dashboard) | título (com tradução opcional em `title_translations`), o que é verificado, justificativa, exceções e exemplos, numa língua declarada por etiqueta BCP 47 |
| `sources` | o motor | para cada recurso CKAN: portal, dataset, nome e formato exatos do recurso, como desempacotar (`archive`), como ler (`file`) e as colunas lidas, cada uma com seu significado |
| `check` | o motor | um modelo permitido e seus parâmetros, escritos como `fonte.coluna` |

Só `sources` e `check` definem o que é calculado. SQL, código ou expressões livres nunca são
aceitos. O exemplo [`rules/territorio/municipio-uf.yaml`](rules/territorio/municipio-uf.yaml)
procura o código do município de cada auto de infração (portal do IBAMA) na tabela de municípios
publicada pelo TSE (portal do TSE) e compara a UF.

## Validar regras

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Linux/macOS: .venv/bin/python
python main.py validate                                   # todos os rules/**/*.yaml
python main.py validate rules/territorio --format json
python -m pytest
python main.py run                                        # ensaio local: baixa as fontes, saídas em work/out
```

O validador informa arquivo, linha, caminho e um código estável para cada problema (mensagens em
português, idioma inicial da interface). Ele confere:

- **YAML 1.2 seguro:** um documento; sem chaves repetidas, âncoras, aliases, chaves de mesclagem ou
  tags explícitas; UTF-8;
- **o esquema** [`schema/rule-v1.schema.json`](schema/rule-v1.schema.json), um arquivo para todas as
  regras: campos obrigatórios, conjuntos fechados de campos e valores, parâmetros de cada modelo;
- **referências cruzadas:** toda `fonte.coluna` usada em `check` está declarada em `sources`; fonte
  ou coluna declarada e não usada gera aviso;
- **nomes de arquivo:** o nome do arquivo é o identificador da regra (minúsculas sem acento, dígitos
  e hífen) e precisa ser único em `rules/`, em qualquer profundidade de subpasta.

## Escrever uma regra

Copie o exemplo, dê a ele um novo nome de arquivo (que é o identificador) e edite. As primeiras regras
estão em português; `description.title_translations` pode trazer o título em outras línguas
(`en: "..."`), e o dashboard em inglês mostra essa versão quando existe, senão o título original. Os nomes exatos do dataset e do
recurso estão em `<portal>/api/3/action/package_show?id=<dataset>`; baixe o arquivo uma vez para
conferir o conteúdo do zip, a codificação, o separador e os cabeçalhos. Ponha versões e códigos
entre aspas. A versão 1.0 especifica um modelo, `lookup-equals`; outros modelos entram no mesmo
esquema conforme ganharem contrato de parâmetros.

Opcional, por editor: o VS Code com a extensão YAML lê [`.vscode/settings.json`](.vscode/settings.json),
que liga o esquema a todo `rules/**/*.yaml` e oferece autocompletar e conferência imediata. Em outros
editores, ligue o mesmo esquema ao mesmo padrão (JetBrains: *JSON Schema Mappings*; Neovim, Helix,
Zed: configuração do `yaml-language-server`). Nada nos arquivos de regra depende do editor.

## Organização do repositório

```
main.py            linha de comando (validate, run)
src/loader.py      leitura segura do YAML, com números de linha
src/validate.py    esquema e referências cruzadas
src/fetch.py       resolução e download no CKAN, com integridade de cada fonte
src/engine.py      leitura das colunas declaradas, DuckDB, modelos
src/outputs.py     results/ e docs/data/ (só contagens e números de registro)
src/accept.py      conferência do artefato da rodada pelo job de publicação
docs/              dashboard (index.html, app.js, style.css; data/ é gravado pelas rodadas)
.github/workflows/ layer2.yml (rodada semanal), tests.yml
schema/            JSON Schema do formato de autoria
rules/             um arquivo por regra, agrupado por espaço de nomes
tests/             testes automáticos
```

## Como funciona uma rodada

`.github/workflows/layer2.yml` roda toda quarta-feira às 04:30 UTC (ou manualmente). O job
**evaluate**, com token só de leitura, baixa cada recurso CKAN uma vez, registra se cada portal e
recurso estava disponível (status HTTP, SHA-256 dos bytes, colunas encontradas), cruza os dados com
DuckDB sem acesso externo e envia as saídas como artefato. O job **publish** confere o artefato
(`python main.py accept`: só os arquivos esperados, JSON válido, listas só com números de registro,
histórico anterior preservado) e faz o commit de `results/` e `docs/data/`. O dashboard em `docs/`
(GitHub Pages a partir de `/docs`) mostra as regras, a saúde de cada fonte, o histórico e a
proveniência; cada visitante pode ordenar os cartões de regras, e essa ordem fica só no navegador
dele. Só são publicadas contagens e números de registro, nunca valores dos portais.

## Próximos passos

Formulários de issue para quem não escreve YAML, mais modelos e as instâncias de controle da ANEEL e
da Prefeitura do Recife.

## Licença e citação

Código sob a [Licença MIT](LICENSE). Metadados de citação em [`CITATION.cff`](CITATION.cff).
