# 5LTEP-L2: Kit de Políticas Semânticas da Camada 2 do 5L-TEP

[![Licença: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[English](README.md) · **Português**

**Regras de domínio, escritas por pessoas depois que os dados existem, conferidas em portais de dados abertos.**
A Camada 2 da Pirâmide de Engenharia da Confiança em Cinco Camadas (5L-TEP, SOFTENG 2026) transforma
conhecimento que um esquema não comporta (o código de um município precisa pertencer à UF com que
está pareado; uma licença não pode vencer antes de ser emitida) em arquivos de regra que qualquer
pessoa pode ler, revisar e adaptar a outro portal CKAN.

> **Estado: protótipo inicial de pesquisa.** Este repositório contém, por enquanto, o formato de
> autoria de regras 1.0, seu JSON Schema e um validador. O motor que resolve recursos CKAN e avalia
> as regras ainda não foi implementado; portanto, **não há resultados** aqui. As regras são exemplos
> com fundamentos e pendências registrados; não são regras oficiais de nenhum órgão, e um sinal
> futuro será algo a revisar, nunca um veredito sobre os dados.

## Como é uma regra

Cada arquivo contém uma verificação atômica, em três partes:

| Parte | Para quem | Conteúdo |
|---|---|---|
| `description` | pessoas | intenção, justificativa, significado de cada coluna, exceções, exemplos e fontes, em qualquer língua declarada por etiqueta BCP 47 |
| `classification` | resumos e exportação | forma da checagem (`AR`, `TC`, `DC`, `DM`), áreas de conhecimento, severidade, dimensão de qualidade, natureza do limite |
| `execution` | o motor | um modelo permitido e seus parâmetros, aplicado a portais, conjuntos, recursos e cabeçalhos exatos |

Só `execution` define o que é calculado. SQL, código ou expressões livres nunca são aceitos: a regra
preenche os parâmetros de um modelo que o motor implementa. Uma aplicação fica `pending_mapping` até
uma pessoa confirmar o significado de suas colunas; entrada ausente, referência sem correspondência
ou coluna ausente são registradas como indeterminadas ou inaplicáveis, nunca como aprovação.

O exemplo [`rules/territory/territory.municipality-state.yaml`](rules/territory/territory.municipality-state.yaml)
confere se o código IBGE do município começa pelo código da UF com que está pareado, quando ambos
descrevem o mesmo lugar.

## Validar regras

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Linux/macOS: .venv/bin/python
python main.py validate                                   # todos os rules/**/*.yaml
python main.py validate rules/territory --format json
python -m pytest
```

O validador informa arquivo, linha, caminho e um código estável para cada problema (mensagens em
português, idioma inicial da interface). Ele confere:

- **YAML 1.2 seguro:** um documento; sem chaves repetidas, âncoras, aliases, chaves de mesclagem ou
  tags explícitas; UTF-8;
- **o esquema** [`schema/rule-v1.schema.json`](schema/rule-v1.schema.json): campos obrigatórios,
  conjuntos fechados de campos e valores, parâmetros de cada modelo;
- **referências cruzadas:** toda fonte e coluna citada por parâmetros, identidade e significado dos
  campos está declarada na mesma aplicação; coluna declarada e não usada gera aviso;
- **habilitação:** aplicação `enabled` exige revisão do mapeamento confirmada e referências
  preparadas (versão, SHA-256, licença, cobertura);
- **padrões:** `pattern` fica num subconjunto de I-Regexp (RFC 9485) e casa com o valor inteiro;
- **pastas:** um `<id>.yaml` por regra e ids únicos.

## Escrever uma regra

Copie o exemplo, dê a ele novo `id` e novo nome de arquivo, e edite. Editores que usam o YAML
language server (o VS Code com a extensão YAML, por exemplo) leem a primeira linha do exemplo e
oferecem autocompletar e conferência imediata a partir do esquema. Ponha datas, versões e códigos
entre aspas. A versão 1.0 especifica um modelo, `hierarchical-code`; as demais famílias candidatas
precisam de contrato de parâmetros próprio antes de uma regra poder usá-las.

## Organização do repositório

```
main.py            linha de comando (validate)
src/loader.py      leitura segura do YAML, com números de linha
src/validate.py    esquema, referências cruzadas e subconjunto de padrões
schema/            JSON Schema do formato de autoria
rules/             um arquivo por regra, agrupado por espaço de nomes
tests/             testes automáticos
```

## Próximos passos

Previsto, não implementado: resolução de recursos CKAN por seletores explícitos, preparação de
referências versionadas, avaliação com DuckDB sem acesso externo, prévia determinística do que cada
aplicação vai calcular, logs estruturados e manifesto da rodada, formulários de issue para quem não
escreve YAML, e as instâncias de controle da ANEEL e da Prefeitura do Recife.

## Licença e citação

Código sob a [Licença MIT](LICENSE). Metadados de citação em [`CITATION.cff`](CITATION.cff).
