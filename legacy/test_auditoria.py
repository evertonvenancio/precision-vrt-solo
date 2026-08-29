"""
Precision VRT Solo — Teste do Sistema de Auditoria

Script para validar o funcionamento da auditoria real.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import sqlite3
from services.auditoria_service import AuditoriaPersistenteService
from core.seguranca.auditoria import TipoAcao, ModuloSistema

def testar_auditoria():
    """
    Testa o sistema de auditoria com dados reais.
    """
    print("🔍 Testando Sistema de Auditoria...")
    print("=" * 50)
    
    try:
        # Conectar ao banco usando Session
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine('sqlite:///precision_vrt.db')
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Instanciar serviço de auditoria
        auditoria_service = AuditoriaPersistenteService(db)
        
        print("✅ 1. Serviço de auditoria instanciado com sucesso")
        
        # Testar registro de operação
        resultado1 = auditoria_service.registrar_operacao(
            tipo_acao=TipoAcao.CRIAR,
            modulo=ModuloSistema.USUARIOS,
            usuario_id=1,
            usuario_nome="test_user",
            acao="teste_operacao",
            recurso_id="123",
            sucesso=True
        )
        
        print(f"✅ 2. Evento de auditoria registrado: ID {resultado1}")
        
        # Testar consulta de eventos
        eventos = auditoria_service.obter_registros(usuario_id=1)
        print(f"✅ 3. Consulta de eventos: {len(eventos)} eventos encontrados")
        
        if eventos:
            evento = eventos[0]
            print(f"   - Usuário: {evento['usuario_nome']}")
            print(f"   - Ação: {evento['acao']}")
            print(f"   - Módulo: {evento['modulo']}")
            print(f"   - Sucesso: {evento['sucesso']}")
        
        # Testar estatísticas
        stats = auditoria_service.obter_estatisticas(periodo_dias=1)
        print(f"✅ 4. Estatísticas: {stats['total_registros']} eventos no período")
        
        # Testar login
        resultado2 = auditoria_service.registrar_login(
            usuario_id=1,
            usuario_nome="test_user",
            ip_origem="127.0.0.1",
            sucesso=True
        )
        
        print(f"✅ 5. Evento de login registrado: ID {resultado2}")
        
        # Testar operação de cliente
        resultado3 = auditoria_service.registrar_operacao_cliente(
            tipo_acao=TipoAcao.CRIAR,
            usuario_id=1,
            usuario_nome="test_user",
            cliente_id="123",
            detalhes={'nome': 'Test Client', 'ativo': True}
        )
        
        print(f"✅ 6. Evento de cliente registrado: ID {resultado3}")
        
        # Verificar eventos no banco
        from models.auditoria import AuditoriaEvento
        total = db.query(AuditoriaEvento).count()
        print(f"✅ 7. Total de eventos no banco: {total}")
        
        db.close()
        
        print("\n🎯 Todos os testes de auditoria passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante testes: {e}")
        return False

if __name__ == "__main__":
    sucesso = testar_auditoria()
    
    if sucesso:
        print("\n🔧 Próximos passos:")
        print("   1. Reiniciar o aplicativo")
        print("   2. Acessar /web/audit para visualizar eventos")
        print("   3. Realizar login/logout para gerar eventos reais")
        print("   4. Testar criação/edição/exclusão de clientes")
    else:
        print("\n❌ Alguns testes falharam. Verificar erros acima.")