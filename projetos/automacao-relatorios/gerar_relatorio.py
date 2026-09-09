"""
Automacao de relatorio gerencial em Excel.

Le um extrato de vendas em CSV, consolida por mes/regiao/categoria e gera uma
pasta de trabalho .xlsx formatada com aba de resumo, tabela dinamica de apoio,
formatacao condicional e grafico nativo do Excel.

Projeto demonstrativo - Gustavo Gorges
Solucoes em Dados & Tecnologia

Uso:
    python gerar_relatorio.py                      # gera dados de exemplo e o relatorio
    python gerar_relatorio.py vendas.csv           # usa um CSV proprio
    python gerar_relatorio.py vendas.csv saida.xlsx

CSV esperado (cabecalho obrigatorio):
    data,regiao,categoria,produto,quantidade,valor_unitario

Requisitos: openpyxl >= 3.1
"""

from __future__ import annotations

import csv
import os
import random
import sys
from collections import defaultdict
from datetime import date, timedelta

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import CellIsRule, DataBarRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------- identidade

AZUL_ESCURO = "0C1F34"
AZUL = "38BDF8"
CINZA = "F2F5F8"
VERDE = "22C55E"
VERMELHO = "F87171"

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
         "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

FINO = Side(style="thin", color="D6DEE7")
BORDA = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)


# ------------------------------------------------------------------- entrada

def gerar_csv_exemplo(caminho: str, n: int = 900) -> str:
    """Cria um CSV de vendas ficticio para quem so quer ver a automacao rodando."""
    regioes = ["Sul", "Sudeste", "Centro-Oeste", "Nordeste", "Norte"]
    categorias = {
        "Software": (1200, 9800),
        "Consultoria": (2500, 18000),
        "Licencas": (400, 3200),
        "Suporte": (300, 2400),
        "Treinamento": (600, 4500),
    }
    produtos = {
        "Software": ["Plataforma BI Pro", "Conector API", "Modulo Fiscal"],
        "Consultoria": ["Consultoria de Dados", "Automacao de Processos"],
        "Licencas": ["Licenca Anual ERP", "Licenca Office"],
        "Suporte": ["Suporte Premium", "Suporte Basico"],
        "Treinamento": ["Treinamento Power BI", "Treinamento Excel"],
    }

    rng = random.Random(42)  # semente fixa: mesmo arquivo a cada execucao
    inicio = date(date.today().year, 1, 1)

    with open(caminho, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["data", "regiao", "categoria", "produto",
                    "quantidade", "valor_unitario"])
        for _ in range(n):
            cat = rng.choice(list(categorias))
            lo, hi = categorias[cat]
            w.writerow([
                (inicio + timedelta(days=rng.randint(0, 364))).isoformat(),
                rng.choices(regioes, weights=[20, 34, 14, 20, 12])[0],
                cat,
                rng.choice(produtos[cat]),
                rng.randint(1, 12),
                round(rng.uniform(lo, hi), 2),
            ])
    return caminho


def detectar_delimitador(caminho: str) -> str:
    with open(caminho, "r", encoding="utf-8-sig") as fh:
        amostra = fh.readline()
    return ";" if amostra.count(";") > amostra.count(",") else ","


def ler_vendas(caminho: str) -> list[dict]:
    """Le o CSV e devolve linhas normalizadas, ignorando registros invalidos."""
    delim = detectar_delimitador(caminho)
    linhas: list[dict] = []
    descartadas = 0

    with open(caminho, "r", encoding="utf-8-sig", newline="") as fh:
        for i, reg in enumerate(csv.DictReader(fh, delimiter=delim), start=2):
            try:
                d = date.fromisoformat(reg["data"].strip()[:10])
                qtd = int(float(str(reg["quantidade"]).replace(",", ".")))
                vu = float(str(reg["valor_unitario"]).replace(".", "").replace(",", ".")) \
                    if "," in str(reg["valor_unitario"]) \
                    else float(reg["valor_unitario"])
            except (ValueError, KeyError, TypeError, AttributeError):
                descartadas += 1
                continue

            linhas.append({
                "data": d,
                "mes": d.month,
                "regiao": (reg.get("regiao") or "Nao informado").strip(),
                "categoria": (reg.get("categoria") or "Nao informado").strip(),
                "produto": (reg.get("produto") or "Nao informado").strip(),
                "quantidade": qtd,
                "receita": round(qtd * vu, 2),
            })

    if descartadas:
        print(f"  aviso: {descartadas} linha(s) descartada(s) por dado invalido")
    if not linhas:
        raise SystemExit("Nenhuma linha valida encontrada no CSV.")
    return linhas


# ----------------------------------------------------------------- formatacao

def estilo_cabecalho(ws, linha: int, primeira: int, ultima: int) -> None:
    for c in range(primeira, ultima + 1):
        cel = ws.cell(row=linha, column=c)
        cel.font = Font(bold=True, color="FFFFFF", size=10)
        cel.fill = PatternFill("solid", fgColor=AZUL_ESCURO)
        cel.alignment = Alignment(horizontal="center", vertical="center",
                                  wrap_text=True)
        cel.border = BORDA
    ws.row_dimensions[linha].height = 26


def largura_automatica(ws, minimo: int = 10, maximo: int = 42) -> None:
    for col in ws.columns:
        letra = get_column_letter(col[0].column)
        maior = max((len(str(c.value)) for c in col if c.value is not None),
                    default=0)
        ws.column_dimensions[letra].width = max(minimo, min(maximo, maior + 3))


# -------------------------------------------------------------------- abas

def aba_resumo(wb: Workbook, dados: list[dict], origem: str) -> None:
    ws = wb.active
    ws.title = "Resumo"
    ws.sheet_view.showGridLines = False

    receita = sum(d["receita"] for d in dados)
    pedidos = len(dados)
    itens = sum(d["quantidade"] for d in dados)

    ws["B2"] = "RELATORIO GERENCIAL DE VENDAS"
    ws["B2"].font = Font(bold=True, size=17, color=AZUL_ESCURO)
    ws["B3"] = f"Fonte: {os.path.basename(origem)}  |  Gerado automaticamente em {date.today().strftime('%d/%m/%Y')}"
    ws["B3"].font = Font(size=9.5, color="6B7A8C")

    kpis = [
        ("Receita total", receita, '"R$" #,##0.00'),
        ("Pedidos", pedidos, "#,##0"),
        ("Itens vendidos", itens, "#,##0"),
        ("Ticket medio", receita / pedidos, '"R$" #,##0.00'),
    ]
    for i, (rot, val, fmt) in enumerate(kpis):
        col = 2 + i * 2
        rc, vc = ws.cell(row=5, column=col), ws.cell(row=6, column=col)
        ws.merge_cells(start_row=5, start_column=col, end_row=5, end_column=col + 1)
        ws.merge_cells(start_row=6, start_column=col, end_row=6, end_column=col + 1)
        rc.value = rot.upper()
        rc.font = Font(bold=True, size=9, color="FFFFFF")
        rc.fill = PatternFill("solid", fgColor=AZUL_ESCURO)
        rc.alignment = Alignment(horizontal="center")
        vc.value = val
        vc.number_format = fmt
        vc.font = Font(bold=True, size=15, color=AZUL_ESCURO)
        vc.fill = PatternFill("solid", fgColor=CINZA)
        vc.alignment = Alignment(horizontal="center")
    ws.row_dimensions[6].height = 30

    # --- receita por mes (base do grafico de linha)
    por_mes = defaultdict(float)
    for d in dados:
        por_mes[d["mes"]] += d["receita"]

    ws["B9"] = "Receita por mes"
    ws["B9"].font = Font(bold=True, size=11, color=AZUL_ESCURO)
    ws["B10"], ws["C10"] = "Mes", "Receita"
    estilo_cabecalho(ws, 10, 2, 3)
    for i in range(1, 13):
        ws.cell(row=10 + i, column=2, value=MESES[i - 1]).border = BORDA
        c = ws.cell(row=10 + i, column=3, value=round(por_mes.get(i, 0.0), 2))
        c.number_format = '"R$" #,##0.00'
        c.border = BORDA

    linha = LineChart()
    linha.title = "Evolucao mensal da receita"
    linha.height, linha.width = 7.6, 15.5
    linha.y_axis.numFmt = '"R$" #,##0'
    linha.add_data(Reference(ws, min_col=3, min_row=10, max_row=22), titles_from_data=True)
    linha.set_categories(Reference(ws, min_col=2, min_row=11, max_row=22))
    ws.add_chart(linha, "E9")

    # --- receita por regiao (base do grafico de barras)
    por_reg = defaultdict(float)
    for d in dados:
        por_reg[d["regiao"]] += d["receita"]
    reg_ord = sorted(por_reg.items(), key=lambda kv: kv[1], reverse=True)

    ws["B25"] = "Receita por regiao"
    ws["B25"].font = Font(bold=True, size=11, color=AZUL_ESCURO)
    ws["B26"], ws["C26"] = "Regiao", "Receita"
    estilo_cabecalho(ws, 26, 2, 3)
    for i, (reg, val) in enumerate(reg_ord, start=27):
        ws.cell(row=i, column=2, value=reg).border = BORDA
        c = ws.cell(row=i, column=3, value=round(val, 2))
        c.number_format = '"R$" #,##0.00'
        c.border = BORDA

    fim = 26 + len(reg_ord)
    ws.conditional_formatting.add(
        f"C27:C{fim}",
        DataBarRule(start_type="min", end_type="max", color=AZUL,
                    showValue=True, minLength=None, maxLength=None),
    )

    barras = BarChart()
    barras.type, barras.title = "bar", "Receita por regiao"
    barras.height, barras.width = 7.6, 15.5
    barras.add_data(Reference(ws, min_col=3, min_row=26, max_row=fim), titles_from_data=True)
    barras.set_categories(Reference(ws, min_col=2, min_row=27, max_row=fim))
    ws.add_chart(barras, "E25")

    largura_automatica(ws)
    ws.column_dimensions["A"].width = 2.5


def aba_detalhe(wb: Workbook, dados: list[dict]) -> None:
    """Consolidado por regiao x categoria, com participacao e destaque."""
    ws = wb.create_sheet("Consolidado")
    ws.sheet_view.showGridLines = False

    agreg = defaultdict(lambda: {"receita": 0.0, "qtd": 0, "pedidos": 0})
    for d in dados:
        k = (d["regiao"], d["categoria"])
        agreg[k]["receita"] += d["receita"]
        agreg[k]["qtd"] += d["quantidade"]
        agreg[k]["pedidos"] += 1

    total = sum(v["receita"] for v in agreg.values())

    cabecalhos = ["Regiao", "Categoria", "Pedidos", "Itens",
                  "Receita", "Ticket medio", "% do total"]
    for i, h in enumerate(cabecalhos, start=1):
        ws.cell(row=1, column=i, value=h)
    estilo_cabecalho(ws, 1, 1, len(cabecalhos))
    ws.freeze_panes = "A2"

    for r, ((reg, cat), v) in enumerate(
        sorted(agreg.items(), key=lambda kv: kv[1]["receita"], reverse=True), start=2
    ):
        vals = [reg, cat, v["pedidos"], v["qtd"], round(v["receita"], 2),
                round(v["receita"] / v["pedidos"], 2), v["receita"] / total]
        for i, val in enumerate(vals, start=1):
            c = ws.cell(row=r, column=i, value=val)
            c.border = BORDA
            if i in (5, 6):
                c.number_format = '"R$" #,##0.00'
            elif i == 7:
                c.number_format = "0.0%"
            elif i in (3, 4):
                c.number_format = "#,##0"

    ultima = 1 + len(agreg)
    ws.auto_filter.ref = f"A1:G{ultima}"

    # verde no que esta acima de 5% do total, vermelho abaixo de 1%
    ws.conditional_formatting.add(
        f"G2:G{ultima}",
        CellIsRule(operator="greaterThan", formula=["0.05"],
                   font=Font(bold=True, color="0F7B3C"),
                   fill=PatternFill("solid", fgColor="E4F7EC")),
    )
    ws.conditional_formatting.add(
        f"G2:G{ultima}",
        CellIsRule(operator="lessThan", formula=["0.01"],
                   font=Font(color="B3261E")),
    )

    largura_automatica(ws)


def aba_base(wb: Workbook, dados: list[dict]) -> None:
    ws = wb.create_sheet("Base")
    cabecalhos = ["Data", "Mes", "Regiao", "Categoria",
                  "Produto", "Quantidade", "Receita"]
    for i, h in enumerate(cabecalhos, start=1):
        ws.cell(row=1, column=i, value=h)
    estilo_cabecalho(ws, 1, 1, len(cabecalhos))
    ws.freeze_panes = "A2"

    for r, d in enumerate(sorted(dados, key=lambda x: x["data"]), start=2):
        ws.cell(row=r, column=1, value=d["data"]).number_format = "DD/MM/YYYY"
        ws.cell(row=r, column=2, value=MESES[d["mes"] - 1])
        ws.cell(row=r, column=3, value=d["regiao"])
        ws.cell(row=r, column=4, value=d["categoria"])
        ws.cell(row=r, column=5, value=d["produto"])
        ws.cell(row=r, column=6, value=d["quantidade"]).number_format = "#,##0"
        ws.cell(row=r, column=7, value=d["receita"]).number_format = '"R$" #,##0.00'

    ws.auto_filter.ref = f"A1:G{1 + len(dados)}"
    largura_automatica(ws)


# --------------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    aqui = os.path.dirname(os.path.abspath(__file__))
    entrada = argv[1] if len(argv) > 1 else os.path.join(aqui, "vendas_exemplo.csv")
    saida = argv[2] if len(argv) > 2 else os.path.join(aqui, "relatorio_gerencial.xlsx")

    if not os.path.exists(entrada):
        print(f"CSV nao encontrado - gerando exemplo em {os.path.basename(entrada)}")
        gerar_csv_exemplo(entrada)

    print(f"Lendo {os.path.basename(entrada)} ...")
    dados = ler_vendas(entrada)
    print(f"  {len(dados)} registros validos")

    wb = Workbook()
    aba_resumo(wb, dados, entrada)
    aba_detalhe(wb, dados)
    aba_base(wb, dados)
    wb.save(saida)

    receita = sum(d["receita"] for d in dados)
    print(f"Relatorio gerado: {os.path.basename(saida)}")
    valor = f"{receita:,.2f}".replace(",", "|").replace(".", ",").replace("|", ".")
    print(f"  3 abas - receita total R$ {valor}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
