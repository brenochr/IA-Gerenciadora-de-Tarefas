import json
import re
from datetime import datetime

# ============================================================
#  INTERPRETADOR PRINCIPAL
# ============================================================

def interpretar_texto(texto):
    """
    Interpreta o texto enviado pela IA ou pelo usuário.
    Retorna SEMPRE uma lista contendo UM comando válido.
    """

    texto = texto.strip()

    # 1. Tentar interpretar como JSON estruturado (IA)
    comando = tentar_interpretar_json(texto)
    if comando:
        return [corrigir_comando(comando)]

    # 2. Interpretar linguagem natural (usuário humano)
    tarefa = interpretar_linguagem_natural(texto)
    return [corrigir_comando(tarefa)]


# ============================================================
#  INTERPRETAÇÃO DE JSON ESTRUTURADO (IA)
# ============================================================

def tentar_interpretar_json(texto):
    """
    Extrai JSON mesmo que a IA envie texto antes/depois.
    Retorna um dicionário com o comando ou None.
    """

    try:
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if not match:
            return None

        dados = json.loads(match.group(0))
        acao = dados.get("acao")

        # ADICIONAR
        if acao == "adicionar":
            return {
                "acao": "adicionar",
                "titulo": dados.get("titulo", "").strip(),
                "prazo": dados.get("prazo", "").strip(),
                "prioridade": dados.get("prioridade", "").strip()
            }

        # ADIAR
        if acao == "adiar":
            return {
                "acao": "adiar",
                "titulo": dados.get("titulo", "").strip(),
                "novo_prazo": dados.get("novo_prazo", "").strip()
            }

        # EDITAR
        if acao == "editar":
            return {
                "acao": "editar",
                "titulo_antigo": dados.get("titulo_antigo", "").strip(),
                "titulo_novo": dados.get("titulo_novo", "").strip()
            }

        # REMOVER
        if acao == "remover":
            return {
                "acao": "remover",
                "titulo": dados.get("titulo", "").strip()
            }

    except:
        return None

    return None


# ============================================================
#  CORREÇÃO DE COMANDOS (SAFEGUARD FINAL)
# ============================================================

def corrigir_comando(cmd):
    """
    Garante que o comando seja válido e seguro.
    """

    hoje = datetime.now().date()
    acao = cmd.get("acao")

    # ---------------------------
    # ADICIONAR
    # ---------------------------
    if acao == "adicionar":
        titulo = cmd.get("titulo", "").strip()
        if titulo == "":
            titulo = "Tarefa"

        prioridade = cmd.get("prioridade", "").lower()
        if prioridade not in ["alta", "média", "media", "baixa"]:
            prioridade = "baixa"
        if prioridade == "media":
            prioridade = "média"

        try:
            prazo = datetime.strptime(cmd.get("prazo", ""), "%Y-%m-%d").date()
        except:
            prazo = hoje

        if prazo < hoje:
            prazo = prazo.replace(year=hoje.year + 1)

        return {
            "acao": "adicionar",
            "titulo": titulo,
            "prazo": prazo.strftime("%Y-%m-%d"),
            "prioridade": prioridade
        }

    # ---------------------------
    # ADIAR
    # ---------------------------
    if acao == "adiar":
        titulo = cmd.get("titulo", "").strip()
        if titulo == "":
            titulo = "Tarefa"

        try:
            novo = datetime.strptime(cmd.get("novo_prazo", ""), "%Y-%m-%d").date()
        except:
            novo = hoje

        if novo < hoje:
            novo = novo.replace(year=hoje.year + 1)

        return {
            "acao": "adiar",
            "titulo": titulo,
            "novo_prazo": novo.strftime("%Y-%m-%d")
        }

    # ---------------------------
    # EDITAR
    # ---------------------------
    if acao == "editar":
        antigo = cmd.get("titulo_antigo", "").strip()
        novo = cmd.get("titulo_novo", "").strip()

        if antigo == "":
            antigo = "Tarefa"
        if novo == "":
            novo = "Tarefa"

        return {
            "acao": "editar",
            "titulo_antigo": antigo,
            "titulo_novo": novo
        }

    # ---------------------------
    # REMOVER
    # ---------------------------
    if acao == "remover":
        titulo = cmd.get("titulo", "").strip()
        if titulo == "":
            titulo = "Tarefa"

        return {
            "acao": "remover",
            "titulo": titulo
        }

    return cmd


# ============================================================
#  INTERPRETAÇÃO DE LINGUAGEM NATURAL (usuário humano)
# ============================================================

def interpretar_linguagem_natural(texto):
    """
    Linguagem natural só cria tarefas (adicionar).
    """
    texto_original = texto
    texto = texto.lower()

    # PRIORIDADE
    if "alta" in texto:
        prioridade = "alta"
    elif "média" in texto or "media" in texto:
        prioridade = "média"
    else:
        prioridade = "baixa"

    # DIA
    numeros = re.findall(r"\b(\d{1,2})\b", texto)
    dia = int(numeros[0]) if numeros else datetime.now().day

    # MÊS E ANO
    hoje = datetime.now()
    prazo = f"{hoje.year}-{hoje.month:02d}-{dia:02d}"

    # TÍTULO
    titulo = texto_original
    titulo = re.sub(r"\b\d{1,2}\b", "", titulo)
    titulo = titulo.replace("alta", "").replace("média", "").replace("media", "").replace("baixa", "")
    titulo = titulo.strip()

    if titulo == "":
        titulo = "Tarefa"

    return {
        "acao": "adicionar",
        "titulo": titulo,
        "prazo": prazo,
        "prioridade": prioridade
    }
