"""
Monitor de precos com web scraping.

Coleta catalogo de produtos (titulo, preco, disponibilidade, avaliacao),
compara com a coleta anterior e reporta variacoes de preco, entradas e saidas
de catalogo. Exporta CSV e um resumo em JSON.

Alvo padrao: books.toscrape.com - site publico mantido justamente para
treino de scraping, com permissao explicita de uso.

Projeto demonstrativo - Gustavo Gorges
Solucoes em Dados & Tecnologia

Uso:
    python monitor_precos.py                 # coleta 3 paginas
    python monitor_precos.py --paginas 10
    python monitor_precos.py --paginas 5 --saida catalogo.csv

Sem dependencias externas: usa apenas a biblioteca padrao do Python.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from html.parser import HTMLParser
from html import unescape

BASE = "https://books.toscrape.com/catalogue/page-{}.html"
UA = "Mozilla/5.0 (compatible; MonitorPrecos/1.0; +portfolio-demo)"

ESTRELAS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


# ------------------------------------------------------------------ scraping

class ParserCatalogo(HTMLParser):
    """Extrai os cards de produto da listagem.

    Estrutura alvo:
        <article class="product_pod">
          <p class="star-rating Three">
          <h3><a title="Titulo do livro" href="...">
          <p class="price_color">GBP 51.77</p>
          <p class="instock availability"> In stock </p>
        </article>
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.itens: list[dict] = []
        self._atual: dict | None = None
        self._captura: str | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()

        if tag == "article" and "product_pod" in classes:
            self._atual = {"titulo": "", "preco": None, "disponivel": False, "estrelas": 0}

        if self._atual is None:
            return

        if tag == "p" and "star-rating" in classes:
            for c in classes:
                if c in ESTRELAS:
                    self._atual["estrelas"] = ESTRELAS[c]

        elif tag == "a" and a.get("title"):
            if not self._atual["titulo"]:
                self._atual["titulo"] = unescape(a["title"]).strip()

        elif tag == "p" and "price_color" in classes:
            self._captura = "preco"

        elif tag == "p" and "availability" in classes:
            self._captura = "disp"
            self._atual["disponivel"] = "instock" in classes

    def handle_data(self, data):
        if self._atual is None or not self._captura:
            return
        texto = data.strip()
        if not texto:
            return
        if self._captura == "preco":
            m = re.search(r"(\d+[.,]\d{2})", texto)
            if m:
                self._atual["preco"] = float(m.group(1).replace(",", "."))
            self._captura = None
        elif self._captura == "disp":
            self._captura = None

    def handle_endtag(self, tag):
        if tag == "article" and self._atual is not None:
            if self._atual["titulo"] and self._atual["preco"] is not None:
                self.itens.append(self._atual)
            self._atual = None
            self._captura = None


def baixar(url: str, tentativas: int = 3, espera: float = 1.5) -> str | None:
    """GET com retry e backoff. Devolve None se a pagina nao existir."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for n in range(1, tentativas + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None                      # fim da paginacao
            if n == tentativas:
                print(f"  erro HTTP {e.code} em {url}")
                return None
        except (urllib.error.URLError, TimeoutError) as e:
            if n == tentativas:
                print(f"  falha de rede em {url}: {e}")
                return None
        time.sleep(espera * n)                   # backoff progressivo
    return None


def coletar(paginas: int, intervalo: float = 1.0) -> list[dict]:
    catalogo: list[dict] = []
    for p in range(1, paginas + 1):
        url = BASE.format(p)
        print(f"  pagina {p}/{paginas} ...", end=" ", flush=True)
        html = baixar(url)
        if html is None:
            print("indisponivel - encerrando paginacao")
            break
        parser = ParserCatalogo()
        parser.feed(html)
        for item in parser.itens:
            item["pagina"] = p
        catalogo.extend(parser.itens)
        print(f"{len(parser.itens)} produtos")
        if p < paginas:
            time.sleep(intervalo)                # educado com o servidor
    return catalogo


# ---------------------------------------------------------------- comparacao

def comparar(atual: list[dict], anterior: list[dict]) -> dict:
    """Diferenca entre duas coletas, chaveada pelo titulo do produto."""
    ant = {i["titulo"]: i for i in anterior}
    atu = {i["titulo"]: i for i in atual}

    variacoes = []
    for titulo, item in atu.items():
        if titulo in ant and ant[titulo]["preco"] != item["preco"]:
            antes = ant[titulo]["preco"]
            variacoes.append({
                "titulo": titulo,
                "de": antes,
                "para": item["preco"],
                "variacao_pct": round((item["preco"] / antes - 1) * 100, 2),
            })
    variacoes.sort(key=lambda v: abs(v["variacao_pct"]), reverse=True)

    return {
        "novos": sorted(set(atu) - set(ant)),
        "removidos": sorted(set(ant) - set(atu)),
        "variacoes": variacoes,
    }


# ------------------------------------------------------------------- saidas

def salvar_csv(catalogo: list[dict], caminho: str) -> None:
    with open(caminho, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(
            fh, delimiter=";",
            fieldnames=["titulo", "preco", "disponivel", "estrelas", "pagina"],
        )
        w.writeheader()
        for item in sorted(catalogo, key=lambda i: i["preco"], reverse=True):
            w.writerow(item)


def resumo(catalogo: list[dict], diff: dict | None) -> dict:
    precos = [i["preco"] for i in catalogo]
    caro = max(catalogo, key=lambda i: i["preco"])
    barato = min(catalogo, key=lambda i: i["preco"])
    return {
        "coletado_em": datetime.now().isoformat(timespec="seconds"),
        "total_produtos": len(catalogo),
        "disponiveis": sum(1 for i in catalogo if i["disponivel"]),
        "preco_medio": round(sum(precos) / len(precos), 2),
        "preco_min": barato["preco"],
        "preco_max": caro["preco"],
        "mais_caro": caro["titulo"],
        "mais_barato": barato["titulo"],
        "media_estrelas": round(sum(i["estrelas"] for i in catalogo) / len(catalogo), 2),
        "comparacao": diff,
    }


# --------------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Monitor de precos por web scraping")
    ap.add_argument("--paginas", type=int, default=3, help="paginas a coletar (padrao: 3)")
    ap.add_argument("--saida", default="catalogo.csv", help="arquivo CSV de saida")
    ap.add_argument("--intervalo", type=float, default=1.0,
                    help="segundos entre requisicoes (padrao: 1.0)")
    args = ap.parse_args(argv[1:])

    aqui = os.path.dirname(os.path.abspath(__file__))
    csv_saida = args.saida if os.path.isabs(args.saida) else os.path.join(aqui, args.saida)
    json_saida = os.path.join(aqui, "resumo.json")

    # coleta anterior, para comparar
    anterior: list[dict] = []
    if os.path.exists(csv_saida):
        with open(csv_saida, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh, delimiter=";"):
                try:
                    anterior.append({"titulo": r["titulo"], "preco": float(r["preco"])})
                except (ValueError, KeyError):
                    continue

    print(f"Coletando {args.paginas} pagina(s) de {BASE.split('/catalogue')[0]} ...")
    catalogo = coletar(args.paginas, args.intervalo)

    if not catalogo:
        print("Nenhum produto coletado - verifique a conexao.")
        return 1

    diff = comparar(catalogo, anterior) if anterior else None
    salvar_csv(catalogo, csv_saida)

    info = resumo(catalogo, diff)
    with open(json_saida, "w", encoding="utf-8") as fh:
        json.dump(info, fh, ensure_ascii=False, indent=2)

    print()
    print(f"{info['total_produtos']} produtos | {info['disponiveis']} disponiveis")
    print(f"Preco medio GBP {info['preco_medio']:.2f} "
          f"(min {info['preco_min']:.2f} / max {info['preco_max']:.2f})")
    print(f"Mais caro: {info['mais_caro'][:52]}")

    if diff:
        print()
        print(f"Comparado a coleta anterior: {len(diff['variacoes'])} mudanca(s) de preco, "
              f"{len(diff['novos'])} novo(s), {len(diff['removidos'])} removido(s)")
        for v in diff["variacoes"][:5]:
            seta = "alta" if v["variacao_pct"] > 0 else "queda"
            print(f"  {seta:5} {v['variacao_pct']:+6.2f}%  {v['titulo'][:44]}")

    print()
    print(f"CSV:  {os.path.basename(csv_saida)}")
    print(f"JSON: {os.path.basename(json_saida)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
