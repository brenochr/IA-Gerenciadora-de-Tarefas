from flask import Flask, render_template, request, jsonify
import json
import os
from interpretador import interpretar_texto   # ← usamos o interpretador externo

app = Flask(__name__)

ARQUIVO_DADOS = "dados.json"


# ============================================================
#  FUNÇÕES DE LEITURA E ESCRITA DO JSON
# ============================================================

def carregar_dados():
    """Lê o arquivo JSON e retorna uma lista de tarefas."""
    if not os.path.exists(ARQUIVO_DADOS):
        return []

    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def salvar_dados(lista):
    """Salva a lista completa de tarefas no JSON."""
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
    """Retorna todas as tarefas salvas no JSON."""
    return jsonify(carregar_dados())


@app.route("/api/processar", methods=["POST"])
def processar():
    """
    Recebe o texto do usuário,
    envia para o interpretador,
    salva no JSON,
    retorna as novas tarefas.
    """
    dados = request.get_json()
    texto = dados.get("texto", "")

    # 1. Interpretar o texto (linguagem natural ou JSON estruturado)
    novas_tarefas = interpretar_texto(texto)

    # 2. Carregar tarefas existentes
    tarefas_existentes = carregar_dados()

    # 3. Adicionar as novas tarefas
    tarefas_existentes.extend(novas_tarefas)

    # 4. Salvar no JSON
    salvar_dados(tarefas_existentes)

    # 5. Retornar para o front-end
    return jsonify(novas_tarefas)


# ============================================================
#  EXECUÇÃO DO SERVIDOR
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
