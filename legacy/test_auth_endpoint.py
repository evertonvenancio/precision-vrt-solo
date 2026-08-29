#!/usr/bin/env python3
"""
Teste do caminho de produção real: Frontend → Endpoint → AuthService → Banco

Testa o endpoint HTTP completo de login
"""

import sys
import os
sys.path.append('.')

from fastapi.testclient import TestClient
from app.web.auth import router, auth_service
import json

def test_auth_endpoint():
    """Teste do endpoint HTTP de autenticação"""
    
    print("🧪 TESTE - CAMINHO DE PRODUÇÃO: HTTP")
    print("=" * 50)
    
    # Criar cliente de teste
    client = TestClient(router)
    
    # Teste 1: Login HTTP válido
    print("\n🔍 TESTE 1 - Login HTTP válido")
    login_data = {
        "usuario": "admin",
        "senha": "admin123",
        "remember_me": False
    }
    
    response = client.post("/login", data=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 303:  # Redirecionamento para dashboard
        print("✅ Login HTTP válido - redirecionado para dashboard")
        # Verificar se tokens foram configurados nos cookies
        cookies = response.cookies
        if "access_token" in cookies and "refresh_token" not in cookies:  # Sem remember_me
            print("✅ Access token configurado no cookie")
        else:
            print("❌ ERRO: Tokens não configurados nos cookies!")
            return False
    else:
        print(f"❌ ERRO: Login HTTP falhou com status {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False
    
    # Teste 2: Verificar usuário atual via endpoint
    print("\n🔍 TESTE 2 - Verificar usuário atual")
    # Obter token do cookie
    access_token = response.cookies.get("access_token")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/current-user", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        if user_data.get("success") and "user" in user_data:
            user = user_data["user"]
            print(f"✅ Usuário atual: {user['username']} (ID: {user['id']})")
        else:
            print("❌ ERRO: Resposta inválida do /current-user")
            return False
    else:
        print(f"❌ ERRO: Verificação falhou com status {response.status_code}")
        return False
    
    # Teste 3: Logout HTTP
    print("\n🔍 TESTE 3 - Logout HTTP")
    response = client.get("/logout")
    
    if response.status_code == 303:  # Redirecionamento para login
        print("✅ Logout HTTP - redirecionado para login")
        # Verificar se tokens foram removidos
        cookies = response.cookies
        if "access_token" not in cookies and "refresh_token" not in cookies:
            print("✅ Tokens removidos dos cookies")
        else:
            print("❌ ERRO: Tokens não foram removidos!")
            return False
    else:
        print(f"❌ ERRO: Logout HTTP falhou com status {response.status_code}")
        return False
    
    # Teste 4: Tentar acessar endpoint com token inválido
    print("\n🔍 TESTE 4 - Acesso com token inválido")
    invalid_token = "token.falso.jwt.incompleto"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = client.get("/current-user", headers=headers)
    
    if response.status_code == 401:  # Unauthorized
        print("✅ Token inválido corretamente rejeitado")
    else:
        print(f"❌ ERRO: Token inválido foi aceito com status {response.status_code}")
        return False
    
    print("\n🎉 TESTE HTTP COMPLETO PASSOU!")
    return True

if __name__ == "__main__":
    success = test_auth_endpoint()
    sys.exit(0 if success else 1)