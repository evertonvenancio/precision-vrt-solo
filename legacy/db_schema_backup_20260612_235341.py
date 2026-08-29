# db_schema.py
# Schema completo do banco de dados - VERSAO ATUALIZADA

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'precision_vrt.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # TABELAS ORIGINAIS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf_cnpj TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            cidade TEXT,
            estado TEXT,
            cep TEXT,
            area_total_hectares REAL DEFAULT 0,
            data_nascimento TEXT,
            responsavel_tecnico_id INTEGER,
            observacoes TEXT,
            pasta_cliente TEXT,
            ativo INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fazendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            hectares_total REAL,
            localizacao TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS talhoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fazenda_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            hectares REAL,
            coordenadas_geojson TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fazenda_id) REFERENCES fazendas(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT,
            comissao_percentual REAL DEFAULT 0.0,
            salario_base REAL DEFAULT 0.0,
            data_admissao TEXT,
            telefone TEXT,
            email TEXT,
            ativo INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recomendacoes_vrt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            fazenda_id INTEGER,
            talhao_id INTEGER,
            cultura TEXT,
            safra TEXT,
            data_amostragem TEXT,
            data_processamento TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'processando',
            arquivo_entrada TEXT,
            arquivo_vrt_shp TEXT,
            arquivo_vrt_tiff TEXT,
            estatisticas_json TEXT,
            observacoes TEXT,
            responsavel_tecnico_id INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (fazenda_id) REFERENCES fazendas(id),
            FOREIGN KEY (talhao_id) REFERENCES talhoes(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recomendacoes_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recomendacao_id INTEGER NOT NULL,
            zona_id INTEGER,
            classe_zona TEXT,
            area_hectares REAL,
            dosagem_kg_ha REAL,
            insumo_sugerido TEXT,
            custo_estimado REAL,
            produtividade_estimada REAL,
            geometria_geojson TEXT,
            FOREIGN KEY (recomendacao_id) REFERENCES recomendacoes_vrt(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financeiro_orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            recomendacao_id INTEGER,
            talhao_id INTEGER,
            descricao TEXT,
            custo_insumos REAL DEFAULT 0,
            custo_mao_obra REAL DEFAULT 0,
            custo_equipamentos REAL DEFAULT 0,
            custo_transporte REAL DEFAULT 0,
            custo_administrativo REAL DEFAULT 0,
            desconto_percentual REAL DEFAULT 0,
            valor_total REAL DEFAULT 0,
            status TEXT DEFAULT 'rascunho',
            data_emissao TEXT DEFAULT CURRENT_TIMESTAMP,
            data_validade TEXT,
            data_aprovacao TEXT,
            comissao_equipe_id INTEGER,
            responsavel_tecnico_id INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (recomendacao_id) REFERENCES recomendacoes_vrt(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financeiro_faturamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orcamento_id INTEGER NOT NULL,
            cliente_id INTEGER NOT NULL,
            numero_nota TEXT,
            serie_nota TEXT,
            valor_bruto REAL DEFAULT 0,
            valor_liquido REAL DEFAULT 0,
            impostos_retidos REAL DEFAULT 0,
            status_pagamento TEXT DEFAULT 'pendente',
            metodo_pagamento TEXT,
            data_faturamento TEXT DEFAULT CURRENT_TIMESTAMP,
            data_pagamento TEXT,
            observacoes TEXT,
            comissao_paga INTEGER DEFAULT 0,
            FOREIGN KEY (orcamento_id) REFERENCES financeiro_orcamentos(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config_export (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            empresa_nome TEXT DEFAULT 'Tech & Agri VRT',
            empresa_logo_path TEXT,
            empresa_cnpj TEXT,
            empresa_endereco TEXT,
            empresa_telefone TEXT,
            empresa_email TEXT,
            cor_primaria TEXT DEFAULT '#2E7D32',
            cor_secundaria TEXT DEFAULT '#1B5E20',
            fonte_titulo TEXT DEFAULT 'Helvetica-Bold',
            fonte_corpo TEXT DEFAULT 'Helvetica',
            disclaimer TEXT DEFAULT 'Mapa gerado automaticamente. Sujeito a validacao tecnica in loco.'
        )
    """)
    
    # NOVAS TABELAS PARA O app.py
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE NOT NULL,
            valor TEXT,
            tipo TEXT DEFAULT 'string',
            descricao TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsaveis_tecnicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            crea TEXT UNIQUE,
            numero_registro TEXT,
            conselho_classe TEXT,
            cpf TEXT,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            cidade TEXT,
            estado TEXT,
            logo_path TEXT,
            cor_primaria TEXT DEFAULT '#2E7D32',
            cor_secundaria TEXT DEFAULT '#81C784',
            cor_texto TEXT DEFAULT '#FFFFFF',
            ativo INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS culturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nome_cientifico TEXT,
            unidade_produtividade TEXT DEFAULT 'sc/ha',
            meta_produtividade_padrao REAL,
            ativo INTEGER DEFAULT 1
        )
    """)
    
    # DADOS INICIAIS
    cursor.execute("INSERT OR IGNORE INTO config_export (id) VALUES (1)")
    
    cursor.execute("""
        INSERT OR IGNORE INTO config_sistema (chave, valor, tipo, descricao) VALUES
        ('senha_painel_gestor', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'string', 'Senha padrao: admin123'),
        ('senha_financeiro', '8c5c9e9fcec32281c5cb5eb2772a9e3f0e2e1e4bfe3e4c7e8f9a0b1c2d3e4f5', 'string', 'Senha padrao: finance123')
    """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO culturas (nome, meta_produtividade_padrao) VALUES
        ('Milho', 80), ('Soja', 55), ('Trigo', 45), ('Arroz', 70),
        ('Feijao', 25), ('Algodao', 40), ('Cafe', 30), ('Cana-de-Acucar', 80),
        ('Sorgo', 60), ('Melancia', 40), ('Abobora', 25), ('Frutiferas', 30), ('Citros', 35)
    """)
    
    conn.commit()
    conn.close()
    logging.info("[DB] Banco de dados inicializado com sucesso.")


def check_integrity():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        tabelas_esperadas = [
            'clientes', 'fazendas', 'talhoes', 'equipe',
            'recomendacoes_vrt', 'recomendacoes_itens',
            'financeiro_orcamentos', 'financeiro_faturamento',
            'config_export', 'config_sistema', 'responsaveis_tecnicos', 'culturas'
        ]
        
        erros = []
        
        for tabela in tabelas_esperadas:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
            if not cursor.fetchone():
                erros.append("Tabela ausente: " + tabela)
        
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        for viol in fk_violations:
            erros.append("Violacao FK: tabela=" + str(viol[0]) + ", rowid=" + str(viol[1]))
        
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        if integrity != 'ok':
            erros.append("Integridade comprometida: " + integrity)
        
        conn.close()
        
        if erros:
            return False, "Integridade comprometida: " + str(len(erros)) + " problema(s) encontrado(s)", erros
        return True, "Integridade verificada: OK", []
        
    except Exception as e:
        return False, "Erro ao verificar integridade: " + str(e), [str(e)]


if __name__ == "__main__":
    init_db()
    ok, msg, erros = check_integrity()
    logging.info("[INTEGRITY] " + msg)
    if erros:
        for e in erros:
            logging.info("  -> " + str(e))

