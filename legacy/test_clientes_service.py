import sys
sys.path.append('.')

print("🧪 TESTE: ClientesService Real")
print("=" * 50)

try:
    from db.database import SessionLocal
    from services.clientes_service import ClientesService
    
    # Criar sessão do banco
    db = SessionLocal()
    
    # Criar usuário autenticado
    user_data = {
        'user_id': '818c527a-1672-4189-861e-aef15fea1325',
        'username': 'admin',
        'role': 'admin',
        'permissions': ['clientes:read']
    }
    
    # Criar serviço
    service = ClientesService(db, user_data)
    
    print("✅ ClientesService criado com sucesso")
    
    # Testar listagem de clientes
    print("📋 Testando listagem de clientes...")
    clientes = service.listar()
    print(f"📊 Clientes encontrados: {len(clientes)}")
    
    for cliente in clientes[:3]:  # Mostrar apenas 3 primeiros
        print(f"  - {cliente['nome']} ({cliente['email']})")
    
    # Testar obtenção de cliente específico
    if clientes:
        cliente_id = clientes[0]['id']
        print(f"🔍 Testando obtenção do cliente ID: {cliente_id}")
        cliente = service.obter(cliente_id)
        if cliente:
            print(f"✅ Cliente encontrado: {cliente['nome']}")
        else:
            print("❌ Cliente não encontrado")
    
    # Testar criação de cliente
    print("🆕 Testando criação de novo cliente...")
    resultado = service.criar(
        nome="Cliente Teste",
        cpf_cnpj="123.456.789-00",
        telefone="11-99999-0000",
        email="teste@example.com",
        cidade="São Paulo",
        estado="SP",
        area_total_hectares=10.5
    )
    
    if resultado['success']:
        print("✅ Cliente criado com sucesso")
        print(f"📝 ID do cliente: {resultado['cliente']['id']}")
        
        # Testar atualização do cliente
        print("🔄 Testando atualização do cliente...")
        resultado_atualizacao = service.atualizar(
            cliente_id=resultado['cliente']['id'],
            nome="Cliente Teste Atualizado",
            cpf_cnpj="123.456.789-00",
            telefone="11-99999-0000",
            email="teste.updated@example.com",
            cidade="São Paulo",
            estado="SP",
            area_total_hectares=15.0
        )
        
        if resultado_atualizacao['success']:
            print("✅ Cliente atualizado com sucesso")
        else:
            print(f"❌ Erro na atualização: {resultado_atualizacao['detail']}")
        
        # Testar exclusão do cliente
        print("🗑️ Testando exclusão do cliente...")
        resultado_exclusao = service.excluir(
            cliente_id=resultado['cliente']['id'],
            senha="admin123",
            justificativa="Cliente de teste"
        )
        
        if resultado_exclusao['success']:
            print("✅ Cliente excluído com sucesso")
        else:
            print(f"❌ Erro na exclusão: {resultado_exclusao['detail']}")
        
    else:
        print(f"❌ Erro na criação: {resultado['detail']}")
    
    # Testar permissões
    permissoes = service.buscar_permissoes()
    print(f"🔐 Permissões: {permissoes.get('view_menu_clientes', False)}")
    
    db.close()
    
    print("✅ TESTE DO CLIENTESERVICE: COMPLETO")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    import traceback
    traceback.print_exc()