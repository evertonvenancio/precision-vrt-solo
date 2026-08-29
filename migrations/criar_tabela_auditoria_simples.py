"""
Precision VRT Solo — Migração da Tabela de Auditoria

Script para criar a tabela auditoria_eventos no banco de dados.
Executar apenas uma vez.
"""

import sqlite3
import os

def criar_tabela_auditoria():
    """
    Cria a tabela de auditoria no banco de dados.
    """
    print("🔧 Criando tabela de auditoria...")
    
    try:
        # Obter caminho do banco
        db_path = os.path.join(os.path.dirname(__file__), "..", "precision_vrt.db")
        
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL para criar a tabela
        sql_create_table = """
        CREATE TABLE IF NOT EXISTS auditoria_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_acao VARCHAR(50) NOT NULL,
            modulo VARCHAR(50) NOT NULL,
            usuario_id INTEGER NOT NULL,
            usuario_nome VARCHAR(100) NOT NULL,
            acao VARCHAR(200) NOT NULL,
            recurso_id VARCHAR(100),
            recurso_tipo VARCHAR(50),
            ip_origem VARCHAR(45),
            user_agent TEXT,
            sucesso BOOLEAN NOT NULL DEFAULT 1,
            mensagem TEXT,
            detalhes TEXT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Executar a criação
        cursor.execute(sql_create_table)
        conn.commit()
        
        # Criar índices separadamente
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_usuario_id ON auditoria_eventos(usuario_id);",
            "CREATE INDEX IF NOT EXISTS idx_tipo_acao ON auditoria_eventos(tipo_acao);",
            "CREATE INDEX IF NOT EXISTS idx_modulo ON auditoria_eventos(modulo);",
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON auditoria_eventos(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_recurso_id ON auditoria_eventos(recurso_id);"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)
        
        conn.commit()
        
        print("✅ Tabela auditoria_eventos criada com sucesso!")
        print("\n📊 Estrutura da tabela:")
        
        # Mostrar estrutura
        cursor.execute("PRAGMA table_info(auditoria_eventos);")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela de auditoria: {e}")
        return False

if __name__ == "__main__":
    sucesso = criar_tabela_auditoria()
    
    if sucesso:
        print("\n🎯 Próximos passos:")
        print("   1. Reiniciar o aplicativo para carregar a nova tabela")
        print("   2. Testar operações de login/logout para registrar eventos")
        print("   3. Acessar /web/audit para visualizar eventos")
    else:
        print("\n❌ A migração falhou. Verifique o erro acima.")