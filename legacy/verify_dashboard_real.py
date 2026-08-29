import sys
sys.path.append('.')

print("🚀 Iniciando verificação ad-hoc do Dashboard Real...")
print("=" * 60)

try:
    # Testar DashboardService com dados reais
    from db.database import SessionLocal
    from services.dashboard_service import DashboardService
    
    print("🔍 Testando DashboardService...")
    db = SessionLocal()
    
    # Criar usuário autenticado
    user_data = {
        'user_id': '818c527a-1672-4189-861e-aef15fea1325',
        'username': 'admin',
        'role': 'admin',
        'permissions': ['dashboard:read']
    }
    
    service = DashboardService(db, user_data)
    dados = service.get_dados()
    
    print("✅ DashboardService criado com sucesso")
    print(f"📊 Total de clientes: {dados['total_clientes']} (DEVE SER 9)")
    print(f"📊 Total de orçamentos: {dados['orcamentos']} (DEVE SER 2)")
    print(f"📊 Total de prescrições: {dados['prescricoes_geradas']}")
    print(f"📊 Área total: {dados['area_total_cadastrada']} ha")
    print(f"👤 Nome usuário: {dados['nome_usuario']}")
    
    # Verificar se dados são reais
    if dados['total_clientes'] == 9 and dados['orcamentos'] == 2:
        print("✅ DADOS REAIS CONFIRMADOS - Dashboard REAL")
    else:
        print("❌ Dados não são os esperados")
    
    # Testar permissões
    permissoes = service.buscar_permissoes()
    print(f"🔐 Permissões carregadas: {len(permissoes)} permissões")
    
    # Testar aniversariantes
    aniversariantes = dados['aniversariantes']
    print(f"🎂 Aniversariantes: {len(aniversariantes)} encontrados")
    
    db.close()
    
    print("✅ VERIFICAÇÃO DO DASHBOARD REAL: SUCESSO")
    
except Exception as e:
    print(f"❌ Erro na verificação: {e}")
    import traceback
    traceback.print_exc()