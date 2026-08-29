"""
Precision VRT Solo — Migração da Tabela de Auditoria

Script para criar a tabela auditoria_eventos no banco de dados.
Executar apenas uma vez.
"""

from sqlalchemy import create_engine, text
from db.database import DATABASE_URL

# Caminho absoluto para o arquivo de banco
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar o caminho correto
from db.database import DATABASE_URL

def criar_tabela_auditoria():
    """
    Cria a tabela de auditoria no banco de dados.
    """
    print("🔧 Criando tabela de auditoria...")
    
    try:
        # Criar conexão
        engine = create_engine(DATABASE_URL)
        
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
            sucesso BOOLEAN NOT NULL DEFAULT TRUE,
            mensagem TEXT,
            detalhes TEXT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            
            -- Índices para performance
            INDEX idx_usuario_id (usuario_id),
            INDEX idx_tipo_acao (tipo_acao),
            INDEX idx_modulo (modulo),
            INDEX idx_timestamp (timestamp),
            INDEX idx_recurso_id (recurso_id)
        );
        """
        
        # Executar a criação
        with engine.connect() as conn:
            conn.execute(text(sql_create_table))
            conn.commit()
            
        print("✅ Tabela auditoria_eventos criada com sucesso!")
        print("\n📊 Estrutura da tabela:")
        
        # Mostrar estrutura
        sql_describe = "PRAGMA table_info(auditoria_eventos);"
        with engine.connect() as conn:
            result = conn.execute(text(sql_describe))
            columns = result.fetchall()
            
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
        
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