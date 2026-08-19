"""Aba 2 — Minhas Qualificações"""
import dash
from dash import html

dash.register_page(__name__, path="/qualificacoes", name="Qualificações", order=2)

# ==================================================================
# TODO: PERSONALIZE COM SUAS QUALIFICAÇÕES REAIS
# ==================================================================

FORMACAO = [
    {
        "curso": "Engenharia de Software",
        "instituicao": "FIAP",
        "periodo": "2025 – 2028 (previsto)",
        "descricao": "Bacharelado com ênfase em desenvolvimento de sistemas, "
                     "ciência de dados e engenharia de software.",
    },
    {
        "curso": "Engenharia da Computação",
        "instituicao": "UNIVESP — Universidade Virtual do Estado de São Paulo",
        "periodo": "2025 – 2029 (previsto)",
        "descricao": "Bacharelado com ênfase em desenvolvimento de hardware e "
                     "sistemas computacionais.",
    },
]

CURSOS_CERTIFICACOES = [
    {"nome": "Estruturas de Computadores", "instituicao": "FIAP",
     "ano": "abr/2025", "carga": "Nanocourse",
     "link": "https://on.fiap.com.br/local/nanocourses/gerar_certificado.php?chave=95fcfc432172b497b52569c783f6cd5e&action=view"},
    {"nome": "Design Thinking – Process", "instituicao": "FIAP",
     "ano": "mar/2025", "carga": "Nanocourse",
     "link": "https://on.fiap.com.br/local/nanocourses/gerar_certificado.php?chave=7e15401cf0a8860ddec5422ab4665462&action=view"},
    {"nome": "Formação Social e Sustentabilidade", "instituicao": "FIAP",
     "ano": "fev/2025", "carga": "Nanocourse",
     "link": "https://on.fiap.com.br/local/nanocourses/gerar_certificado.php?chave=2b63fc3503c28b4d882637cf23235af9&action=view"},
]

PROJETOS = [
    {
        "nome": "Stratfy — Projetos Acadêmicos FIAP",
        "papel": "Membro do grupo Stratfy",
        "descricao": "Participação em projetos multidisciplinares da graduação: "
                     "Global Solution (SAFS, SOMA-Fogo), Challenge (NORA), entre outros.",
    },
]
EXPERIENCIAS = [
    {
        "cargo": "Estagiario",
        "empresa": "Banco PAN BTG",
        "periodo": "02/11/2025",
        "atividades": [
            "Observabilidade",
            "Monitoração do ambiente",
            "Desenvolvimento de processo e automações",
        ],
    },
]


def _card_formacao(f):
    return html.Div(
        className="qual-item",
        children=[
            html.H3(f["curso"]),
            html.Div(f["instituicao"], className="qual-inst"),
            html.Div(f["periodo"], className="qual-periodo"),
            html.P(f["descricao"]),
        ],
    )


def _card_curso(c):
    conteudo = [
        html.H4(c["nome"]),
        html.Div(f"{c['instituicao']} • {c['ano']} • {c['carga']}",
                 className="curso-meta"),
    ]
    if c.get("link"):
        conteudo.append(
            html.Span("Exibir credencial ↗", className="curso-link-badge")
        )
        return html.A(
            className="curso-card curso-card-link",
            href=c["link"], target="_blank", children=conteudo,
        )
    return html.Div(className="curso-card", children=conteudo)


def _card_projeto(p):
    return html.Div(
        className="proj-card",
        children=[
            html.H4(p["nome"]),
            html.Div(p["papel"], className="proj-papel"),
            html.P(p["descricao"]),
        ],
    )


def _card_exp(e):
    return html.Div(
        className="exp-card",
        children=[
            html.H4(e["cargo"]),
            html.Div(f"{e['empresa']} • {e['periodo']}", className="exp-meta"),
            html.Ul([html.Li(a) for a in e["atividades"]]),
        ],
    )


def layout():
    return html.Div(
        className="page page-qual",
        children=[
            html.H1("Minhas Qualificações"),

            html.Section(
                className="card",
                children=[
                    html.H2("Formação Acadêmica"),
                    html.Div([_card_formacao(f) for f in FORMACAO],
                             className="qual-list"),
                ],
            ),

            html.Section(
                className="card",
                children=[
                    html.H2("Cursos e Certificações"),
                    html.Div([_card_curso(c) for c in CURSOS_CERTIFICACOES],
                             className="cursos-grid"),
                ],
            ),

            html.Section(
                className="card",
                children=[
                    html.H2("Projetos Relevantes"),
                    html.Div([_card_projeto(p) for p in PROJETOS],
                             className="projs-grid"),
                ],
            ),

            html.Section(
                className="card",
                children=[
                    html.H2("Experiência Profissional"),
                    html.Div([_card_exp(e) for e in EXPERIENCIAS],
                             className="exps-list"),
                ],
            ),
        ],
    )
