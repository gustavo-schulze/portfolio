# Gustavo Gorges — Soluções em Dados & Tecnologia

Portfólio de serviços em Excel avançado, Python, Power BI, automação de
processos e desenvolvimento web.

**Site:** https://SEU-USUARIO.github.io/portfolio/
*(atualize esta URL depois de publicar)*

## Projetos demonstrativos

> Todos usam **dados fictícios**, marcados como tal dentro de cada projeto.
> Não representam trabalho realizado para clientes.

| Projeto | O que mostra | Stack |
|---|---|---|
| [Dashboard Comercial](projetos/dashboard-vendas/) | KPIs, receita mensal, mix por categoria e ranking de produtos, com filtro por ano e região | JavaScript, SVG |
| [Controle Financeiro](projetos/controle-financeiro/) | Orçado × realizado, evolução do saldo e classificação automática de lançamentos | JavaScript, SVG |
| [Automação de Relatórios](projetos/automacao-relatorios/) | CSV vira pasta Excel com 3 abas, gráficos nativos e formatação condicional | Python, openpyxl |
| [Monitor de Preços](projetos/scraper-precos/) | Coleta catálogo, compara com a rodada anterior e reporta variação de preço | Python (só stdlib) |

Os dois primeiros abrem direto no navegador. Os dois últimos são scripts que
você pode executar — cada um tem seu próprio README com instruções.

## Estrutura

```
.
├── index.html              página única do portfólio
├── css/style.css           identidade visual (tokens em :root)
├── js/main.js              menu mobile e revelação ao rolar
├── img/                    capturas dos projetos
└── projetos/
    ├── dashboard-vendas/       demo interativa
    ├── controle-financeiro/    demo interativa
    ├── automacao-relatorios/   script Python + README
    └── scraper-precos/         script Python + README
```

## Rodando localmente

É um site estático — abrir `index.html` no navegador já funciona. Para servir
via HTTP (recomendado, evita restrições de origem):

```bash
python -m http.server 8000
# depois acesse http://localhost:8000
```

## Tecnologia

HTML, CSS e JavaScript puro. **Sem framework, sem build, sem dependências.**
A única requisição externa é a fonte (Google Fonts). Publicado no GitHub Pages.

## Personalizar

- **Cores e tipografia:** variáveis no `:root` de `css/style.css`
- **Textos, serviços e projetos:** direto no `index.html`
- **Contatos:** procure por `wa.me/5547997605191` e `gustavo.gorges007@gmail.com`

---

**Contato** · [gustavo.gorges007@gmail.com](mailto:gustavo.gorges007@gmail.com)
· WhatsApp [+55 (47) 99760-5191](https://wa.me/5547997605191)
· Joinville, SC
