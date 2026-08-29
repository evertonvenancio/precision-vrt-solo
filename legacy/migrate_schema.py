import sqlite3
import os

DB_PATH = os.path.join(r'C:\precision_vrt_solo', 'precision_vrt.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar se colunas já existem
    cursor.execute("PRAGMA table_info(responsaveis_tecnicos)")
    columns = [row[1] for row in cursor.fetchall()]
    
    changes = []
    
    if 'numero_registro' not in columns:
        cursor.execute("ALTER TABLE responsaveis_tecnicos ADD COLUMN numero_registro TEXT")
        changes.append("numero_registro")
    
    if 'conselho_classe' not in columns:
        cursor.execute("ALTER TABLE responsaveis_tecnicos ADD COLUMN conselho_classe TEXT")
        changes.append("conselho_classe")
    
    conn.commit()
    conn.close()
    
    if changes:
        logging.info("MIGRACAO OK: " + ", ".join(changes))
    else:
        logging.info("MIGRACAO: Colunas ja existem")

if __name__ == '__main__':
    migrate()

