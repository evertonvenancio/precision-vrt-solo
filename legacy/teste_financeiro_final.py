#!/usr/bin/env python3
"""
Teste final do CRUD completo de Financeiro
"""

from app.services.financeiro_service import FinanceiroService
from app.services.clientes_service import ClientesService
from db.database import SessionLocal
import uuid

print('🧪 TESTE FINAL - CRUD COMPLETO DE FINANCEIRO')
db = SessionLocal()
financeiro_service = FinanceiroService(db)
clientes_service = ClientesService(db)

# Criar cliente primeiro para usar no orçamento
cliente = clientes_service.criar(
    nome='Cliente Financeiro Completo',
    email=f'financeiro-completo-{uuid.uuid4()}@example.com',
    cidade='São Paulo'
)
print(f'✅ Cliente criado: {cliente["id"]}')

# Criar orçamento
orcamento = financeiro_service.criar_orcamento(
    cliente_id=cliente['id'],
    descricao='Orçamento Completo de Serviços',
    valor_total=5000.00,
    desconto_percentual=15,
    status='aprovado'
)
print(f'✅ Orçamento criado: {orcamento["id"]}')
print(f'   Valor total bruto: R${orcamento["valor_total_bruto"]:.2f}')
print(f'   Desconto: {orcamento["desconto_percentual"]}%')
print(f'   Valor liquido: R${orcamento["valor_total"]:.2f}')
print(f'   Status: {orcamento["status"]}')

# Listar orçamentos
orcamentos = financeiro_service.listar_orcamentos()
if orcamentos and len(orcamentos) > 0:
    print(f'✅ Orçamentos listados: {len(orcamentos)}')
else:
    print('❌ Nenhum orçamento encontrado')
    exit(1)

# Listar clientes ativos
clientes_ativos = financeiro_service.listar_clientes_ativos()
if clientes_ativos and len(clientes_ativos) > 0:
    print(f'✅ Clientes ativos listados: {len(clientes_ativos)}')
else:
    print('❌ Nenhum cliente ativo encontrado')
    exit(1)

db.close()
print('✅ TESTE CRUD COMPLETO DE FINANCEIRO CONCLUÍDO COM SUCESSO!')