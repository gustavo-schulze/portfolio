# Monitor de Preços — Web Scraping

> **Projeto demonstrativo.** Coleta de [books.toscrape.com](https://books.toscrape.com),
> site público mantido justamente para treino de scraping.

Monitora um catálogo de produtos, compara com a coleta anterior e reporta
variações de preço, entradas e saídas de catálogo.

## O problema

Acompanhar preço de concorrente ou de fornecedor na mão não escala: abrir
dezenas de páginas, anotar valores numa planilha, comparar com a semana
passada. Ninguém sustenta isso por muito tempo.

## A solução

Um script que coleta, compara e reporta — **sem nenhuma dependência externa**,
só a biblioteca padrão do Python:

- Parser HTML próprio sobre `html.parser` (sem BeautifulSoup, sem requests)
- **Retry com backoff progressivo** e detecção de fim de paginação via 404
- Intervalo configurável entre requisições, para não sobrecarregar o servidor
- **Comparação com a coleta anterior**: lê o CSV que ele mesmo gravou e calcula
  a variação percentual por produto, ordenada por relevância
- Saída em CSV (`;`, UTF-8 com BOM — abre direto no Excel brasileiro) e um
  `resumo.json` com as estatísticas do período

## Como executar

```bash
python monitor_precos.py                     # 3 páginas
python monitor_precos.py --paginas 10
python monitor_precos.py --paginas 5 --intervalo 2.0 --saida catalogo.csv
```

Rode duas vezes para ver a comparação entre coletas.

## Resultado

```
Coletando 3 pagina(s) de https://books.toscrape.com ...
  pagina 1/3 ... 20 produtos
  pagina 2/3 ... 20 produtos
  pagina 3/3 ... 20 produtos

60 produtos | 60 disponiveis
Preco medio GBP 35.00 (min 12.84 / max 57.31)
Mais caro: Slow States of Collapse: Poems

CSV:  catalogo.csv
JSON: resumo.json
```

## Dados extraídos

| Campo | Descrição |
|---|---|
| `titulo` | Nome do produto |
| `preco` | Valor numérico já convertido |
| `disponivel` | Booleano, lido da classe de estoque |
| `estrelas` | Avaliação 1–5, traduzida da classe CSS |
| `pagina` | Página de origem na paginação |

## Nota sobre uso responsável

O alvo é um site feito para praticar scraping. Em produção, respeite sempre o
`robots.txt`, os termos de uso do site e limite a frequência das requisições.

## Stack

Python 3.10+ · `urllib` · `html.parser` · `csv` · `json` · `argparse`

---

Gustavo Gorges — Soluções em Dados & Tecnologia
[gustavo.gorges007@gmail.com](mailto:gustavo.gorges007@gmail.com) · WhatsApp +55 (47) 99760-5191
