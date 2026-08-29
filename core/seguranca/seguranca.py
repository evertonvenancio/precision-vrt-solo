"""Modulo de seguranca do Precision VRT Solo.

Responsavel por hash de senhas, verificacao de credenciais,
registro de auditoria e gerenciamento de permissoes granular.
"""

import hashlib
import json
import logging
import os
import sqlite3
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuracao do banco de dados
# ---------------------------------------------------------------------------

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "precision_vrt.db")


def _get_connection() -> sqlite3.Connection:
    """Retorna uma conexao com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Hash de Senha
# ---------------------------------------------------------------------------

def hash_senha(senha: str) -> str:
    """Retorna o hash SHA-256 da senha."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Verificacao de Senha (Popup de Seguranca)
# ---------------------------------------------------------------------------

def verificar_senha_popup(usuario_id: str, senha_input: str) -> bool:
    """Verifica se a senha informada corresponde ao hash armazenado.

    Args:
        usuario_id: ID do usuario (String/UUID).
        senha_input: Senha em texto plano para verificar.

    Returns:
        True se a senha for correta, False caso contrario.
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT senha_hash FROM usuarios WHERE id = ?",
            (str(usuario_id),),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            logger.warning("Usuario nao encontrado para verificacao: %s", usuario_id)
            return False

        senha_hash = row["senha_hash"]
        return hash_senha(senha_input) == senha_hash

    except Exception as exc:
        logger.error("Erro ao verificar senha: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Auditoria
# ---------------------------------------------------------------------------

def registrar_auditoria(
    usuario_id: str,
    acao: str,
    detalhes: str,
    justificativa: str = "",
) -> bool:
    """Registra uma acao no log de auditoria.

    Args:
        usuario_id: ID do usuario que executou a acao.
        acao: Tipo da acao (ex: EDICAO_CLIENTE).
        detalhes: Descricao detalhada da acao.
        justificativa: Justificativa fornecida pelo usuario.

    Returns:
        True se registrado com sucesso, False caso contrario.
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO logs_auditoria (usuario_id, acao, detalhes, justificativa)
            VALUES (?, ?, ?, ?)
            """,
            (str(usuario_id), acao, detalhes, justificativa),
        )
        conn.commit()
        conn.close()
        logger.info("Auditoria registrada: %s - %s", acao, detalhes)
        return True

    except Exception as exc:
        logger.error("Erro ao registrar auditoria: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Permissoes
# ---------------------------------------------------------------------------

def permissoes_padrao() -> Dict[str, bool]:
    """Retorna o dicionario de permissoes padrao (tudo liberado para admin).

    Returns:
        Dict com todas as chaves de permissao definidas como True.
    """
    return {
        "view_menu_inicio": True,
        "view_menu_clientes": True,
        "view_menu_recomendacao": True,
        "view_menu_conhecimento": True,
        "view_menu_financeiro": True,
        "view_menu_equipe": True,
        "view_menu_configuracoes": True,
        "view_menu_ativos": True,
        "total": True,
    }


def salvar_permissoes_usuario(
    usuario_id: str,
    permissoes: Dict[str, bool],
) -> Tuple[bool, str]:
    """Salva o dicionario de permissoes no campo JSON do usuario.

    Args:
        usuario_id: ID do usuario (String/UUID).
        permissoes: Dicionario de permissoes booleanas.

    Returns:
        Tupla (sucesso: bool, mensagem: str).
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET permissoes = ? WHERE id = ?",
            (json.dumps(permissoes), str(usuario_id)),
        )
        conn.commit()
        conn.close()
        logger.info("Permissoes salvas para usuario: %s", usuario_id)
        return True, "Permissoes salvas com sucesso."

    except Exception as exc:
        logger.error("Erro ao salvar permissoes: %s", exc)
        return False, f"Erro ao salvar permissoes: {exc}"


def carregar_permissoes_usuario(usuario_id: str) -> Dict[str, bool]:
    """Carrega as permissoes do usuario do banco.

    Se o campo permissoes for nulo, vazio ou JSON invalido,
    retorna permissoes_padrao().

    Args:
        usuario_id: ID do usuario (String/UUID) ou objeto Usuario.

    Returns:
        Dicionario de permissoes booleanas.
    """
    # Se receber um objeto (ex: SQLAlchemy model), extrai o ID
    if hasattr(usuario_id, "id"):
        usuario_id = str(usuario_id.id)

    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT permissoes FROM usuarios WHERE id = ?",
            (str(usuario_id),),
        )
        row = cursor.fetchone()
        conn.close()

        if not row or not row["permissoes"]:
            logger.info("Permissoes nao encontradas para usuario %s. Usando padrao.", usuario_id)
            return permissoes_padrao()

        permissoes = json.loads(row["permissoes"])
        if not isinstance(permissoes, dict):
            logger.warning("Formato invalido de permissoes para usuario %s. Usando padrao.", usuario_id)
            return permissoes_padrao()

        return permissoes

    except json.JSONDecodeError:
        logger.warning("JSON invalido nas permissoes do usuario %s. Usando padrao.", usuario_id)
        return permissoes_padrao()

    except Exception as exc:
        logger.error("Erro ao carregar permissoes: %s", exc)
        return permissoes_padrao()


def check_permission_seguranca(chave: str, permissoes: Dict[str, bool]) -> bool:
    """Verifica se uma permissao especifica esta liberada.

    Se o usuario tiver permissao "total", retorna True automaticamente.

    Args:
        chave: Nome da permissao a verificar.
        permissoes: Dicionario de permissoes do usuario.

    Returns:
        True se permitido, False caso contrario.
    """
    if permissoes.get("total", False):
        return True
    return permissoes.get(chave, False)