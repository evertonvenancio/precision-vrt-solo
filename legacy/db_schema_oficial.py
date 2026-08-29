import sqlite3
import hashlib

DB_NAME = "precision_vrt.db"

def get_connection():
    """Retorna a conexao com o banco."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Cria as tabelas se nao existirem."""
    conn = get_connection()
    cursor = conn.cursor()

    # Cargos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cargos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            permissoes_padrao TEXT DEFAULT '{}'
        )
    """)

    # Funcionarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            cpf TEXT,
            telefone TEXT,
            cargo_id INTEGER,
            registro_profissional TEXT,
            foto_path TEXT,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY(cargo_id) REFERENCES cargos(id)
        )
    """)

    # Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER UNIQUE,
            login TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            permissoes TEXT DEFAULT '{}',
            ultimo_acesso TIMESTAMP,
            FOREIGN KEY(funcionario_id) REFERENCES funcionarios(id)
        )
    """)

    # Config Visual
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config_visual (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            marca_nome TEXT DEFAULT 'Tech & Agri',
            marca_slogan TEXT DEFAULT 'Transformando dados em resultados',
            logo_path TEXT,
            software_nome TEXT DEFAULT 'Precision VRT Solo',
            desenvolvedor TEXT DEFAULT 'VNC Dec',
            cor_primaria TEXT DEFAULT '#00c853'
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO config_visual (id) VALUES (1)")

    # Dados Iniciais
    cargos = [
        ('Administrador', '{"total": true}'),
        ('Agrônomo/RT', '{"prescricao": true}'),
        ('Financeiro', '{"financeiro": true}'),
        ('Vendedor', '{"clientes": true}')
    ]
    cursor.executemany("INSERT OR IGNORE INTO cargos (nome, permissoes_padrao) VALUES (?, ?)", cargos)

    # Admin
    if not cursor.execute("SELECT id FROM usuarios WHERE login='admin'").fetchone():
        senha = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT INTO funcionarios (nome_completo, cargo_id) VALUES (?, ?)", ('Administrador Master', 1))
        func_id = cursor.lastrowid
        cursor.execute("INSERT INTO usuarios (funcionario_id, login, senha_hash, permissoes) VALUES (?, ?, ?, ?)",
                       (func_id, 'admin', senha, '{"total": true}'))

    conn.commit()
    conn.close()
    logging.info("Banco de dados verificado.")

