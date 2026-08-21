"""
Aba 4 — Análise de Dados (parte principal, peso 7,0 na avaliação)

Tema: O boom da Inteligência Artificial em dois recortes complementares
      1) O custo de treinar modelos está explodindo (Epoch AI)
      2) Desenvolvedores estão adotando IA em massa (Stack Overflow Survey 2024)

Método estatístico principal: Intervalos de Confiança (95%)
  - IC para média (via distribuição t de Student, pequenas amostras)
  - IC para proporção (Wilson score, robusto para p próximo de 0 ou 1)
  - IC para diferença de médias (dois grupos independentes)
"""
import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from pathlib import Path
import re

dash.register_page(__name__, path="/analise", name="Análise de Dados", order=4)

DATA_DIR = Path(__file__).parent.parent / "data"

# ==================================================================
# CARREGAMENTO E LIMPEZA DOS DADOS
# ==================================================================

def _parse_cost(x):
    if pd.isna(x):
        return None
    try:
        return float(re.sub(r"[$,]", "", str(x)))
    except (ValueError, TypeError):
        return None


# ---- Dataset 1: Epoch AI ------------------------------------------
epoch = pd.read_csv(DATA_DIR / "epoch_ai_models.csv")
epoch["cost_usd"] = epoch["Training compute cost (2023 USD)"].apply(_parse_cost)
epoch["ano"] = pd.to_datetime(epoch["Publication date"], errors="coerce").dt.year
epoch["log_cost"] = np.log10(epoch["cost_usd"].where(epoch["cost_usd"] > 0))
epoch["params"] = pd.to_numeric(epoch["Parameters"], errors="coerce")
epoch["flop"] = pd.to_numeric(epoch["Training compute (FLOP)"], errors="coerce")
epoch["log_params"] = np.log10(epoch["params"].where(epoch["params"] > 0))
epoch["log_flop"] = np.log10(epoch["flop"].where(epoch["flop"] > 0))


def _org_principal(org):
    """Consolida os nomes bagunçados de organização nas principais big techs."""
    if pd.isna(org):
        return "Outras"
    o = str(org).lower()
    if "openai" in o:
        return "OpenAI"
    if "deepmind" in o:
        return "Google DeepMind"
    if "google" in o:
        return "Google"
    if "meta" in o or "facebook" in o:
        return "Meta"
    if "microsoft" in o:
        return "Microsoft"
    if "nvidia" in o:
        return "NVIDIA"
    if "alibaba" in o:
        return "Alibaba"
    if "anthropic" in o:
        return "Anthropic"
    if "mistral" in o:
        return "Mistral AI"
    return "Outras"


epoch["org_grupo"] = epoch["Organization"].apply(_org_principal)

# ---- Dataset 2: Stack Overflow Survey 2024 ------------------------
so = pd.read_csv(DATA_DIR / "so_survey_2024.csv")
# ai_select: 1=No don't plan, 2=No plan to, 3=Yes
so["usa_ia"] = so["ai_select"].map(lambda x: 1 if x == 3 else (0 if x in [1, 2] else None))
# ai_sent: 1=Favorable, 2=Indifferent, 3=Unfavorable, 4=Unsure, 5=Very fav, 6=Very unfav
so["favoravel_ia"] = so["ai_sent"].map(lambda x: 1 if x in [1, 5] else (0 if x in [3, 6] else None))
# ai_threat: 1=Yes, 2=I'm not sure, 3=No
so["ia_ameaca"] = so["ai_threat"].map(lambda x: 1 if x == 1 else (0 if x == 3 else None))
# salário limpo (remove outliers extremos) e anos de experiência
so["salario"] = so["converted_comp_yearly"].where(
    so["converted_comp_yearly"].between(1000, 500000)
)
so["anos_exp"] = pd.to_numeric(so["years_code_pro"], errors="coerce")

# ==================================================================
# FUNÇÕES ESTATÍSTICAS — INTERVALOS DE CONFIANÇA
# ==================================================================

def ic_media(dados, confianca=0.95):
    """IC para a média (t de Student, adequado quando n é pequeno ou sigma desconhecido)."""
    dados = np.asarray(dados)
    dados = dados[~np.isnan(dados)]
    n = len(dados)
    if n < 2:
        return None
    media = np.mean(dados)
    dp = np.std(dados, ddof=1)  # desvio amostral
    erro = stats.t.ppf((1 + confianca) / 2, df=n - 1) * dp / np.sqrt(n)
    return {"media": media, "n": n, "dp": dp, "li": media - erro, "ls": media + erro,
            "margem": erro}


def ic_proporcao(sucessos, n, confianca=0.95):
    """IC de Wilson para proporção — mais robusto que Wald, especialmente para p próximo de 0 ou 1."""
    if n == 0:
        return None
    p = sucessos / n
    z = stats.norm.ppf((1 + confianca) / 2)
    denom = 1 + z ** 2 / n
    centro = (p + z ** 2 / (2 * n)) / denom
    metade = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denom
    return {"p": p, "n": n, "sucessos": int(sucessos),
            "li": max(0, centro - metade), "ls": min(1, centro + metade)}


def ic_diff_medias(a, b, confianca=0.95):
    """IC para diferença de médias (Welch, não assume variâncias iguais)."""
    a = np.asarray(a); a = a[~np.isnan(a)]
    b = np.asarray(b); b = b[~np.isnan(b)]
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    ma, mb = np.mean(a), np.mean(b)
    va, vb = np.var(a, ddof=1), np.var(b, ddof=1)
    se = np.sqrt(va / na + vb / nb)
    df = (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    diff = ma - mb
    erro = stats.t.ppf((1 + confianca) / 2, df=df) * se
    return {"diff": diff, "li": diff - erro, "ls": diff + erro,
            "ma": ma, "mb": mb, "na": na, "nb": nb}


# ==================================================================
# ESTATÍSTICA DESCRITIVA — medidas centrais e de dispersão
# ==================================================================

def descritivas(serie):
    """Calcula todas as medidas centrais e de dispersão de uma variável quantitativa."""
    s = pd.Series(serie).dropna()
    n = len(s)
    if n == 0:
        return None
    media = s.mean()
    dp = s.std(ddof=1)
    moda = s.round(-3).mode()
    return {
        "n": n,
        "media": media,
        "mediana": s.median(),
        "moda": moda.iloc[0] if len(moda) else np.nan,
        "minimo": s.min(),
        "maximo": s.max(),
        "amplitude": s.max() - s.min(),
        "variancia": s.var(ddof=1),
        "dp": dp,
        "cv": dp / media * 100 if media else np.nan,   # coeficiente de variação (%)
        "q1": s.quantile(0.25),
        "q3": s.quantile(0.75),
    }


# calcula para as duas variáveis quantitativas mais relevantes
DESC_SALARIO = descritivas(so["salario"])
DESC_CUSTO = descritivas(epoch["cost_usd"])
DESC_EXP = descritivas(so["anos_exp"])


def tabela_descritivas():
    """Monta a tabela HTML comparando as medidas das variáveis quantitativas."""
    def fmt(v, moeda=False):
        if pd.isna(v):
            return "—"
        if moeda:
            return f"US$ {v:,.0f}"
        return f"{v:,.1f}"

    linhas = [
        ("Nº de observações (n)", f"{DESC_SALARIO['n']:,}", f"{DESC_CUSTO['n']:,}",
         f"{DESC_EXP['n']:,}"),
        ("Média", fmt(DESC_SALARIO["media"], True), fmt(DESC_CUSTO["media"], True),
         fmt(DESC_EXP["media"])),
        ("Mediana", fmt(DESC_SALARIO["mediana"], True), fmt(DESC_CUSTO["mediana"], True),
         fmt(DESC_EXP["mediana"])),
        ("Moda (faixa)", fmt(DESC_SALARIO["moda"], True), fmt(DESC_CUSTO["moda"], True),
         fmt(DESC_EXP["moda"])),
        ("Mínimo", fmt(DESC_SALARIO["minimo"], True), fmt(DESC_CUSTO["minimo"], True),
         fmt(DESC_EXP["minimo"])),
        ("Máximo", fmt(DESC_SALARIO["maximo"], True), fmt(DESC_CUSTO["maximo"], True),
         fmt(DESC_EXP["maximo"])),
        ("Amplitude", fmt(DESC_SALARIO["amplitude"], True), fmt(DESC_CUSTO["amplitude"], True),
         fmt(DESC_EXP["amplitude"])),
        ("Desvio-padrão", fmt(DESC_SALARIO["dp"], True), fmt(DESC_CUSTO["dp"], True),
         fmt(DESC_EXP["dp"])),
        ("Coef. de variação (CV)", f"{DESC_SALARIO['cv']:.1f}%", f"{DESC_CUSTO['cv']:.1f}%",
         f"{DESC_EXP['cv']:.1f}%"),
    ]
    header = html.Tr([
        html.Th("Medida"),
        html.Th("Salário anual (USD)"),
        html.Th("Custo de treino (USD)"),
        html.Th("Anos de exp. prof."),
    ])
    corpo = [html.Tr([html.Td(c) for c in linha]) for linha in linhas]
    return html.Table(className="stats-table", children=[html.Thead(header), html.Tbody(corpo)])


# ==================================================================
# DISTRIBUIÇÃO — histograma + boxplot
# ==================================================================

def fig_histograma_salario():
    s = so["salario"].dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=s, nbinsx=50, marker=dict(color="#4f8cff"),
        hovertemplate="Faixa: US$ %{x}<br>Freq: %{y}<extra></extra>",
    ))
    fig.add_vline(x=s.mean(), line_dash="dash", line_color="#f59e0b",
                  annotation_text=f"Média US$ {s.mean():,.0f}", annotation_position="top")
    fig.add_vline(x=s.median(), line_dash="dot", line_color="#5eead4",
                  annotation_text=f"Mediana US$ {s.median():,.0f}", annotation_position="bottom")
    fig.update_layout(
        title="Distribuição dos salários anuais dos desenvolvedores (USD)",
        xaxis_title="Salário anual (USD)",
        yaxis_title="Frequência (nº de respondentes)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"), height=420, bargap=0.02,
    )
    return fig


def fig_boxplot_salario_ia():
    sub = so[so["salario"].notna() & so["usa_ia"].notna()].copy()
    sub["grupo"] = sub["usa_ia"].map({1: "Usa IA", 0: "Não usa IA"})
    fig = go.Figure()
    for grupo, cor in [("Usa IA", "#4f8cff"), ("Não usa IA", "#4b5563")]:
        dados = sub[sub["grupo"] == grupo]["salario"]
        fig.add_trace(go.Box(
            y=dados, name=grupo, marker=dict(color=cor), boxmean=True,
        ))
    fig.update_layout(
        title="Boxplot dos salários — usa IA vs. não usa",
        yaxis_title="Salário anual (USD)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"), height=420, showlegend=False,
    )
    return fig


# ==================================================================
# CORRELAÇÃO — custo vs. FLOP vs. parâmetros (em escala log)
# ==================================================================

def fig_correlacao():
    sub = epoch[
        (epoch["cost_usd"] > 0) & (epoch["params"] > 0) & (epoch["flop"] > 0)
    ].copy()
    corr = sub[["log_cost", "log_flop", "log_params"]].corr()
    labels = {"log_cost": "log(Custo)", "log_flop": "log(FLOP)",
              "log_params": "log(Parâmetros)"}
    corr = corr.rename(index=labels, columns=labels)

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=list(corr.columns), y=list(corr.index),
        colorscale="RdBu", zmid=0, zmin=-1, zmax=1,
        text=corr.round(3).values, texttemplate="%{text}",
        textfont=dict(size=16, color="#000"),
        colorbar=dict(title="r de Pearson"),
    ))
    fig.update_layout(
        title=f"Matriz de correlação (log-log, n = {len(sub)} modelos)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"), height=420,
    )
    return fig, corr, sub


def fig_dispersao_custo_flop():
    sub = epoch[(epoch["cost_usd"] > 0) & (epoch["flop"] > 0)].copy()
    r = sub["log_cost"].corr(sub["log_flop"])
    fig = px.scatter(
        sub, x="flop", y="cost_usd",
        hover_name="System", hover_data={"Organization": True},
        log_x=True, log_y=True,
        color_discrete_sequence=["#5eead4"],
    )
    fig.update_layout(
        title=f"Custo de treino vs. poder computacional (FLOP) — r = {r:.3f}",
        xaxis_title="Compute de treino (FLOP, escala log)",
        yaxis_title="Custo de treino (USD, escala log)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"), height=420,
    )
    fig.update_traces(marker=dict(size=7, opacity=0.65))
    return fig, r


# ==================================================================
# ANÁLISE 1 — CUSTO DE TREINAMENTO DE MODELOS DE IA POR ANO
# ==================================================================

def fig_custo_por_ano(ano_min=2017, ano_max=2023, org="Todas"):
    df = epoch[
        epoch["cost_usd"].notna() & epoch["ano"].notna()
        & (epoch["ano"] >= ano_min) & (epoch["ano"] <= ano_max)
    ]
    if org != "Todas":
        df = df[df["org_grupo"] == org]
    resultados = []
    for ano, grupo in df.groupby("ano"):
        ic = ic_media(grupo["log_cost"].values)
        if ic is None:
            continue
        resultados.append({
            "ano": int(ano),
            "n": ic["n"],
            "media_log": ic["media"],
            "li_log": ic["li"],
            "ls_log": ic["ls"],
            "media_usd": 10 ** ic["media"],
            "li_usd": 10 ** ic["li"],
            "ls_usd": 10 ** ic["ls"],
        })
    res = pd.DataFrame(resultados)

    sufixo_org = "" if org == "Todas" else f" · {org}"
    fig = go.Figure()
    if len(res):
        fig.add_trace(go.Scatter(
            x=res["ano"], y=res["media_usd"],
            mode="lines+markers",
            name="Custo médio (geométrico)",
            line=dict(color="#4f8cff", width=3),
            marker=dict(size=10),
            error_y=dict(
                type="data",
                symmetric=False,
                array=res["ls_usd"] - res["media_usd"],
                arrayminus=res["media_usd"] - res["li_usd"],
                color="#4f8cff",
            ),
            hovertemplate=(
                "<b>Ano %{x}</b><br>"
                "Custo médio: US$ %{y:,.0f}<br>"
                "IC 95%: US$ %{customdata[0]:,.0f} – US$ %{customdata[1]:,.0f}<br>"
                "n = %{customdata[2]} modelos<extra></extra>"
            ),
            customdata=res[["li_usd", "ls_usd", "n"]].values,
        ))
    fig.update_layout(
        title=f"Custo médio de treinamento de modelos de IA por ano — IC 95% "
              f"({ano_min}–{ano_max}){sufixo_org}",
        xaxis_title="Ano de publicação",
        yaxis_title="Custo de treinamento (USD 2023, escala log)",
        yaxis_type="log",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"),
        hovermode="x unified",
        height=440,
    )
    return fig, res


def fig_top_modelos(ano_min=2017, ano_max=2023, org="Todas"):
    filtrado = epoch[
        epoch["cost_usd"].notna() & epoch["ano"].notna()
        & (epoch["ano"] >= ano_min) & (epoch["ano"] <= ano_max)
    ]
    if org != "Todas":
        filtrado = filtrado[filtrado["org_grupo"] == org]
    top = filtrado.nlargest(10, "cost_usd")[
        ["System", "Organization", "ano", "cost_usd"]
    ]
    sufixo_org = "" if org == "Todas" else f" · {org}"
    n_modelos = len(top)
    if n_modelos == 0:
        fig = go.Figure()
        fig.update_layout(
            title=f"Sem modelos com custo estimado no filtro selecionado{sufixo_org}",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaed"), height=440,
        )
        return fig
    fig = px.bar(
        top.iloc[::-1],
        x="cost_usd", y="System", orientation="h",
        color="Organization",
        text=top.iloc[::-1]["cost_usd"].apply(lambda v: f"US$ {v/1e6:.1f}M"),
        hover_data={"ano": True, "cost_usd": ":,.0f"},
    )
    fig.update_layout(
        title=f"Top {n_modelos} modelos de IA mais caros de treinar "
              f"({ano_min}–{ano_max}){sufixo_org}",
        xaxis_title="Custo de treinamento (USD 2023)",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"),
        height=440,
    )
    fig.update_traces(textposition="outside")
    return fig


# ==================================================================
# ANÁLISE 2 — ADOÇÃO DE IA POR DESENVOLVEDORES
# ==================================================================

def fig_adocao_global():
    resp = so[so["usa_ia"].notna()]
    ic = ic_proporcao(resp["usa_ia"].sum(), len(resp))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Usa IA no dev", "Não usa IA"],
        y=[ic["p"] * 100, (1 - ic["p"]) * 100],
        marker=dict(color=["#4f8cff", "#4b5563"]),
        text=[f"{ic['p']*100:.1f}%<br>IC: [{ic['li']*100:.1f}% – {ic['ls']*100:.1f}%]",
              f"{(1-ic['p'])*100:.1f}%"],
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Adoção de IA entre desenvolvedores no mundo (n = {ic['n']:,})",
        yaxis_title="Percentual de respondentes (%)",
        yaxis=dict(range=[0, 75]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"),
        showlegend=False,
        height=400,
    )
    return fig, ic


def fig_adocao_por_pais():
    resp = so[so["usa_ia"].notna()]
    paises = (
        resp.groupby("country")["usa_ia"]
        .agg(["count", "sum"])
        .rename(columns={"count": "n", "sum": "sucessos"})
        .query("n >= 150")
        .sort_values("n", ascending=False)
        .head(15)
    )
    ics = paises.apply(lambda r: ic_proporcao(r["sucessos"], r["n"]), axis=1)
    paises["p"] = [ic["p"] for ic in ics]
    paises["li"] = [ic["li"] for ic in ics]
    paises["ls"] = [ic["ls"] for ic in ics]
    paises = paises.sort_values("p", ascending=True).reset_index()
    paises["pais_curto"] = paises["country"].str.replace(
        "United States of America", "EUA"
    ).str.replace(
        "United Kingdom of Great Britain and Northern Ireland", "Reino Unido"
    ).str.replace("Russian Federation", "Rússia")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=paises["pais_curto"],
        x=paises["p"] * 100,
        orientation="h",
        marker=dict(color=paises["p"] * 100, colorscale="Blues", showscale=False),
        error_x=dict(
            type="data",
            symmetric=False,
            array=(paises["ls"] - paises["p"]) * 100,
            arrayminus=(paises["p"] - paises["li"]) * 100,
            color="#94a3b8",
        ),
        text=[f"{p*100:.1f}% (n={n})" for p, n in zip(paises["p"], paises["n"])],
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>Usam IA: %{x:.1f}%<br>"
            "IC 95%: [%{customdata[0]:.1f}% – %{customdata[1]:.1f}%]<br>"
            "n = %{customdata[2]}<extra></extra>"
        ),
        customdata=np.stack([paises["li"] * 100, paises["ls"] * 100, paises["n"]], axis=1),
    ))
    fig.update_layout(
        title="Proporção de desenvolvedores que usam IA — por país (IC 95%)",
        xaxis_title="Percentual que usa IA (%)",
        xaxis=dict(range=[0, 100]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"),
        height=560,
        margin=dict(l=120, r=60),
    )
    return fig, paises


def fig_sentimento():
    # ai_sent categorias reais
    labels_map = {1: "Favorável", 2: "Indiferente", 3: "Desfavorável",
                  4: "Não sei", 5: "Muito favorável", 6: "Muito desfavorável"}
    resp = so[so["ai_sent"].notna()].copy()
    resp["sentimento"] = resp["ai_sent"].map(labels_map)
    contagem = resp["sentimento"].value_counts()
    ordem = ["Muito favorável", "Favorável", "Indiferente", "Não sei",
             "Desfavorável", "Muito desfavorável"]
    contagem = contagem.reindex([o for o in ordem if o in contagem.index])
    cores = ["#059669", "#4f8cff", "#94a3b8", "#a78bfa", "#f59e0b", "#dc2626"]

    fig = go.Figure(data=[go.Pie(
        labels=contagem.index,
        values=contagem.values,
        hole=0.55,
        marker=dict(colors=cores[:len(contagem)]),
        textinfo="label+percent",
    )])
    fig.update_layout(
        title=f"Sentimento dos devs sobre IA no workflow (n = {len(resp):,})",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"),
        height=400,
    )
    return fig


def analise_salario_ia():
    """Compara salário médio de devs que usam IA vs os que não usam."""
    sub = so[
        so["converted_comp_yearly"].notna()
        & so["usa_ia"].notna()
        & so["converted_comp_yearly"].between(1000, 500000)
    ].copy()
    usa = sub[sub["usa_ia"] == 1]["converted_comp_yearly"]
    nao_usa = sub[sub["usa_ia"] == 0]["converted_comp_yearly"]

    ic_usa = ic_media(usa.values)
    ic_nao = ic_media(nao_usa.values)
    ic_dif = ic_diff_medias(usa.values, nao_usa.values)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Usa IA", "Não usa IA"],
        y=[ic_usa["media"], ic_nao["media"]],
        marker=dict(color=["#4f8cff", "#4b5563"]),
        error_y=dict(
            type="data",
            array=[ic_usa["margem"], ic_nao["margem"]],
            color="#94a3b8",
        ),
        text=[
            f"US$ {ic_usa['media']:,.0f}<br>IC: [{ic_usa['li']:,.0f} – {ic_usa['ls']:,.0f}]",
            f"US$ {ic_nao['media']:,.0f}<br>IC: [{ic_nao['li']:,.0f} – {ic_nao['ls']:,.0f}]",
        ],
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Salário anual médio (USD) — usa IA vs. não usa (n = {len(sub):,})",
        yaxis_title="Salário anual (USD)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"),
        showlegend=False,
        height=400,
    )
    return fig, ic_usa, ic_nao, ic_dif


# ==================================================================
# COMPUTA VALORES PARA EXIBIR NA PÁGINA
# ==================================================================

# Intervalo de anos disponível para o filtro interativo
_anos_validos = epoch[epoch["cost_usd"].notna() & epoch["ano"].notna()]
ANO_MIN_DISP = 2017
ANO_MAX_DISP = int(_anos_validos["ano"].max())

# Organizações disponíveis para o filtro (só as que têm modelos com custo)
_orgs_com_custo = (
    epoch[epoch["cost_usd"].notna()]["org_grupo"].value_counts()
)
# mantém as principais big techs com pelo menos 2 modelos, ordenadas por quantidade
ORGS_DISP = ["Todas"] + [
    o for o in _orgs_com_custo.index if o != "Outras" and _orgs_com_custo[o] >= 2
] + (["Outras"] if "Outras" in _orgs_com_custo.index else [])

# RES_CUSTO no período completo — usado nos KPIs (valor de referência)
_, RES_CUSTO = fig_custo_por_ano(ANO_MIN_DISP, ANO_MAX_DISP)
FIG_GLOBAL, IC_GLOBAL = fig_adocao_global()
FIG_PAISES, TAB_PAISES = fig_adocao_por_pais()
FIG_SENT = fig_sentimento()
FIG_SAL, IC_USA, IC_NAO, IC_DIF = analise_salario_ia()
FIG_HIST = fig_histograma_salario()
FIG_BOX = fig_boxplot_salario_ia()
FIG_CORR, MAT_CORR, _ = fig_correlacao()
FIG_DISP, R_CUSTO_FLOP = fig_dispersao_custo_flop()

# Métricas destaque para os KPIs
CRESC_CUSTO = RES_CUSTO.iloc[-1]["media_usd"] / RES_CUSTO.iloc[0]["media_usd"]
BR = TAB_PAISES[TAB_PAISES["country"] == "Brazil"]
if len(BR):
    BR_P = BR.iloc[0]["p"] * 100
    BR_LI = BR.iloc[0]["li"] * 100
    BR_LS = BR.iloc[0]["ls"] * 100
    BR_N = int(BR.iloc[0]["n"])
else:
    BR_P = BR_LI = BR_LS = BR_N = 0


# ==================================================================
# LAYOUT
# ==================================================================

def kpi_card(titulo, valor, sub):
    return html.Div(
        className="kpi",
        children=[
            html.Div(titulo, className="kpi-titulo"),
            html.Div(valor, className="kpi-valor"),
            html.Div(sub, className="kpi-sub"),
        ],
    )


def layout():
    return html.Div(
        className="page page-analise",
        children=[
            html.H1("Análise de Dados: o boom da Inteligência Artificial"),
            html.P(
                "Este estudo combina dois datasets públicos e reais para investigar duas "
                "faces do crescimento da IA: o custo crescente de treinar modelos e a adoção "
                "acelerada pelos desenvolvedores. Todas as conclusões são apresentadas com "
                "intervalos de confiança de 95% — a estatística inferencial nos permite ir além "
                "dos números observados e afirmar, com margem controlada, o que provavelmente "
                "acontece na população.",
                className="lead",
            ),

            # -------- KPIs de destaque --------
            html.Section(
                className="kpi-row",
                children=[
                    kpi_card("Custo geométrico médio de treino (2023)",
                             f"US$ {RES_CUSTO.iloc[-1]['media_usd']/1e6:.2f}M",
                             f"IC 95%: US$ {RES_CUSTO.iloc[-1]['li_usd']/1e6:.2f}M – "
                             f"US$ {RES_CUSTO.iloc[-1]['ls_usd']/1e6:.2f}M"),
                    kpi_card("Crescimento vs. 2017",
                             f"{CRESC_CUSTO:,.1f}× em 6 anos",
                             "custo geométrico médio"),
                    kpi_card("Devs que usam IA (mundo)",
                             f"{IC_GLOBAL['p']*100:.1f}%",
                             f"IC 95%: [{IC_GLOBAL['li']*100:.1f}% – "
                             f"{IC_GLOBAL['ls']*100:.1f}%] • n = {IC_GLOBAL['n']:,}"),
                    kpi_card("Devs que usam IA (Brasil)",
                             f"{BR_P:.1f}%",
                             f"IC 95%: [{BR_LI:.1f}% – {BR_LS:.1f}%] • n = {BR_N:,}"),
                ],
            ),

            # -------- Datasets utilizados --------
            html.Section(
                className="card",
                children=[
                    html.H2("Sobre os dados"),
                    html.Div(
                        className="dataset-grid",
                        children=[
                            html.Div(className="dataset-card", children=[
                                html.H3("Dataset 1 — Epoch AI"),
                                html.P([
                                    html.Strong("Fonte: "),
                                    html.A("Epoch AI — Data on AI Models",
                                           href="https://epoch.ai/data/ai-models",
                                           target="_blank"),
                                ]),
                                html.Ul([
                                    html.Li(f"{len(epoch):,} modelos catalogados"),
                                    html.Li(f"{epoch['cost_usd'].notna().sum()} com custo "
                                            f"de treinamento estimado (USD 2023)"),
                                    html.Li("Período: 2015 – 2024"),
                                    html.Li("Licença: Creative Commons Attribution 4.0"),
                                ]),
                            ]),
                            html.Div(className="dataset-card", children=[
                                html.H3("Dataset 2 — Stack Overflow Survey 2024"),
                                html.P([
                                    html.Strong("Fonte: "),
                                    html.A("Stack Overflow Developer Survey 2024",
                                           href="https://survey.stackoverflow.co/2024/",
                                           target="_blank"),
                                    " (via TidyTuesday)",
                                ]),
                                html.Ul([
                                    html.Li(f"{len(so):,} respondentes em 185 países"),
                                    html.Li("28 colunas — foco em uso, confiança e "
                                            "sentimento sobre IA"),
                                    html.Li("Amostra brasileira: 1.367 respondentes"),
                                    html.Li("Licença: Open Database License (ODbL)"),
                                ]),
                            ]),
                        ],
                    ),
                ],
            ),

            # -------- Perguntas de pesquisa --------
            html.Section(
                className="card",
                children=[
                    html.H2("Perguntas que este estudo responde"),
                    html.Ol([
                        html.Li("Qual a magnitude e a velocidade do aumento do custo de "
                                "treinamento de modelos de IA?"),
                        html.Li("Que proporção de desenvolvedores hoje usa IA em seu "
                                "workflow? Essa adoção varia significativamente entre países?"),
                        html.Li("Como os desenvolvedores se sentem em relação à IA — "
                                "adoção massiva significa aceitação massiva?"),
                        html.Li("Desenvolvedores que usam IA ganham mais do que os que "
                                "não usam? A diferença é estatisticamente significativa?"),
                    ]),
                ],
            ),

            # ==============================================================
            # NAVEGAÇÃO POR ABAS INTERNAS (F-Pattern: título → conteúdo)
            # ==============================================================
            dcc.Tabs(
                id="abas-analise",
                value="descritiva",
                className="abas-analise",
                children=[
                    dcc.Tab(label="Estatística Descritiva", value="descritiva",
                            className="aba-item", selected_className="aba-item-sel"),
                    dcc.Tab(label="Parte 1 · Custo dos Modelos", value="parte1",
                            className="aba-item", selected_className="aba-item-sel"),
                    dcc.Tab(label="Parte 2 · Adoção de IA", value="parte2",
                            className="aba-item", selected_className="aba-item-sel"),
                    dcc.Tab(label="Parte 3 · Distribuição e Correlação", value="parte3",
                            className="aba-item", selected_className="aba-item-sel"),
                    dcc.Tab(label="Conclusão", value="conclusao",
                            className="aba-item", selected_className="aba-item-sel"),
                ],
            ),
            html.Div(id="conteudo-aba", className="conteudo-aba"),
        ],
    )


# ==================================================================
# CONTEÚDO DE CADA ABA INTERNA (funções que retornam o layout)
# ==================================================================

def _secao_descritiva():
    return html.Div([
        html.H2("Estatística descritiva das variáveis quantitativas",
                className="section-title"),
        html.Section(className="card", children=[
            html.P(
                "Antes da análise inferencial, resumimos as três principais variáveis "
                "quantitativas do estudo com medidas de tendência central (média, "
                "mediana, moda) e de dispersão (amplitude, desvio-padrão, coeficiente "
                "de variação). Essas medidas descrevem o comportamento típico e a "
                "variabilidade dos dados."
            ),
            tabela_descritivas(),
            html.Div(className="interpretation", children=[
                html.H4("Leitura das medidas"),
                html.P([
                    html.Strong("Média vs. mediana: "),
                    f"no salário, a média (US$ {DESC_SALARIO['media']:,.0f}) é bem "
                    f"maior que a mediana (US$ {DESC_SALARIO['mediana']:,.0f}). "
                    "Essa diferença indica uma distribuição assimétrica à direita — "
                    "poucos salários muito altos puxam a média para cima. Nesse caso, "
                    "a mediana representa melhor o desenvolvedor 'típico'.",
                ]),
                html.P([
                    html.Strong("Coeficiente de variação (CV): "),
                    f"o custo de treinamento tem CV de {DESC_CUSTO['cv']:.1f}%, "
                    f"muito acima do salário ({DESC_SALARIO['cv']:.1f}%). Um CV alto "
                    "significa dispersão enorme em relação à média — coerente com o "
                    "fato de que os custos vão de centenas a dezenas de milhões de "
                    "dólares. O CV permite comparar a variabilidade entre variáveis "
                    "de escalas diferentes, já que é adimensional (em %).",
                ]),
                html.P([
                    html.Strong("Amplitude: "),
                    "mede a diferença entre o maior e o menor valor. É a medida de "
                    "dispersão mais simples, mas sensível a outliers — por isso a "
                    "complementamos com o desvio-padrão e o CV.",
                ]),
            ]),
        ]),
    ])


def _secao_parte1():
    return html.Div([
        html.H2("Parte 1 — O custo de treinar modelos está explodindo",
                className="section-title"),
        html.Section(className="card", children=[
            html.Div(className="filtro-box", children=[
                html.H4("🔎 Filtros interativos"),
                html.P("Combine o período e a organização. Os dois gráficos "
                       "abaixo se recalculam automaticamente.",
                       className="filtro-hint"),
                html.Label("Organização", className="filtro-label"),
                dcc.Dropdown(
                    id="filtro-org",
                    options=[{"label": o, "value": o} for o in ORGS_DISP],
                    value="Todas",
                    clearable=False,
                    className="filtro-dropdown",
                ),
                html.Label("Período (anos)", className="filtro-label",
                           style={"marginTop": "18px"}),
                dcc.RangeSlider(
                    id="filtro-ano",
                    min=ANO_MIN_DISP,
                    max=ANO_MAX_DISP,
                    step=1,
                    value=[ANO_MIN_DISP, ANO_MAX_DISP],
                    marks={a: str(a) for a in range(ANO_MIN_DISP, ANO_MAX_DISP + 1)},
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
            ]),
            dcc.Graph(id="grafico-custo-ano"),
            html.Div(className="interpretation", children=[
                html.H4("Interpretação"),
                html.Div(id="texto-custo-ano"),
                html.P([
                    html.Strong("Por que média geométrica? "),
                    "Custos de treinamento variam por várias ordens de grandeza "
                    "(de centenas de dólares a dezenas de milhões). A média aritmética "
                    "seria distorcida por outliers. A média geométrica (equivalente à "
                    "média do log) descreve o comportamento típico de forma mais fiel.",
                ]),
            ]),
        ]),
        html.Section(className="card", children=[
            dcc.Graph(id="grafico-top-modelos"),
            html.Div(className="interpretation", children=[
                html.H4("Modelos mais caros do período selecionado"),
                html.P("Este ranking também responde ao filtro de ano acima. "
                       "No período completo, GPT-4 (OpenAI) lidera com US$ 40 milhões "
                       "estimados só de treinamento — quase o dobro do segundo colocado, "
                       "Gemini 1.0 Ultra (Google). Todos os mais caros foram lançados a "
                       "partir de 2022, evidenciando a corrida dos últimos anos."),
            ]),
        ]),
    ])


def _secao_parte2():
    return html.Div([
        html.H2("Parte 2 — Desenvolvedores adotaram IA em massa",
                className="section-title"),
        html.Section(className="card", children=[
            dcc.Graph(figure=FIG_GLOBAL),
            html.Div(className="interpretation", children=[
                html.H4("A maioria já usa IA no dia a dia"),
                html.P([
                    "Entre os ", html.Strong(f"{IC_GLOBAL['n']:,}"),
                    " desenvolvedores que responderam à pergunta, ",
                    html.Strong(f"{IC_GLOBAL['p']*100:.1f}%"),
                    " já usam IA no processo de desenvolvimento. O intervalo de "
                    "confiança de 95% (método de Wilson) é ",
                    html.Strong(f"[{IC_GLOBAL['li']*100:.2f}% ; {IC_GLOBAL['ls']*100:.2f}%]"),
                    " — um intervalo estreitíssimo, graças ao tamanho da amostra. "
                    "Isso significa que, se pudéssemos repetir a pesquisa infinitas "
                    "vezes na mesma população, 95% dos ICs conteriam a verdadeira "
                    "proporção populacional dentro dessa faixa.",
                ]),
            ]),
        ]),
        html.Section(className="card", children=[
            dcc.Graph(figure=FIG_PAISES),
            html.Div(className="interpretation", children=[
                html.H4("A adoção não é homogênea entre países"),
                html.P([
                    "Ucrânia lidera com ", html.Strong("72,3%"), " dos devs usando IA, "
                    "seguida por Índia (68%) e Brasil (66%). Nações do leste europeu, "
                    "sul da Ásia e América Latina aparecem consistentemente acima da "
                    "média mundial. Países como Rússia (47%) e Reino Unido (51%) estão "
                    "abaixo. Como os ICs de vários pares se sobrepõem (ex: Índia e Brasil), "
                    "não podemos afirmar que a diferença entre esses dois é "
                    "estatisticamente significativa; já entre Ucrânia e Rússia, por "
                    "exemplo, a diferença é clara.",
                ]),
            ]),
        ]),
        html.Section(className="card", children=[
            dcc.Graph(figure=FIG_SENT),
            html.Div(className="interpretation", children=[
                html.H4("Adoção não é o mesmo que entusiasmo"),
                html.P("Embora 62% já usem IA, apenas cerca de dois terços dos que "
                       "responderam essa pergunta se dizem favoráveis ou muito favoráveis. "
                       "O restante se divide entre indiferentes, indecisos e uma "
                       "minoria explícita de desfavoráveis — sinal de que ferramentas "
                       "de IA já estão no dia a dia mesmo de quem não gosta muito delas."),
            ]),
        ]),
        html.Section(className="card", children=[
            dcc.Graph(figure=FIG_SAL),
            html.Div(className="interpretation", children=[
                html.H4("Usar IA não significa ganhar mais"),
                html.P([
                    "Comparando o salário anual médio (USD) entre quem usa e quem não "
                    "usa IA (filtrando salários entre US$ 1k e 500k para remover "
                    "outliers), obtemos: ",
                    html.Br(),
                    html.Strong("Usa IA: "),
                    f"US$ {IC_USA['media']:,.0f} (IC 95%: "
                    f"US$ {IC_USA['li']:,.0f} – US$ {IC_USA['ls']:,.0f}, "
                    f"n = {IC_USA['n']:,})",
                    html.Br(),
                    html.Strong("Não usa IA: "),
                    f"US$ {IC_NAO['media']:,.0f} (IC 95%: "
                    f"US$ {IC_NAO['li']:,.0f} – US$ {IC_NAO['ls']:,.0f}, "
                    f"n = {IC_NAO['n']:,})",
                    html.Br(),
                    html.Strong("Diferença (usa − não usa): "),
                    f"US$ {IC_DIF['diff']:,.0f} (IC 95%: "
                    f"US$ {IC_DIF['li']:,.0f} – US$ {IC_DIF['ls']:,.0f})",
                ]),
                html.P([
                    "Contraintuitivamente, quem ",
                    html.Em("não"), " usa IA ganha, em média, mais do que quem usa. "
                    "Como o IC da diferença não contém zero, a diferença é "
                    "estatisticamente significativa a 95% de confiança. Uma hipótese "
                    "razoável: profissionais mais seniores (que ganham mais) tendem "
                    "a adotar novas ferramentas mais devagar; devs juniores e em países "
                    "emergentes (com salários menores em USD) aderiram mais rápido à IA. "
                    "Correlação não é causa — usar IA não faz alguém ganhar menos.",
                ]),
            ]),
        ]),
    ])


def _secao_parte3():
    return html.Div([
        html.H2("Parte 3 — Distribuição e correlação",
                className="section-title"),
        html.Section(className="card", children=[
            dcc.Graph(figure=FIG_HIST),
            html.Div(className="interpretation", children=[
                html.H4("Forma da distribuição salarial"),
                html.P([
                    "O histograma confirma o que as medidas descritivas sugeriram: a "
                    "distribuição de salários é fortemente ", html.Strong("assimétrica "
                    "à direita"), " (cauda longa para valores altos). A maior parte dos "
                    "desenvolvedores se concentra na faixa mais baixa, e a média (linha "
                    "laranja) fica à direita da mediana (linha verde) — assinatura "
                    "clássica de uma distribuição enviesada positivamente.",
                ]),
            ]),
        ]),
        html.Section(className="card", children=[
            dcc.Graph(figure=FIG_BOX),
            html.Div(className="interpretation", children=[
                html.H4("Boxplot: comparando os dois grupos"),
                html.P([
                    "O boxplot mostra a mediana (linha central), o intervalo "
                    "interquartil (caixa, 50% centrais dos dados) e a média (linha "
                    "tracejada). Fica visível que ambos os grupos têm muitos outliers "
                    "superiores (pontos acima da caixa) e que a mediana de quem não usa "
                    "IA é ligeiramente maior — consistente com a análise de IC feita "
                    "na Parte 2.",
                ]),
            ]),
        ]),
        html.Section(className="card", children=[
            dcc.Graph(figure=FIG_CORR),
            dcc.Graph(figure=FIG_DISP),
            html.Div(className="interpretation", children=[
                html.H4("O que impulsiona o custo de treinamento?"),
                html.P([
                    "A matriz de correlação (r de Pearson sobre variáveis em escala "
                    "log) revela uma relação ", html.Strong("fortíssima"),
                    f" entre custo e poder computacional: r = "
                    f"{MAT_CORR.loc['log(Custo)', 'log(FLOP)']:.3f}. Ou seja, quanto "
                    "mais FLOPs (operações de ponto flutuante) um modelo consome no "
                    "treino, mais caro ele é — o que faz todo sentido, já que compute "
                    "é o principal item de custo. A correlação com o número de "
                    f"parâmetros é moderada-forte (r = "
                    f"{MAT_CORR.loc['log(Custo)', 'log(Parâmetros)']:.3f}).",
                ]),
                html.P([
                    "O gráfico de dispersão confirma visualmente: os pontos se alinham "
                    "quase em linha reta na escala log-log, indicando uma relação de ",
                    html.Strong("lei de potência"), " entre compute e custo. ",
                    html.Em("Correlação não implica causalidade"),
                    ", mas aqui a relação causal é bem estabelecida na literatura: "
                    "mais compute custa mais dinheiro.",
                ]),
            ]),
        ]),
    ])


def _secao_conclusao():
    return html.Div([
        html.H2("Conclusão", className="section-title"),
        html.Section(className="card conclusion", children=[
            html.P([
                "O boom da IA é real e mensurável em duas frentes complementares: ",
                html.Strong("do lado da oferta"),
                ", o custo médio de treinar um modelo notável multiplicou-se por "
                f"aproximadamente {CRESC_CUSTO:,.1f} vezes entre "
                f"{int(RES_CUSTO.iloc[0]['ano'])} e {int(RES_CUSTO.iloc[-1]['ano'])}, "
                "chegando à casa dos milhões de dólares por modelo; ",
                html.Strong("do lado da demanda"),
                ", 61,8% dos desenvolvedores no mundo já usam IA no workflow "
                "(IC 95% [61,4% ; 62,2%]), e o Brasil está acima da média mundial "
                f"com {BR_P:.1f}% (IC 95% [{BR_LI:.1f}% ; {BR_LS:.1f}%]). ",
            ]),
            html.P([
                "Os intervalos de confiança nos permitem afirmar essas conclusões "
                "com margem controlada, em vez de apenas apresentar médias observadas. "
                "O achado surpreendente sobre salário — devs que usam IA ganham menos, "
                "em média — mostra a importância de olhar além do óbvio e considerar "
                "confundidores como senioridade e paridade cambial."
            ]),
        ]),
    ])

# ==================================================================
# CALLBACK — troca o conteúdo conforme a aba interna selecionada
# ==================================================================

@callback(
    Output("conteudo-aba", "children"),
    Input("abas-analise", "value"),
)
def trocar_aba(aba):
    if aba == "descritiva":
        return _secao_descritiva()
    if aba == "parte1":
        return _secao_parte1()
    if aba == "parte2":
        return _secao_parte2()
    if aba == "parte3":
        return _secao_parte3()
    if aba == "conclusao":
        return _secao_conclusao()
    return _secao_descritiva()


# ==================================================================
# CALLBACK — filtro de ano atualiza os gráficos da Parte 1
# ==================================================================

@callback(
    Output("grafico-custo-ano", "figure"),
    Output("grafico-top-modelos", "figure"),
    Output("texto-custo-ano", "children"),
    Input("filtro-ano", "value"),
    Input("filtro-org", "value"),
)
def atualizar_parte1(intervalo, org):
    ano_min, ano_max = intervalo
    fig_custo, res = fig_custo_por_ano(ano_min, ano_max, org)
    fig_top = fig_top_modelos(ano_min, ano_max, org)

    org_txt = "" if org == "Todas" else f" (organização: {org})"

    # texto de interpretação dinâmico
    if len(res) >= 2:
        primeiro, ultimo = res.iloc[0], res.iloc[-1]
        cresc = ultimo["media_usd"] / primeiro["media_usd"]
        anos_span = int(ultimo["ano"]) - int(primeiro["ano"])
        texto = html.P([
            "Aplicando IC 95% sobre a média geométrica (log do custo) por ano no "
            f"período {ano_min}–{ano_max}{org_txt}, o custo médio de treinar um modelo "
            "saiu de ",
            html.Strong(f"US$ {primeiro['media_usd']:,.0f}"),
            f" em {int(primeiro['ano'])} para ",
            html.Strong(f"US$ {ultimo['media_usd']:,.0f}"),
            f" em {int(ultimo['ano'])}",
            " — um aumento de " if cresc >= 1 else " — uma variação de ",
            html.Strong(f"{cresc:,.1f}×"),
            f" em {anos_span} ano(s). " if anos_span else ". ",
            "Os intervalos de confiança são mais largos onde há poucos modelos "
            "catalogados e mais estreitos onde a amostra é maior.",
        ])
    elif len(res) == 1:
        unico = res.iloc[0]
        texto = html.P([
            f"No ano {int(unico['ano'])}{org_txt}, o custo médio geométrico foi de ",
            html.Strong(f"US$ {unico['media_usd']:,.0f}"),
            f" (IC 95%: US$ {unico['li_usd']:,.0f} – US$ {unico['ls_usd']:,.0f}, "
            f"n = {int(unico['n'])} modelos). Amplie o intervalo ou troque a "
            "organização para ver a tendência ao longo do tempo.",
        ])
    else:
        texto = html.P(f"Não há modelos com custo estimado no filtro selecionado{org_txt}. "
                       "Amplie o intervalo de anos ou escolha 'Todas' as organizações.")

    return fig_custo, fig_top, texto
