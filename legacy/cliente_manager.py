import sqlite3
import re
from datetime import datetime

DB_NAME = "precision_vrt.db"

class ClienteManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self._criar_tabela()

    def _criar_tabela(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                fazenda TEXT,
                cidade TEXT,
                cep TEXT,
                data_coleta TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def validar_cep(self, cep):
        """Valida e normaliza CEP no formato 00000-000."""
        if not cep:
            return ""
        cep_str = str(cep)
        cep_clean = re.sub(r"\D", "", cep_str)
        if len(cep_clean) == 8:
            return f"{cep_clean[:5]}-{cep_clean[5:]}"
        return cep_str

    def validar_data(self, data_str):
        """Valida data no formato DD/MM/YYYY."""
        if not data_str:
            return ""
        try:
            dt = datetime.strptime(str(data_str), "%d/%m/%Y")
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            return data_str

    def adicionar(self, nome, fazenda, cidade, cep, data_coleta):
        cursor = self.conn.cursor()
        cep_validado = self.validar_cep(cep)
        data_validada = self.validar_data(data_coleta)
        
        cursor.execute("""
            INSERT INTO clientes (nome, fazenda, cidade, cep, data_coleta)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, fazenda, cidade, cep_validado, data_validada))
        self.conn.commit()
        return cursor.lastrowid

    def listar(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY nome")
        return cursor.fetchall()

    def fechar(self):
        self.conn.close()
