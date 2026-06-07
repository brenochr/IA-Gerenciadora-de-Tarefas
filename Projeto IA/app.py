from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime, timedelta

app = Flask(__name__)

ARQUIVO_DADOS = "dados.json"


def carregar_dados():
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def salvar_dados(tarefas):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)


# IA SIMULADA — depois substituímos pela IA real
def interpretar_texto(texto):
    hoje = datetime.now().strftime("%Y-%m-%d")

    return [{
        "titulo": "Tarefa gerada pela IA",
        "prioridade": "alta",
        "prazo": hoje,
        "duracao_minutos": 60
    }]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tarefas", methods=["GET"])
def listar_tarefas():
    return jsonify(carregar_dados())


@app.route("/api/processar", methods=["POST"])
def processar():
    dados = request.json
    texto = dados.get("texto", "")

    tarefas_existentes = carregar_dados()
    novas_tarefas = interpretar_texto(texto)

    tarefas_existentes.extend(novas_tarefas)
    salvar_dados(tarefas_existentes)

    return jsonify(novas_tarefas)


if __name__ == "__main__":
    app.run(debug=True)
