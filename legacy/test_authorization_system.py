#!/usr/bin/env python3
"""
Teste completo do sistema de autorização real
Valida o fluxo: JWT → Permissão → Acesso
"""

import sys
import os
sys.path.append('.')

from app.services.auth_service_real import AuthService
import jwt

def test_authorization_system():
    """Teste completo do sistema de autorização"""
    
    print("🧪 TESTE COMPLETO - SISTEMA DE AUTORIZAÇÃO REAL")
    print("=" * 60)
    
    # Inicializar AuthService
    service = AuthService()
    
    # Teste 1: Gerar JWT real
    print("\n🔍 TESTE 1 - Gerar JWT real")
    user_data = service.authenticate_user('admin', 'admin123')
    if not user_data:
        print("❌ ERRO: Login falhou!")
        return False
    
    access_token = service.create_access_token(user_data)
    refresh_token = service.create_refresh_token(user_data)
    print(f"✅ JWT gerado: {access_token[:50]}...")
    print(f"✅ Refresh token gerado: {refresh_token[:50]}...")
    
    # Teste 2: Verificar JWT válido
    print("\n🔍 TESTE 2 - Verificar JWT válido")
    payload = service.verify_token(access_token)
    if payload:
        print(f"✅ JWT válido: {payload.get('sub')}")
        print(f"✅ Permissões: {payload.get('permissions', [])}")
    else:
        print("❌ ERRO: JWT inválido!")
        return False
    
    # Teste 3: Verificar JWT expirado
    print("\n🔍 TESTE 3 - Verificar JWT expirado")
    # Criar JWT expirado
    expired_payload = {
        'sub': 'admin',
        'user_id': '818c527a-1672-4189-861e-aef15fea1325',
        'role': 'admin',
        'permissions': ['dashboard:read'],
        'exp': 1234567890,  # Data no passado
        'iat': 1234560000
    }
    expired_token = jwt.encode(expired_payload, service.secret_key, algorithm='HS256')
    
    expired_result = service.verify_token(expired_token)
    if expired_result is None:
        print("✅ JWT expirado corretamente rejeitado")
    else:
        print("❌ ERRO: JWT expirado foi aceito!")
        return False
    
    # Teste 4: Verificar JWT inválido
    print("\n🔍 TESTE 4 - Verificar JWT inválido")
    invalid_token = "token.falso.jwt.incompleto"
    invalid_result = service.verify_token(invalid_token)
    if invalid_result is None:
        print("✅ JWT inválido corretamente rejeitado")
    else:
        print("❌ ERRO: JWT inválido foi aceito!")
        return False
    
    # Teste 5: Testar permissões específicas
    print("\n🔍 TESTE 5 - Testar permissões específicas")
    user_permissions = payload.get('permissions', [])
    
    # Permissão existente
    has_read = 'dashboard:read' in user_permissions
    print(f"✅ Tem dashboard:read: {has_read}")
    
    # Permissão inexistente
    has_export = 'relatorios:export' in user_permissions
    print(f"✅ Tem relatorios:export (deveria ser False): {not has_export}")
    
    # Teste 6: Testar fluxo completo simulado
    print("\n🔍 TESTE 6 - Simular fluxo de endpoint protegido")
    
    # Simular chamada a endpoint protegido
    def simulate_protected_endpoint(token, required_permission):
        """Simula endpoint protegido por permissão"""
        try:
            # Verificar token
            payload = service.verify_token(token)
            if not payload:
                return {"status": 401, "message": "Token inválido"}
            
            # Verificar permissão
            user_permissions = payload.get('permissions', [])
            if required_permission not in user_permissions:
                return {"status": 403, "message": f"Permissão '{required_permission}' necessária"}
            
            return {"status": 200, "message": "Acesso permitido"}
            
        except Exception as e:
            return {"status": 500, "message": f"Erro interno: {str(e)}"}
    
    # Testar acesso permitido
    result = simulate_protected_endpoint(access_token, 'dashboard:read')
    if result['status'] == 200:
        print("✅ Acesso permitido para dashboard:read")
    else:
        print(f"❌ ERRO: Acesso negado inesperado: {result}")
        return False
    
    # Testar acesso negado
    result = simulate_protected_endpoint(access_token, 'relatorios:export')
    if result['status'] == 403:
        print("✅ Acesso negado para relatorios:export (correto)")
    else:
        print(f"❌ ERRO: Acesso permitido inesperado: {result}")
        return False
    
    # Teste 7: Testar token revogado (logout)
    print("\n🔍 TESTE 7 - Testar token revogado")
    service.logout_user(access_token, refresh_token)
    
    # Verificar se token foi revogado
    revoked_result = service.verify_token(access_token)
    if revoked_result is None:
        print("✅ Token revogado corretamente")
    else:
        print("❌ ERRO: Token revogado ainda é válido!")
        return False
    
    print("\n🎉 TODOS OS TESTES DE AUTORIZAÇÃO PASSARAM!")
    return True

if __name__ == "__main__":
    success = test_authorization_system()
    sys.exit(0 if success else 1)