from flask import Flask, render_template, request, jsonify
import json
import os
import re
from interpretador import interpretar_texto
from datetime import datetime, timedelta
from groq import Groq
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

app = Flask(__name__)

ARQUIVO_DADOS = "dados.json"

# Inicializa cliente Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ============================================================
#  FUNÇÃO PARA CHAMAR A IA DO GROQ (COM SAFEGUARDS)
# ============================================================

def chamar_llm(prompt):
    resposta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta.choices[0].message.content


# ============================================================
#  FUNÇÕES DE LEITURA E ESCRITA DO JSON
# ============================================================

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return []

    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def salvar_dados(lista):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)


# ============================================================
#  ROTAS DO FLASK
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tarefas", methods=["GET"])
def listar_tarefas():
    tarefas = carregar_dados()

    hoje = datetime.now().date()
    limite_passado = hoje - timedelta(days=7)

    tarefas_ativas = []
    tarefas_passadas = []

    for t in tarefas:
        prazo = datetime.strptime(t["prazo"], "%Y-%m-%d").date()

        if prazo < limite_passado:
            continue

        if prazo < hoje:
            tarefas_passadas.append(t)
        else:
            tarefas_ativas.append(t)

    salvar_dados(tarefas_ativas + tarefas_passadas)

    return jsonify({
        "ativas": tarefas_ativas,
        "passadas": tarefas_passadas
    })


@app.route("/api/processar", methods=["POST"])
def processar():
    dados = request.get_json()
    texto = dados.get("texto", "")

    ano_atual = datetime.now().year

    # ============================================================
    # 1. Prompt seguro para IA
    # ============================================================

    prompt = f"""
Converta o texto abaixo em um JSON de comando **puro**, sem explicações, sem comentários e sem texto adicional.

O JSON deve ser EXATAMENTE um destes formatos:

1) ADICIONAR:
{{
    "acao": "adicionar",
    "titulo": "...",
    "prazo": "YYYY-MM-DD",
    "prioridade": "alta" | "média" | "baixa"
}}

2) ADIAR:
{{
    "acao": "adiar",
    "titulo": "...",
    "novo_prazo": "YYYY-MM-DD"
}}

3) EDITAR:
{{
    "acao": "editar",
    "titulo_antigo": "...",
    "titulo_novo": "..."
}}

4) REMOVER:
{{
    "acao": "remover",
    "titulo": "..."
}}

REGRAS IMPORTANTES:
- Use SEMPRE o ano atual ({ano_atual}), a menos que o usuário especifique outro ano explicitamente.
- Nunca use datas no passado. Se o usuário pedir uma data passada, ajuste para o próximo ano.
- Nunca deixe campos vazios.
- Nunca escreva observações fora do JSON.
- O JSON deve ser a ÚNICA coisa na resposta.

Texto do usuário: "{texto}"
"""

    resposta_ia = chamar_llm(prompt)

    # ============================================================
    # 2. Extrair apenas o JSON da resposta da IA
    # ============================================================

    match = re.search(r"\{.*\}", resposta_ia, re.DOTALL)
    if not match:
        return jsonify({"erro": "A IA não retornou JSON válido."}), 400

    json_puro = match.group(0)

    # ============================================================
    # 3. Interpretador transforma JSON → objeto Python
    # ============================================================

    comando = interpretar_texto(json_puro)[0]
    acao = comando["acao"]

    # ============================================================
    # 4. Carregar tarefas existentes
    # ============================================================

    tarefas = carregar_dados()
    hoje = datetime.now().date()

    # ============================================================
    # 5. Aplicar comando
    # ============================================================

    # ADICIONAR
    if acao == "adicionar":
        prazo = datetime.strptime(comando["prazo"], "%Y-%m-%d").date()
        if prazo < hoje:
            prazo = prazo.replace(year=hoje.year + 1)
        comando["prazo"] = prazo.strftime("%Y-%m-%d")
        tarefas.append(comando)

    # ADIAR
    elif acao == "adiar":
        for t in tarefas:
            if t["titulo"].lower() == comando["titulo"].lower():
                novo = datetime.strptime(comando["novo_prazo"], "%Y-%m-%d").date()
                if novo < hoje:
                    novo = novo.replace(year=hoje.year + 1)
                t["prazo"] = novo.strftime("%Y-%m-%d")

    # EDITAR
    elif acao == "editar":
        for t in tarefas:
            if t["titulo"].lower() == comando["titulo_antigo"].lower():
                t["titulo"] = comando["titulo_novo"]

    # REMOVER
    elif acao == "remover":
        tarefas = [
            t for t in tarefas
            if t["titulo"].lower() != comando["titulo"].lower()
        ]

    # ============================================================
    # 6. Salvar no JSON
    # ============================================================

    salvar_dados(tarefas)

    return jsonify([comando])


# ============================================================
#  EXECUÇÃO DO SERVIDOR
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
