"""
Precision VRT Solo - Status Codes de Autorização

Documentação de status HTTP para sistema de autorização.
"""

# HTTP 401 - Não Autenticado
# Usado quando:
# * Token ausente
# * Token inválido (assina incorreta, formato inválido)
# * Token expirado
# * Sessão não autenticável
# * Usuário desativado no banco (mesmo com token válido)
# * JWT malformado

# HTTP 403 - Proibido
# Usado quando:
# * Usuário autenticado (token válido, ativo no banco)
# * Mas não possui a permissão necessária para a operação
# * Verificação de permissão falhou

# Fluxo de decisão:
# 1. Verificar token → falha → 401
# 2. Verificar usuário ativo → falha → 401  
# 3. Verificar permissão → falha → 403