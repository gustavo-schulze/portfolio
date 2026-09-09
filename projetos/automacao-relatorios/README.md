# Automação de Relatório Gerencial

> **Projeto demonstrativo** — dados fictícios gerados pelo próprio script.

Transforma um extrato de vendas em CSV numa pasta de trabalho Excel formatada e
pronta para apresentar, sem nenhuma etapa manual.

## O problema

Consolidar vendas por mês, região e categoria costuma ser feito à mão: copiar
CSV, montar tabela dinâmica, formatar, inserir gráfico, repetir todo mês. Uma
hora de trabalho repetitivo e sujeito a erro de digitação.

## A solução

Um script Python que executa em segundos e sempre produz o mesmo layout:

- Lê o CSV detectando o delimitador (`;` ou `,`) e o padrão numérico brasileiro
- Descarta linhas inválidas em vez de quebrar, avisando quantas foram
- Gera **3 abas**:
  - **Resumo** — 4 KPIs, receita por mês e por região, com gráfico de linha e de
    barras nativos do Excel (não são imagens — continuam editáveis)
  - **Consolidado** — região × categoria com ticket médio, participação
    percentual, autofiltro e formatação condicional
  - **Base** — dados normalizados, com filtro e painéis congelados
- Barras de dados na coluna de receita e destaque automático do que passa de 5%
  ou fica abaixo de 1% do total

## Como executar

```bash
pip install openpyxl

python gerar_relatorio.py                    # gera CSV de exemplo + relatório
python gerar_relatorio.py vendas.csv         # usa seu próprio CSV
python gerar_relatorio.py vendas.csv out.xlsx
```

## Formato de entrada

```csv
data;regiao;categoria;produto;quantidade;valor_unitario
2025-03-14;Sudeste;Software;Plataforma BI Pro;3;4820.00
```

`data` em ISO (`AAAA-MM-DD`). Aceita valores com vírgula decimal.

## Resultado

```
Lendo vendas_exemplo.csv ...
  900 registros validos
Relatorio gerado: relatorio_gerencial.xlsx
  3 abas - receita total R$ 24.985.353,47
```

## Stack

Python 3.10+ · openpyxl · biblioteca padrão (`csv`, `collections`, `datetime`)

---

Gustavo Gorges — Soluções em Dados & Tecnologia
[gustavo.gorges007@gmail.com](mailto:gustavo.gorges007@gmail.com) · WhatsApp +55 (47) 99760-5191
