"""
Precision VRT Solo - Serviço do Módulo Clientes - IMPLEMENTAÇÃO REAL
Toda consulta ao banco e regra de negócio centralizada aqui.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from models.cliente import Cliente
from core.seguranca.permissions import get_permissoes


class ClientesService:
    """
    Serviço central do módulo Clientes.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db)

    def listar(self) -> List[dict]:
        """Lista todos os clientes ativos."""
        try:
            query = select(Cliente).where(Cliente.ativo == True)
            result = self.db.execute(query)
            clientes = result.scalars().all()
            
            # Converter para formato compatível com frontend
            return [
                {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "email": cliente.email,
                    "telefone": cliente.telefone,
                    "cpf_cnpj": cliente.cpf_cnpj,
                    "endereco": cliente.endereco,
                    "cidade": cliente.cidade,
                    "estado": cliente.estado,
                    "cep": cliente.cep,
                    "area_total_hectares": cliente.area_total_hectares,
                    "ativo": cliente.ativo,
                    "criado_em": cliente.criado_em.isoformat() if cliente.criado_em else None,
                }
                for cliente in clientes
            ]
        except Exception as e:
            print(f"Erro ao listar clientes: {e}")
            return []

    def obter(self, cliente_id: str) -> Optional[dict]:
        """Obtém um cliente específico pelo ID."""
        try:
            query = select(Cliente).where(Cliente.id == cliente_id)
            result = self.db.execute(query)
            cliente = result.scalar_one_or_none()
            
            if cliente:
                return {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "email": cliente.email,
                    "telefone": cliente.telefone,
                    "cpf_cnpj": cliente.cpf_cnpj,
                    "endereco": cliente.endereco,
                    "cidade": cliente.cidade,
                    "estado": cliente.estado,
                    "cep": cliente.cep,
                    "area_total_hectares": cliente.area_total_hectares,
                    "ativo": cliente.ativo,
                    "criado_em": cliente.criado_em.isoformat() if cliente.criado_em else None,
                }
            return None
        except Exception as e:
            print(f"Erro ao obter cliente {cliente_id}: {e}")
            return None

    def criar(self, nome: str, email: str, **kwargs) -> dict:
        """Cria um novo cliente."""
        try:
            # Validar campos obrigatórios
            if not nome or not email:
                raise ValueError("Nome e email são obrigatórios")
            
            # Verificar se email já existe
            existing_query = select(Cliente).where(Cliente.email == email)
            existing_result = self.db.execute(existing_query)
            if existing_result.scalar_one_or_none():
                raise ValueError("Email já cadastrado")
            
            # Criar cliente
            cliente = Cliente(nome=nome, email=email, **kwargs)
            self.db.add(cliente)
            self.db.commit()
            self.db.refresh(cliente)
            
            return {
                "id": cliente.id,
                "nome": cliente.nome,
                "email": cliente.email,
                "telefone": cliente.telefone,
                "cpf_cnpj": cliente.cpf_cnpj,
                "endereco": cliente.endereco,
                "cidade": cliente.cidade,
                "estado": cliente.estado,
                "cep": cliente.cep,
                "area_total_hectares": cliente.area_total_hectares,
                "ativo": cliente.ativo,
                "criado_em": cliente.criado_em.isoformat() if cliente.criado_em else None,
            }
        except Exception as e:
            print(f"Erro ao criar cliente: {e}")
            self.db.rollback()
            raise

    def atualizar(self, cliente_id: str, **kwargs) -> dict:
        """Atualiza um cliente existente."""
        try:
            query = select(Cliente).where(Cliente.id == cliente_id)
            result = self.db.execute(query)
            cliente = result.scalar_one_or_none()
            
            if not cliente:
                raise ValueError("Cliente não encontrado")
            
            # Atualizar campos
            for key, value in kwargs.items():
                if hasattr(cliente, key) and value is not None:
                    setattr(cliente, key, value)
            
            cliente.atualizado_em = datetime.now()
            self.db.commit()
            self.db.refresh(cliente)
            
            return {
                "id": cliente.id,
                "nome": cliente.nome,
                "email": cliente.email,
                "telefone": cliente.telefone,
                "cpf_cnpj": cliente.cpf_cnpj,
                "endereco": cliente.endereco,
                "cidade": cliente.cidade,
                "estado": cliente.estado,
                "cep": cliente.cep,
                "area_total_hectares": cliente.area_total_hectares,
                "ativo": cliente.ativo,
                "criado_em": cliente.criado_em.isoformat() if cliente.criado_em else None,
            }
        except Exception as e:
            print(f"Erro ao atualizar cliente {cliente_id}: {e}")
            self.db.rollback()
            raise

    def excluir(self, cliente_id: str) -> bool:
        """Exclui um cliente (desativa logicamente)."""
        try:
            query = select(Cliente).where(Cliente.id == cliente_id)
            result = self.db.execute(query)
            cliente = result.scalar_one_or_none()
            
            if not cliente:
                raise ValueError("Cliente não encontrado")
            
            # Desativar cliente em vez de excluir
            cliente.ativo = False
            cliente.atualizado_em = datetime.now()
            self.db.commit()
            
            return True
        except Exception as e:
            print(f"Erro ao excluir cliente {cliente_id}: {e}")
            self.db.rollback()
            raise