import sys
sys.path.append('.')

print("🧪 TESTE: DashboardService com dados reais")
print("=" * 50)

try:
    from db.database import SessionLocal
    from services.dashboard_service import DashboardService
    from auth.authenticated_user import AuthenticatedUser
    
    # Criar sessão do banco
    db = SessionLocal()
    
    # Criar usuário autenticado (dados reais do banco)
    user_data = {
        'user_id': '818c527a-1672-4189-861e-aef15fea1325',
        'username': 'admin',
        'role': 'admin',
        'permissions': ['dashboard:read']
    }
    
    # Criar serviço
    service = DashboardService(db, user_data)
    
    # Testar dados do dashboard
    dados = service.get_dados()
    
    print("✅ DashboardService criado com sucesso")
    print(f"📊 Total de clientes: {dados['total_clientes']}")
    print(f"📊 Total de fazendas: {dados['total_fazendas']}")
    print(f"📊 Total de orçamentos: {dados['orcamentos']}")
    print(f"📊 Total de prescrições: {dados['prescricoes_geradas']}")
    print(f"📊 Área total: {dados['area_total_cadastrada']} ha")
    print(f"👤 Nome usuário: {dados['nome_usuario']}")
    
    # Verificar se os dados são reais (não zerados)
    total_reais = sum([
        dados['total_clientes'],
        dados['total_fazendas'], 
        dados['orcamentos'],
        dados['prescricoes_geradas']
    ])
    
    if total_reais > 0:
        print("✅ DADOS REAIS ENCONTRADOS - Dashboard REAL")
    else:
        print("⚠️  Todos os dados zerados - possivelmente sem dados no banco")
    
    # Testar permissões
    permissoes = service.buscar_permissoes()
    print(f"🔐 Permissões: {permissoes}")
    
    db.close()
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    import traceback
    traceback.print_exc()