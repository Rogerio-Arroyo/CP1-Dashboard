"""Aba 3 — Skills"""
import dash
from dash import html
import plotly.graph_objects as go
from dash import dcc

dash.register_page(__name__, path="/skills", name="Skills", order=3)

# ==================================================================
# TODO: PERSONALIZE COM SUAS SKILLS REAIS
# Nível de 1 a 5 (1=iniciante, 5=avançado)
# ==================================================================

LINGUAGENS = [
    ("Python", 4),
    ("JavaScript", 3),
    ("Java", 3),
    ("SQL", 3),
    ("HTML/CSS", 4),
    ("TypeScript", 2),
]

FRAMEWORKS_FERRAMENTAS = [
    ("Dash / Plotly", 3),
    ("React", 3),
    ("Pandas / NumPy", 4),
    ("Git / GitHub", 4),
    ("Docker", 2),
    ("Streamlit", 3),
]

BANCOS_DADOS = [
    ("MySQL", 3),
    ("PostgreSQL", 3),
    ("MongoDB", 2),
    ("Oracle", 2),
]

SOFT_SKILLS = [
    "Trabalho em equipe",
    "Comunicação",
    "Aprendizado rápido",
    "Resolução de problemas",
    "Proatividade",
    "Pensamento analítico",
]

IDIOMAS = [
    ("Português", "Nativo"),
    ("Inglês", "Intermediário"),
    ("<<Outro>>", "<<Nível>>"),
]


def _bar_chart(titulo, dados, cor):
    """Gera gráfico de barras horizontais para skills técnicas."""
    labels = [d[0] for d in dados]
    values = [d[1] for d in dados]
    fig = go.Figure(
        data=[
            go.Bar(
                y=labels,
                x=values,
                orientation="h",
                marker=dict(color=cor),
                text=[f"{v}/5" for v in values],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Nível: %{x}/5<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=titulo,
        xaxis=dict(range=[0, 5.5], tickvals=[1, 2, 3, 4, 5]),
        yaxis=dict(autorange="reversed"),
        height=max(220, 45 * len(labels) + 80),
        margin=dict(l=10, r=30, t=50, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"),
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def layout():
    return html.Div(
        className="page page-skills",
        children=[
            html.H1("Skills"),

            html.Section(
                className="card",
                children=[
                    html.H2("Competências Técnicas"),
                    html.Div(
                        className="skills-grid",
                        children=[
                            _bar_chart("Linguagens de Programação", LINGUAGENS, "#4f8cff"),
                            _bar_chart("Frameworks & Ferramentas", FRAMEWORKS_FERRAMENTAS, "#5eead4"),
                            _bar_chart("Bancos de Dados", BANCOS_DADOS, "#f59e0b"),
                        ],
                    ),
                ],
            ),

            html.Section(
                className="card",
                children=[
                    html.H2("Soft Skills"),
                    html.Div(
                        className="soft-skills",
                        children=[
                            html.Span(s, className="pill") for s in SOFT_SKILLS
                        ],
                    ),
                ],
            ),

            html.Section(
                className="card",
                children=[
                    html.H2("Idiomas"),
                    html.Div(
                        className="idiomas",
                        children=[
                            html.Div(
                                className="idioma-item",
                                children=[
                                    html.Div(nome, className="idioma-nome"),
                                    html.Div(nivel, className="idioma-nivel"),
                                ],
                            )
                            for nome, nivel in IDIOMAS
                        ],
                    ),
                ],
            ),
        ],
    )
