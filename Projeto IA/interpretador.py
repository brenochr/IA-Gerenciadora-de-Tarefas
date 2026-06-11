import json
import re
from datetime import datetime

# ============================================================
#  INTERPRETADOR PRINCIPAL
# ============================================================

def interpretar_texto(texto):
    """
    Interpreta o texto enviado pelo usuário OU pela IA.
    Pode receber:
    - linguagem natural ("entregar o projeto dia 14 prioridade alta")
    - JSON estruturado ({"acao": "adicionar", ...})
    Retorna SEMPRE uma lista de tarefas no formato:
    [
        {
            "titulo": "...",
            "prazo": "YYYY-MM-DD",
            "prioridade": "alta/média/baixa"
        }
    ]
    """

    texto = texto.strip()

    # 1. Tentar interpretar como JSON estruturado
    comando = tentar_interpretar_json(texto)
    if comando:
        return [comando]

    # 2. Interpretar linguagem natural
    return interpretar_linguagem_natural(texto)


# ============================================================
#  INTERPRETAÇÃO DE JSON ESTRUTURADO (para IA)
# ============================================================

def tentar_interpretar_json(texto):
    """
    Tenta interpretar o texto como JSON.
    Se for válido e contiver 'acao': 'adicionar',
    retorna um dicionário de tarefa.
    Caso contrário, retorna None.
    """
    try:
        dados = json.loads(texto)

        if isinstance(dados, dict) and dados.get("acao") == "adicionar":
            return {
                "titulo": dados.get("titulo", "").strip(),
                "prazo": dados.get("prazo", "").strip(),
                "prioridade": dados.get("prioridade", "baixa").strip()
            }

    except Exception:
        pass

    return None


# ============================================================
#  INTERPRETAÇÃO DE LINGUAGEM NATURAL (usuário humano)
# ============================================================

def interpretar_linguagem_natural(texto):
    texto_original = texto
    texto = texto.lower()

    # ---------------------------
    # PRIORIDADE
    # ---------------------------
    if "alta" in texto:
        prioridade = "alta"
    elif "média" in texto or "media" in texto:
        prioridade = "média"
    else:
        prioridade = "baixa"

    # ---------------------------
    # DIA (número no texto)
    # ---------------------------
    numeros = re.findall(r"\b(\d{1,2})\b", texto)
    dia = int(numeros[0]) if numeros else datetime.now().day

    # ---------------------------
    # MÊS E ANO (atuais)
    # ---------------------------
    hoje = datetime.now()
    prazo = f"{hoje.year}-{hoje.month:02d}-{dia:02d}"

    # ---------------------------
    # TÍTULO (texto sem números e sem prioridade)
    # ---------------------------
    titulo = texto_original
    titulo = re.sub(r"\b\d{1,2}\b", "", titulo)
    titulo = titulo.replace("alta", "").replace("média", "").replace("media", "").replace("baixa", "")
    titulo = titulo.strip()

    if titulo == "":
        titulo = "Tarefa"

    return [{
        "titulo": titulo,
        "prazo": prazo,
        "prioridade": prioridade
    }]
