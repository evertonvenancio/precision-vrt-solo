"""
Gerenciamento de Insumos - SQLite
"""

import sqlite3
import json
import copy
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("C:/precision_vrt_solo")
DB_PATH = BASE_DIR / "dados_agri.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def carregar_insumos():
    """Carrega todos os insumos do SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM insumos")
    rows = cursor.fetchall()
    conn.close()
    
    adubos = []
    corretivos = []
    for row in rows:
        item = dict(row)
        item["teores"] = json.loads(item["teores"]) if item["teores"] else {}
        if item["categoria"] == "Adubo":
            adubos.append(item)
        else:
            corretivos.append(item)
    
    return {"adubos": adubos, "corretivos": corretivos}

def listar_adubos():
    return carregar_insumos().get("adubos", [])

def listar_corretivos():
    return carregar_insumos().get("corretivos", [])

def listar_todos():
    dados = carregar_insumos()
    return dados.get("adubos", []) + dados.get("corretivos", [])

def adicionar_adubo(nome, teores, preco_kg):
    """Adiciona adubo ao SQLite."""
    novo_id = nome.lower().replace(" ", "_").replace("-", "_")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO insumos (id, categoria, nome, teores, preco_kg, preco_t, unidade, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (novo_id, "Adubo", nome, json.dumps(teores, ensure_ascii=False), preco_kg, None, "kg/ha", datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return novo_id

def adicionar_corretivo(nome, teores, preco_t):
    """Adiciona corretivo ao SQLite."""
    novo_id = nome.lower().replace(" ", "_").replace("-", "_")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO insumos (id, categoria, nome, teores, preco_kg, preco_t, unidade, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (novo_id, "Corretivo", nome, json.dumps(teores, ensure_ascii=False), None, preco_t, "t/ha", datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return novo_id

def remover_insumo(id_insumo):
    """Remove insumo pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM insumos WHERE id = ?", (id_insumo,))
    conn.commit()
    conn.close()
    return True

def buscar_insumo(id_insumo):
    """Busca insumo pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM insumos WHERE id = ?", (id_insumo,))
    row = cursor.fetchone()
    conn.close()
    if row:
        item = dict(row)
        item["teores"] = json.loads(item["teores"]) if item["teores"] else {}
        return item
    return None

def clonar_insumo_para_edicao(id_insumo):
    """Retorna copia profunda para edicao temporaria."""
    insumo = buscar_insumo(id_insumo)
    if insumo:
        return copy.deepcopy(insumo)
    return None
