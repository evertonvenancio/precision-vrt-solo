import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'precision_vrt.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def atualizar_schema():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se as colunas já existem
    cursor.execute("PRAGMA table_info(responsaveis_tecnicos)")
    colunas_existentes = [row['name'] for row in cursor.fetchall()]
    
    alteracoes = []
    
    if 'numero_registro' not in colunas_existentes:
        cursor.execute("ALTER TABLE responsaveis_tecnicos ADD COLUMN numero_registro TEXT")
        alteracoes.append("numero_registro")
        logging.info("[DB] Coluna 'numero_registro' adicionada.")
    else:
        logging.info("[DB] Coluna 'numero_registro' já existe.")
    
    if 'conselho_classe' not in colunas_existentes:
        cursor.execute("ALTER TABLE responsaveis_tecnicos ADD COLUMN conselho_classe TEXT")
        alteracoes.append("conselho_classe")
        logging.info("[DB] Coluna 'conselho_classe' adicionada.")
    else:
        logging.info("[DB] Coluna 'conselho_classe' já existe.")
    
    conn.commit()
    conn.close()
    
    if alteracoes:
        logging.info(f"[DB] Schema atualizado com sucesso. Colunas adicionadas: {', '.join(alteracoes)}")
    else:
        logging.info("[DB] Nenhuma alteração necessária. Schema já está atualizado.")

if __name__ == "__main__":
    atualizar_schema()

