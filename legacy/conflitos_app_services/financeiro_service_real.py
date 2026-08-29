"""
Precision VRT Solo - Serviço do Módulo Financeiro - IMPLEMENTAÇÃO REAL
Toda consulta ao banco e regra de negócio centralizada aqui.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
import uuid

from models.financeiro import Orcamento, TipoOrcamento, StatusOrcamento
from core.seguranca.permissions import get_permissoes


class FinanceiroService:
    """
    Serviço central do módulo Financeiro.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db)

    def listar_orcamentos(self) -> List[dict]:
        """Lista todos os orçamentos."""
        try:
            query = select(Orcamento)
            result = self.db.execute(query)
            orcamentos = result.scalars().all()
            
            return [orcamento.to_dict() for orcamento in orcamentos]
        except Exception as e:
            print(f"Erro ao listar orçamentos: {e}")
            return []

    def listar_clientes_ativos(self) -> List[dict]:
        """Lista clientes ativos."""
        try:
            # Importar aqui para evitar circular import
            from models.cliente import Cliente
            
            query = select(Cliente).where(Cliente.ativo == True)
            result = self.db.execute(query)
            clientes = result.scalars().all()
            
            return [
                {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "email": cliente.email,
                    "telefone": cliente.telefone,
                    "cpf_cnpj": cliente.cpf_cnpj,
                    "ativo": cliente.ativo,
                    "criado_em": cliente.criado_em.isoformat() if cliente.criado_em else None,
                }
                for cliente in clientes
            ]
        except Exception as e:
            print(f"Erro ao listar clientes ativos: {e}")
            return []

    def criar_orcamento(self, cliente_id: str, descricao: str, valor_total: float, **kwargs) -> dict:
        """Cria um novo orçamento."""
        try:
            # Validar campos obrigatórios
            if not cliente_id or not descricao or not valor_total:
                raise ValueError("Cliente ID, descrição e valor total são obrigatórios")
            
            # Verificar se cliente existe
            from models.cliente import Cliente
            cliente_query = select(Cliente).where(Cliente.id == cliente_id)
            cliente_result = self.db.execute(cliente_query)
            cliente = cliente_result.scalar_one_or_none()
            
            if not cliente:
                raise ValueError("Cliente não encontrado")
            
            # Criar orçamento
            orcamento = Orcamento(
                id=str(uuid.uuid4()) if 'uuid' not in locals() else str(uuid.uuid4()),
                tenant_id=kwargs.get('tenant_id', 'default'),
                cliente_id=cliente_id,
                tipo=kwargs.get('tipo', TipoOrcamento.SERVICO),
                status=kwargs.get('status', StatusOrcamento.RASCUNHO),
                descricao=descricao,
                valor_total=Decimal(str(valor_total)),
                data_emissao=kwargs.get('data_emissao', date.today()),
                data_validade=kwargs.get('data_validade', date.today()),
                **kwargs
            )
            
            self.db.add(orcamento)
            self.db.commit()
            self.db.refresh(orcamento)
            
            return orcamento.to_dict()
        except Exception as e:
            print(f"Erro ao criar orçamento: {e}")
            self.db.rollback()
            raise

    def atualizar_orcamento(self, orcamento_id: str, **kwargs) -> dict:
        """Atualiza um orçamento existente."""
        try:
            query = select(Orcamento).where(Orcamento.id == orcamento_id)
            result = self.db.execute(query)
            orcamento = result.scalar_one_or_none()
            
            if not orcamento:
                raise ValueError("Orçamento não encontrado")
            
            # Atualizar campos
            for key, value in kwargs.items():
                if hasattr(orcamento, key) and value is not None:
                    setattr(orcamento, key, value)
            
            orcamento.atualizado_em = datetime.now()
            self.db.commit()
            self.db.refresh(orcamento)
            
            return orcamento.to_dict()
        except Exception as e:
            print(f"Erro ao atualizar orçamento {orcamento_id}: {e}")
            self.db.rollback()
            raise

    def excluir_orcamento(self, orcamento_id: str) -> bool:
        """Exclui um orçamento."""
        try:
            query = select(Orcamento).where(Orcamento.id == orcamento_id)
            result = self.db.execute(query)
            orcamento = result.scalar_one_or_none()
            
            if not orcamento:
                raise ValueError("Orçamento não encontrado")
            
            self.db.delete(orcamento)
            self.db.commit()
            
            return True
        except Exception as e:
            print(f"Erro ao excluir orçamento {orcamento_id}: {e}")
            self.db.rollback()
            raise