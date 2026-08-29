"""
Salvar recomendacao no banco de dados SQLite
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("C:/precision_vrt_solo")
DB_PATH = BASE_DIR / "dados_agri.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def salvar_recomendacao(cliente_id, equipe_id, talhao, cultura, produtividade_alvo, area_ha, detalhes, custo_total, faturamento=0):
    """Salva recomendacao no SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recomendacoes (cliente_id, equipe_id, talhao, cultura, produtividade_alvo, area_ha, data_calculo, detalhes, custo_total, faturamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cliente_id, equipe_id, talhao, cultura, produtividade_alvo, area_ha, datetime.now().isoformat(), json.dumps(detalhes, ensure_ascii=False), custo_total, faturamento))
    conn.commit()
    rec_id = cursor.lastrowid
    conn.close()
    return rec_id

def listar_recomendacoes_por_periodo(meses=6):
    """Retorna recomendacoes dos ultimos N meses."""
    conn = get_connection()
    cursor = conn.cursor()
    from datetime import timedelta
    data_limite = (datetime.now() - timedelta(days=30*meses)).isoformat()
    cursor.execute('''
        SELECT r.*, c.nome as cliente_nome, e.nome as equipe_nome
        FROM recomendacoes r
        LEFT JOIN clientes c ON r.cliente_id = c.id
        LEFT JOIN equipe e ON r.equipe_id = e.id
        WHERE r.data_calculo > ?
        ORDER BY r.data_calculo DESC
    ''', (data_limite,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def calcular_metricas_financeiras(meses=6):
    """Calcula faturamento, custos e lucro do periodo."""
    recs = listar_recomendacoes_por_periodo(meses)
    
    # Agrupar por mes
    from collections import defaultdict
    
    dados_mensais = defaultdict(lambda: {"faturamento": 0, "custo_total": 0, "comissao": 0})
    
    for rec in recs:
        data = datetime.fromisoformat(rec["data_calculo"].replace("Z", "+00:00"))
        mes_ano = f"{data.year}-{data.month:02d}"
        
        # Faturamento = custo_total + margem (assumir 40% margem)
        faturamento = rec["faturamento"] or (rec["custo_total"] * 1.4 if rec["custo_total"] else 0)
        dados_mensais[mes_ano]["faturamento"] += faturamento
        dados_mensais[mes_ano]["custo_total"] += rec["custo_total"] or 0
        
        # Comissao
        if rec["equipe_id"]:
            from equipe_manager import buscar_funcionario
            func = buscar_funcionario(rec["equipe_id"])
            if func:
                comissao = faturamento * (func["percentual_comissao"] / 100)
                dados_mensais[mes_ano]["comissao"] += comissao
    
    # Converter para lista ordenada
    resultado = []
    for mes in sorted(dados_mensais.keys()):
        faturamento = dados_mensais[mes]["faturamento"]
        custo_total = dados_mensais[mes]["custo_total"] + dados_mensais[mes]["comissao"]
        lucro = faturamento - custo_total
        resultado.append({
            "mes": mes,
            "faturamento": round(faturamento, 2),
            "custo_total": round(custo_total, 2),
            "lucro": round(lucro, 2)
        })
    
    return resultado
