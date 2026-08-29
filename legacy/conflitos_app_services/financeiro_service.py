"""
Precision VRT Solo - Serviço do Módulo Financeiro - IMPLEMENTAÇÃO REAL COM SQLALCHEMY
Toda consulta ao banco e regra de negócio centralizada aqui.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import uuid

from models.orcamento_sql import Orcamento, TipoOrcamento, StatusOrcamento
from models.cliente_sql import Cliente
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
            query = select(Cliente).where(Cliente.ativo == True)
            result = self.db.execute(query)
            clientes = result.scalars().all()
            
            return [cliente.to_dict() for cliente in clientes]
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
            cliente_query = select(Cliente).where(Cliente.id == cliente_id)
            cliente_result = self.db.execute(cliente_query)
            cliente = cliente_result.scalar_one_or_none()
            
            if not cliente:
                raise ValueError("Cliente não encontrado")
            
            # Calcular valores baseado em valor total
            valor_bruto = valor_total
            desconto_percentual = kwargs.get('desconto_percentual', 0)
            valor_liquido = valor_total * (1 - desconto_percentual / 100)
            
            # Criar orçamento com campos existentes
            orcamento = Orcamento(
                id=str(uuid.uuid4()),
                tenant_id=kwargs.get('tenant_id', 'default'),  # 'default' tenant is required
                cliente_id=cliente_id,
                usuario_id=kwargs.get('usuario_id', None),  # REMOVED: 'default' fallback
                valor_total_bruto=valor_bruto,
                desconto_percentual=desconto_percentual,
                valor_total_liquido=valor_liquido,
                status=kwargs.get('status', 'rascunho'),
                criado_em=datetime.now(),
                atualizado_em=datetime.now()
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
            
            # Atualizar campos existentes
            for key, value in kwargs.items():
                if hasattr(orcamento, key) and value is not None:
                    setattr(orcamento, key, value)
            
            # Recalcular valores se necessário
            if 'valor_total_bruto' in kwargs:
                desconto_percentual = kwargs.get('desconto_percentual', orcamento.desconto_percentual)
                orcamento.valor_total_liquido = kwargs['valor_total_bruto'] * (1 - desconto_percentual / 100)
            
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