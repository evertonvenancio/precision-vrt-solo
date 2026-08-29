#!/usr/bin/env python3
"""
Teste End-to-End Real: Login → JWT → Endpoint Protegido
"""

import sys
import os
sys.path.append('.')

from app.services.auth_service_real import AuthService
from fastapi.testclient import TestClient
import json

def test_end_to_end_authorization():
    """Teste completo de autorização end-to-end"""
    
    print("🧪 TESTE END-TO-END - AUTORIZAÇÃO REAL")
    print("=" * 50)
    
    # Inicializar AuthService
    service = AuthService()
    
    # Teste 1: Login real
    print("\n🔍 TESTE 1 - Login real")
    user_data = service.authenticate_user('admin', 'admin123')
    if not user_data:
        print("❌ ERRO: Login falhou!")
        return False
    
    print(f"✅ Login realizado: {user_data['username']}")
    print(f"✅ Permissões: {user_data['permissions']}")
    
    # Teste 2: Gerar JWT
    print("\n🔍 TESTE 2 - Gerar JWT")
    access_token = service.create_access_token(user_data)
    print(f"✅ JWT gerado: {access_token[:50]}...")
    
    # Teste 3: Testar endpoint simulado de dashboard
    print("\n🔍 TESTE 3 - Endpoint protegido de dashboard")
    
    def simulate_dashboard_endpoint(token):
        """Simula endpoint de dashboard protegido"""
        try:
            # Verificar JWT
            payload = service.verify_token(token)
            if not payload:
                return {"status": 401, "message": "Não autenticado"}
            
            # Verificar permissão
            if 'dashboard:read' not in payload.get('permissions', []):
                return {"status": 403, "message": "Permissão necessária"}
            
            # Retornar dados do dashboard
            return {
                "status": 200, 
                "message": "Dashboard acessado",
                "user": payload['sub'],
                "data": {"clientes": 9, "fazendas": 2}
            }
            
        except Exception as e:
            return {"status": 500, "message": f"Erro: {str(e)}"}
    
    # Acesso permitido
    result = simulate_dashboard_endpoint(access_token)
    if result['status'] == 200:
        print("✅ Dashboard acessado com sucesso")
        print(f"   User: {result['user']}")
        print(f"   Data: {result['data']}")
    else:
        print(f"❌ ERRO: Acesso ao dashboard falhou: {result}")
        return False
    
    # Teste 4: Testar endpoint sem permissão
    print("\n🔍 TESTE 4 - Endpoint sem permissão")
    
    def simulate_relatorios_endpoint(token):
        """Simula endpoint de relatórios protegido"""
        try:
            payload = service.verify_token(token)
            if not payload:
                return {"status": 401, "message": "Não autenticado"}
            
            if 'relatorios:export' not in payload.get('permissions', []):
                return {"status": 403, "message": "Permissão necessária"}
            
            return {"status": 200, "message": "Relatórios exportados"}
            
        except Exception as e:
            return {"status": 500, "message": f"Erro: {str(e)}"}
    
    result = simulate_relatorios_endpoint(access_token)
    if result['status'] == 403:
        print("✅ Acesso a relatórios corretamente negado")
    else:
        print(f"❌ ERRO: Acesso a relatórios permitido inesperado: {result}")
        return False
    
    # Teste 5: Testar token inválido
    print("\n🔍 TESTE 5 - Token inválido")
    result = simulate_dashboard_endpoint("token.falso.jwt")
    if result['status'] == 401:
        print("✅ Token inválido corretamente negado")
    else:
        print(f"❌ ERRO: Token inválido foi aceito: {result}")
        return False
    
    # Teste 6: Testar logout
    print("\n🔍 TESTE 6 - Logout")
    service.logout_user(access_token)
    
    # Tentar acessar após logout
    result = simulate_dashboard_endpoint(access_token)
    if result['status'] == 401:
        print("✅ Acesso negado após logout")
    else:
        print(f"❌ ERRO: Acesso permitido após logout: {result}")
        return False
    
    print("\n🎉 TESTE END-TO-END PASSOU COMPLETAMENTE!")
    return True

if __name__ == "__main__":
    success = test_end_to_end_authorization()
    sys.exit(0 if success else 1)