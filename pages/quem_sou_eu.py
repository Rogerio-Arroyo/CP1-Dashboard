"""Aba 1 — Quem sou eu"""
import dash
from dash import html

dash.register_page(__name__, path="/", name="Quem sou eu", order=1)

NOME = "Rogério Cruz Arroyo"
CARGO = "Estagiário de SRE OPS / Observabilidade"
EMPRESA_OU_INSTITUICAO = "Banco Pan e BTG"
CIDADE = "São Paulo, SP"
EMAIL = "rogerio.cruz.arroyo@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/rogério-arroyo"
GITHUB = "https://github.com/Rogerio-Arroyo"

FOTO_URL = "/assets/foto.jpg"

# Formações exibidas com o logo da instituição ao lado
FORMACOES = [
    {
        "curso": "Engenharia de Software",
        "instituicao": "FIAP",
        "logo": "/assets/fiap.png",
        "detalhe": "2º semestre · Turma 2ESPH",
    },
    {
        "curso": "Engenharia da Computação",
        "instituicao": "UNIVESP",
        "logo": "/assets/univesp.png",
        "detalhe": "Universidade Virtual do Estado de São Paulo",
    },
]

MINI_BIO = """\
Sou estudante de Engenharia de Software na FIAP e de Engenharia da \
Computação na UNIVESP. Atualmente trabalho como Estagiário de SRE \
OPS / Observabilidade no Banco Pan e BTG. Tenho interesse em dados, \
desenvolvimento web e inteligência artificial. Este portfólio reúne \
minhas qualificações e uma análise de dados que fiz sobre a adoção \
de IA no mercado de tecnologia.
"""


def _formacao_item(f):
    return html.Div(
        className="formacao-linha",
        children=[
            html.Img(src=f["logo"], alt=f["instituicao"], className="formacao-logo"),
            html.Div(
                className="formacao-info",
                children=[
                    html.Div(f["curso"], className="formacao-curso"),
                    html.Div(f["instituicao"], className="formacao-inst"),
                    html.Div(f["detalhe"], className="formacao-detalhe"),
                ],
            ),
        ],
    )


def layout():
    return html.Div(
        className="page page-quem",
        children=[
            html.Section(
                className="hero",
                children=[
                    html.Div(
                        className="hero-photo",
                        children=[
                            html.Img(src=FOTO_URL, alt="Foto de perfil"),
                        ],
                    ),
                    html.Div(
                        className="hero-text",
                        children=[
                            html.H1(NOME),
                            html.H3(CARGO),
                            html.P(
                                [
                                    html.Strong("Empresa: "),
                                    EMPRESA_OU_INSTITUICAO,
                                ]
                            ),
                            html.P([html.Strong("Cidade: "), CIDADE]),
                            html.Div(
                                className="contacts",
                                children=[
                                    html.A("✉ " + EMAIL, href=f"mailto:{EMAIL}"),
                                    html.A("in LinkedIn", href=LINKEDIN, target="_blank"),
                                    html.A("gh GitHub", href=GITHUB, target="_blank"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Section(
                className="card",
                children=[
                    html.H2("Formação"),
                    html.Div(
                        className="formacoes",
                        children=[_formacao_item(f) for f in FORMACOES],
                    ),
                ],
            ),
            html.Section(
                className="card",
                children=[
                    html.H2("Mini-bio"),
                    html.P(MINI_BIO, style={"whiteSpace": "pre-wrap"}),
                ],
            ),
            html.Section(
                className="card",
                children=[
                    html.H2("Sobre este dashboard"),
                    html.P(
                        "Este dashboard foi desenvolvido individualmente como entrega do "
                        "CP1 da disciplina Data Science and Statistical Computing. Ele "
                        "reúne minhas qualificações profissionais e uma análise de dados "
                        "aplicada sobre a adoção de inteligência artificial no mercado "
                        "de desenvolvimento de software — combinando dois datasets públicos "
                        "e reais para responder à pergunta: até que ponto o boom da IA está "
                        "consolidado, e o que os dados dizem sobre ele?"
                    ),
                    html.P(
                        "Navegue pelas abas acima para conhecer meu perfil e explorar a análise."
                    ),
                ],
            ),
        ],
    )
