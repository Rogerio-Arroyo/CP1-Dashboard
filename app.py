"""
CP1 — Dashboard Profissional com Análise de Dados
Disciplina: Data Science and Statistical Computing (FIAP 2ESPH)
Framework: Dash (Plotly) — +1 ponto extra
"""
import dash
from dash import Dash, html, dcc, page_container

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Portfólio | Dashboard Profissional",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)

server = app.server  # exposto para gunicorn (deploy no Render/Railway)

# ------------------------------------------------------------------
# NAVBAR — links para as 4 abas obrigatórias do enunciado
# ------------------------------------------------------------------
def make_navbar():
    links = [
        ("/", "Quem sou eu"),
        ("/qualificacoes", "Qualificações"),
        ("/skills", "Skills"),
        ("/analise", "Análise de Dados"),
    ]
    return html.Nav(
        className="navbar",
        children=[
            html.Div("PORTFÓLIO", className="brand"),
            html.Div(
                className="nav-links",
                children=[
                    dcc.Link(label, href=href, className="nav-link")
                    for href, label in links
                ],
            ),
        ],
    )


app.layout = html.Div(
    className="app",
    children=[
        make_navbar(),
        html.Main(page_container, className="content"),
        html.Footer(
            className="footer",
            children=[
                html.Span(
                    "CP1 — Data Science and Statistical Computing | FIAP 2ESPH | "
                    "Dashboard construído em Dash (Plotly)"
                ),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8050, debug=True)


