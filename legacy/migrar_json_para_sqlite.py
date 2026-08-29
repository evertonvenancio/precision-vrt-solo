"""
Script de Migracao: JSON -> SQLite
Le arquivos .json existentes, transfere para SQLite, renomeia JSON para backup.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import shutil

BASE_DIR = Path("C:/precision_vrt_solo")
DB_PATH = BASE_DIR / "dados_agri.db"
CLIENTES_DIR = BASE_DIR / "clientes"
CONFIG_DIR = BASE_DIR / "config"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def migrar_clientes():
    """Migra clientes dos JSON para SQLite."""
    if not CLIENTES_DIR.exists():
        logging.info("Pasta de clientes nao existe. Pulando...")
        return 0
    
    conn = get_connection()
    cursor = conn.cursor()
    count = 0
    
    for pasta in CLIENTES_DIR.iterdir():
        if not pasta.is_dir():
            continue
        
        json_file = pasta / "dados_cliente.json"
        if not json_file.exists():
            continue
        
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                dados = json.load(f)
            
            cursor.execute('''
                INSERT OR REPLACE INTO clientes 
                (nome, cpf_cnpj, propriedade, cidade, telefone, email, area_total, safe_name, data_cadastro, pasta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados.get("nome", ""),
                dados.get("cpf_cnpj", ""),
                dados.get("propriedade", ""),
                dados.get("cidade", ""),
                dados.get("telefone", ""),
                dados.get("email", ""),
                dados.get("area_total", 0),
                dados.get("safe_name", pasta.name),
                dados.get("data_cadastro", datetime.now().isoformat()),
                str(pasta)
            ))
            count += 1
            
            # Renomear JSON para backup
            backup = json_file.with_suffix(".json_old")
            shutil.move(str(json_file), str(backup))
            logging.info(f"  ✓ Cliente '{dados.get('nome')}' migrado. JSON renomeado para .json_old")
            
        except Exception as e:
            logging.info(f"  ✗ Erro ao migrar {json_file}: {e}")
    
    conn.commit()
    conn.close()
    return count

def migrar_insumos():
    """Migra insumos do insumos_banco.json para SQLite."""
    json_path = CONFIG_DIR / "insumos_banco.json"
    if not json_path.exists():
        logging.info("insumos_banco.json nao encontrado. Pulando...")
        return 0
    
    conn = get_connection()
    cursor = conn.cursor()
    count = 0
    
    try:
        with open(json_path, "r", encoding="utf-8-sig") as f:
            dados = json.load(f)
        
        # Adubos
        for adubo in dados.get("adubos", []):
            cursor.execute('''
                INSERT OR REPLACE INTO insumos 
                (id, categoria, nome, teores, preco_kg, preco_t, unidade, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                adubo["id"],
                "Adubo",
                adubo["nome"],
                json.dumps(adubo["teores"], ensure_ascii=False),
                adubo.get("preco_kg", 0),
                None,
                adubo.get("unidade", "kg/ha"),
                datetime.now().isoformat()
            ))
            count += 1
        
        # Corretivos
        for corr in dados.get("corretivos", []):
            cursor.execute('''
                INSERT OR REPLACE INTO insumos 
                (id, categoria, nome, teores, preco_kg, preco_t, unidade, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                corr["id"],
                "Corretivo",
                corr["nome"],
                json.dumps(corr["teores"], ensure_ascii=False),
                None,
                corr.get("preco_t", 0),
                corr.get("unidade", "t/ha"),
                datetime.now().isoformat()
            ))
            count += 1
        
        # Renomear JSON para backup
        backup = json_path.with_suffix(".json_old")
        shutil.move(str(json_path), str(backup))
        logging.info(f"  ✓ {count} insumos migrados. JSON renomeado para .json_old")
        
    except Exception as e:
        logging.info(f"  ✗ Erro ao migrar insumos: {e}")
    
    conn.commit()
    conn.close()
    return count

def migrar_configuracoes():
    """Migra branding e custos dos JSON para SQLite (tabela key-value)."""
    conn = get_connection()
    cursor = conn.cursor()
    count = 0
    
    # Branding
    branding_path = CONFIG_DIR / "branding.json"
    if branding_path.exists():
        try:
            with open(branding_path, "r", encoding="utf-8") as f:
                branding = json.load(f)
            
            for key, value in branding.items():
                if key == "data_atualizacao":
                    continue
                cursor.execute('''
                    INSERT OR REPLACE INTO configuracoes (key, value, categoria, data_atualizacao)
                    VALUES (?, ?, ?, ?)
                ''', (key, json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value), "branding", datetime.now().isoformat()))
                count += 1
            
            backup = branding_path.with_suffix(".json_old")
            shutil.move(str(branding_path), str(backup))
            logging.info(f"  ✓ Branding migrado ({count} chaves). JSON renomeado.")
        except Exception as e:
            logging.info(f"  ✗ Erro ao migrar branding: {e}")
    
    # Custos operacionais
    custos_op_path = CONFIG_DIR / "custos_operacionais.json"
    if custos_op_path.exists():
        try:
            with open(custos_op_path, "r", encoding="utf-8") as f:
                custos = json.load(f)
            
            for key, value in custos.items():
                if key == "data_atualizacao":
                    continue
                cursor.execute('''
                    INSERT OR REPLACE INTO configuracoes (key, value, categoria, data_atualizacao)
                    VALUES (?, ?, ?, ?)
                ''', (f"custos_op_{key}", str(value), "custos_operacionais", datetime.now().isoformat()))
                count += 1
            
            backup = custos_op_path.with_suffix(".json_old")
            shutil.move(str(custos_op_path), str(backup))
            logging.info("  ✓ Custos operacionais migrados. JSON renomeado.")
        except Exception as e:
            logging.info(f"  ✗ Erro ao migrar custos operacionais: {e}")
    
    # Custos estrategicos
    custos_est_path = CONFIG_DIR / "custos_estrategicos.json"
    if custos_est_path.exists():
        try:
            with open(custos_est_path, "r", encoding="utf-8") as f:
                custos = json.load(f)
            
            cursor.execute('''
                INSERT OR REPLACE INTO configuracoes (key, value, categoria, data_atualizacao)
                VALUES (?, ?, ?, ?)
            ''', ("custos_estrategicos", json.dumps(custos, ensure_ascii=False), "custos_estrategicos", datetime.now().isoformat()))
            
            backup = custos_est_path.with_suffix(".json_old")
            shutil.move(str(custos_est_path), str(backup))
            logging.info("  ✓ Custos estrategicos migrados. JSON renomeado.")
        except Exception as e:
            logging.info(f"  ✗ Erro ao migrar custos estrategicos: {e}")
    
    conn.commit()
    conn.close()
    return count

def executar_migracao():
    """Executa migracao completa."""
    logging.info("=" * 60)
    logging.info("MIGRACAO JSON -> SQLITE")
    logging.info("=" * 60)
    logging.info(f"Banco de dados: {DB_PATH}")
    logging.info("")
    
    # Inicializar schema
    import db_schema
    db_schema.init_database()
    
    logging.info("\n[1/3] Migrando clientes...")
    n_clientes = migrar_clientes()
    
    logging.info("\n[2/3] Migrando insumos...")
    n_insumos = migrar_insumos()
    
    logging.info("\n[3/3] Migrando configuracoes...")
    n_config = migrar_configuracoes()
    
    logging.info("\n" + "=" * 60)
    logging.info("MIGRACAO CONCLUIDA")
    logging.info("=" * 60)
    logging.info(f"Clientes migrados: {n_clientes}")
    logging.info(f"Insumos migrados: {n_insumos}")
    logging.info(f"Configuracoes migradas: {n_config}")
    logging.info("\nArquivos .json renomeados para .json_old (backup).")
    logging.info("Para reverter, renomeie os arquivos de volta.")

if __name__ == "__main__":
    executar_migracao()

