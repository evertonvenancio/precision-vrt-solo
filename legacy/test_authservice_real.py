#!/usr/bin/env python3
"""
Teste completo do AuthService REAL - Fluxo End-to-End

Teste a integração real:
AuthService → Banco → JWT → Endpoint
"""

import sys
import os
sys.path.append('.')

from app.services.auth_service_real import AuthService
import jwt
from datetime import datetime, timedelta

def test_authservice_real():
    """Teste completo do AuthService real"""
    
    print("🧪 TESTE COMPLETO - AUTHSERVICE REAL")
    print("=" * 50)
    
    # Inicializar AuthService
    service = AuthService()
    print("✅ AuthService inicializado")
    
    # Teste 1: Login válido
    print("\n🔍 TESTE 1 - Login válido")
    user_data = service.authenticate_user('admin', 'admin123')
    if user_data:
        print(f"✅ Login válido: {user_data['username']} (ID: {user_data['id']})")
    else:
        print("❌ ERRO: Login falhou!")
        return False
    
    # Teste 2: Senha inválida
    print("\n🔍 TESTE 2 - Senha inválida")
    result = service.authenticate_user('admin', 'senha_errada')
    if result is None:
        print("✅ Senha inválida corretamente rejeitada")
    else:
        print("❌ ERRO: Senha inválida foi aceita!")
        return False
    
    # Teste 3: Usuário inexistente
    print("\n🔍 TESTE 3 - Usuário inexistente")
    result = service.authenticate_user('usuario_inexistente', 'qualquer_senha')
    if result is None:
        print("✅ Usuário inexistente corretamente rejeitado")
    else:
        print("❌ ERRO: Usuário inexistente foi autenticado!")
        return False
    
    # Teste 4: Usuário inativo
    print("\n🔍 TESTE 4 - Usuário inativo")
    # Simular usuário inativo
    class MockInactiveSession:
        def execute(self, query, params=None):
            class MockResult:
                def fetchone(self):
                    return ('id_fake', 'admin_inativo', 'hash_fake', False, None)
            return MockResult()
    
    service_inactive = AuthService(MockInactiveSession())
    result = service_inactive.authenticate_user('admin_inativo', 'qualquer_senha')
    if result is None:
        print("✅ Usuário inativo corretamente rejeitado")
    else:
        print("❌ ERRO: Usuário inativo foi autenticado!")
        return False
    
    # Teste 5: JWT inválido
    print("\n🔍 TESTE 5 - JWT inválido")
    invalid_token = "token_falso.jwt.incompleto"
    result = service.verify_token(invalid_token)
    if result is None:
        print("✅ JWT inválido corretamente rejeitado")
    else:
        print("❌ ERRO: JWT inválido foi aceito!")
        return False
    
    # Teste 6: JWT expirado
    print("\n🔍 TESTE 6 - JWT expirado")
    # Criar JWT expirado
    expired_payload = {
        'sub': 'admin',
        'user_id': '818c527a-1672-4189-861e-aef15fea1325',
        'role': 'admin',
        'permissions': ['dashboard:read'],
        'exp': datetime.utcnow() - timedelta(minutes=1),  # Expirado
        'iat': datetime.utcnow()
    }
    expired_token = jwt.encode(expired_payload, service.secret_key, algorithm='HS256')
    result = service.verify_token(expired_token)
    if result is None:
        print("✅ JWT expirado corretamente rejeitado")
    else:
        print("❌ ERRO: JWT expirado foi aceito!")
        return False
    
    # Teste 7: Refresh
    print("\n🔍 TESTE 7 - Refresh token")
    # Gerar tokens
    access_token = service.create_access_token(user_data)
    refresh_token = service.create_refresh_token(user_data)
    
    # Testar refresh
    new_access_token = service.refresh_access_token(refresh_token)
    if new_access_token:
        print("✅ Refresh token funciona corretamente")
    else:
        print("❌ ERRO: Refresh token falhou!")
        return False
    
    # Teste 8: Logout
    print("\n🔍 TESTE 8 - Logout com revogação")
    # Verificar token antes
    before_verify = service.verify_token(access_token)
    
    # Realizar logout
    service.logout_user(access_token, refresh_token)
    
    # Verificar token após
    after_verify = service.verify_token(access_token)
    
    if before_verify and not after_verify:
        print("✅ Logout com revogação funciona corretamente")
    else:
        print("❌ ERRO: Logout não revogou o token!")
        return False
    
    # Teste 9: Restart
    print("\n🔍 TESTE 9 - Restart com novo token")
    # Gerar novo token (não revogado)
    new_access_token = service.create_access_token(user_data)
    
    # Simular novo serviço (restart)
    service2 = AuthService()
    result = service2.verify_token(new_access_token)
    if result:
        print("✅ Token não revogado persistiu corretamente após restart")
    else:
        print("❌ ERRO: Token não revogado não persistiu!")
        return False
    
    # Teste 10: Banco como autoridade
    print("\n🔍 TESTE 10 - Banco como autoridade")
    # Testar JWT gerado com dados reais
    token = service.create_access_token(user_data)
    payload = jwt.decode(token, service.secret_key, algorithms=['HS256'])
    
    # Verificar se os dados são reais
    expected_user_id = '818c527a-1672-4189-861e-aef15fea1325'
    expected_username = 'admin'
    expected_role = 'admin'
    
    if (payload.get('user_id') == expected_user_id and 
        payload.get('sub') == expected_username and
        payload.get('role') == expected_role):
        print("✅ JWT contém identidade real do banco")
    else:
        print("❌ ERRO: JWT não contém dados reais do banco!")
        return False
    
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    return True

if __name__ == "__main__":
    success = test_authservice_real()
    sys.exit(0 if success else 1)