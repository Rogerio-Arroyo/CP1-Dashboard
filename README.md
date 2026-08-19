# CP1 — Dashboard Profissional com Análise de Dados

Dashboard individual desenvolvido em **Dash (Plotly)** para o Checkpoint 1 da
disciplina *Data Science and Statistical Computing* — FIAP, turma 2ESPH.

> **Framework:** Dash — habilita o **+1 ponto extra** previsto no enunciado.

---

## Estrutura do projeto

```
cp1-dashboard/
├── app.py                            # entry point Dash (multi-página)
├── pages/
│   ├── quem_sou_eu.py                # Aba 1
│   ├── qualificacoes.py              # Aba 2
│   ├── skills.py                     # Aba 3
│   └── analise_dados.py              # Aba 4 (análise + IC)
├── data/
│   ├── epoch_ai_models.csv           # Dataset 1: Epoch AI
│   ├── so_survey_2024.csv            # Dataset 2: Stack Overflow Survey 2024
│   ├── so_survey_2024_questions.csv  # Metadados: perguntas
│   └── so_survey_2024_crosswalk.csv  # Metadados: labels das respostas
├── assets/
│   └── style.css                     # tema escuro
├── requirements.txt
├── Procfile                          # deploy (Render/Railway)
├── runtime.txt                       # versão Python p/ deploy
└── README.md
```

---

## Rodando localmente

```bash
# 1. Criar ambiente virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate       # no Windows: .venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar o app
python app.py
```

Abra <http://localhost:8050> no navegador.

---

## Personalizando as abas pessoais

Antes de hospedar, **edite os placeholders** marcados como `<<...>>` e `TODO`
nos três arquivos:

- `pages/quem_sou_eu.py` — nome, cargo, empresa, mini-bio, links, foto
- `pages/qualificacoes.py` — formação, cursos, projetos, experiência
- `pages/skills.py` — linguagens, frameworks, bancos, soft skills, idiomas

**Foto de perfil:** salve como `assets/foto.jpg` (o CSS já corta em círculo).

A aba `pages/analise_dados.py` **não precisa ser alterada** — a análise já
está pronta e é a parte que vale 7,0 dos 10,0 pontos.

---

## Hospedagem (grátis)

O enunciado exige o dashboard hospedado e funcionando. Opção mais rápida:

### Render.com (gratuito)

1. Suba este projeto para um repositório no GitHub.
2. Acesse <https://render.com>, crie conta grátis e clique em **New → Web Service**.
3. Conecte seu GitHub e escolha o repositório.
4. Configuração:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:server --bind 0.0.0.0:$PORT --timeout 120`
5. Clique em **Create Web Service**. O deploy leva ~3 minutos.
6. Você recebe uma URL pública tipo `https://seu-projeto.onrender.com`.

O `Procfile` já está configurado — o Render detecta automaticamente.

### Alternativas
- **Railway.app** — mesma lógica, também grátis.
- **PythonAnywhere** — grátis com URL do tipo `usuario.pythonanywhere.com`.

---

## Análise de Dados — resumo técnico

**Tema:** o boom da IA em duas frentes: (1) custo crescente de treinar modelos e (2) adoção acelerada por desenvolvedores.

**Datasets reais e públicos:**

| Dataset | Fonte | Linhas | O que traz |
|---|---|---|---|
| Epoch AI — Data on AI Models | [epoch.ai/data/ai-models](https://epoch.ai/data/ai-models) | 1.755 modelos | Custo estimado de treinamento (USD 2023), FLOPs, parâmetros, organização, data |
| Stack Overflow Developer Survey 2024 | [survey.stackoverflow.co/2024](https://survey.stackoverflow.co/2024/) | 65.437 devs | Uso de IA, sentimento, confiança, salário, país, tipo de dev |

**Estatística inferencial aplicada:**

- **IC para média** — distribuição t de Student (adequado para n pequeno)
- **IC para proporção** — método de Wilson (mais robusto que Wald)
- **IC para diferença de médias** — teste t de Welch (variâncias desiguais)

**Perguntas respondidas:**

1. Qual a magnitude e velocidade do aumento do custo de treinamento de modelos?
2. Que proporção de devs usa IA hoje? A adoção varia entre países?
3. Adoção significa aceitação — como devs se sentem sobre IA?
4. Devs que usam IA ganham mais? A diferença é estatisticamente significativa?

**Principais conclusões:**

- Custo médio de treinamento cresceu ~13.000× entre 2015 e 2023 (US$ 206 → US$ 2,77M).
- **61,8%** dos devs no mundo usam IA (IC 95% [61,4% ; 62,2%], n=60.907).
- Brasil está acima da média com **66,0%** (IC 95% [63,4% ; 68,4%], n=1.367).
- Contraintuitivamente, devs que usam IA ganham em média **menos** que os que não usam — diferença estatisticamente significativa (IC não contém zero), provavelmente por confusão com senioridade e paridade cambial.

---

## Licenças dos dados

- **Epoch AI:** Creative Commons Attribution 4.0 (CC-BY 4.0)
- **Stack Overflow Survey:** Open Database License (ODbL)

Ambos são livres para uso acadêmico com atribuição.

---

## Créditos

Dashboard construído para a disciplina Data Science and Statistical Computing (FIAP 2ESPH), Prof. Eduardo dos Santos Ramos.
