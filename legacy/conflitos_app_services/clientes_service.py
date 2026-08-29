"""
Precision VRT Solo - Serviço do Módulo Clientes - IMPLEMENTAÇÃO REAL
Toda consulta ao banco e regra de negócio centralizada aqui.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, select
from typing import List, Optional
from datetime import datetime
import uuid

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
            query = text("""
                SELECT id, tenant_id, nome, cpf_cnpj, telefone, email, endereco, 
                       cidade, estado, cep, area_total_hectares, data_nascimento, 
                       ativo, criado_em
                FROM clientes 
                WHERE ativo = 1
            """)
            result = self.db.execute(query)
            clientes = result.fetchall()
            
            return [
                {
                    "id": row.id,
                    "nome": row.nome,
                    "email": row.email,
                    "telefone": row.telefone,
                    "cpf_cnpj": row.cpf_cnpj,
                    "endereco": row.endereco,
                    "cidade": row.cidade,
                    "estado": row.estado,
                    "cep": row.cep,
                    "area_total_hectares": row.area_total_hectares,
                    "ativo": row.ativo,
                    "criado_em": row.criado_em if row.criado_em else None,
                }
                for row in clientes
            ]
        except Exception as e:
            print(f"Erro ao listar clientes: {e}")
            return []

    def obter(self, cliente_id: str) -> Optional[dict]:
        """Obtém um cliente específico pelo ID."""
        try:
            query = text("""
                SELECT id, tenant_id, nome, cpf_cnpj, telefone, email, endereco, 
                       cidade, estado, cep, area_total_hectares, data_nascimento, 
                       ativo, criado_em
                FROM clientes 
                WHERE id = :id
            """)
            result = self.db.execute(query, {"id": cliente_id})
            row = result.fetchone()
            
            if row:
                return {
                    "id": row.id,
                    "nome": row.nome,
                    "email": row.email,
                    "telefone": row.telefone,
                    "cpf_cnpj": row.cpf_cnpj,
                    "endereco": row.endereco,
                    "cidade": row.cidade,
                    "estado": row.estado,
                    "cep": row.cep,
                    "area_total_hectares": row.area_total_hectares,
                    "ativo": row.ativo,
                    "criado_em": row.criado_em if row.criado_em else None,
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
            existing_query = text("SELECT id FROM clientes WHERE email = :email")
            existing_result = self.db.execute(existing_query, {"email": email})
            if existing_result.fetchone():
                raise ValueError("Email já cadastrado")
            
            # Criar cliente
            insert_query = text("""
                INSERT INTO clientes (id, tenant_id, nome, cpf_cnpj, telefone, email, 
                                   endereco, cidade, estado, cep, area_total_hectares, 
                                   data_nascimento, ativo, criado_em)
                VALUES (:id, :tenant_id, :nome, :cpf_cnpj, :telefone, :email, 
                       :endereco, :cidade, :estado, :cep, :area_total_hectares, 
                       :data_nascimento, :ativo, datetime('now'))
                RETURNING id, nome, email, telefone, cpf_cnpj, endereco, cidade, 
                         estado, cep, area_total_hectares, ativo, criado_em
            """)
            
            params = {
                "id": str(uuid.uuid4()),
                "tenant_id": kwargs.get('tenant_id', 'default'),
                "nome": nome,
                "cpf_cnpj": kwargs.get('cpf_cnpj'),
                "telefone": kwargs.get('telefone'),
                "email": email,
                "endereco": kwargs.get('endereco'),
                "cidade": kwargs.get('cidade'),
                "estado": kwargs.get('estado'),
                "cep": kwargs.get('cep'),
                "area_total_hectares": kwargs.get('area_total_hectares'),
                "data_nascimento": kwargs.get('data_nascimento'),
                "ativo": kwargs.get('ativo', True)
            }
            
            result = self.db.execute(insert_query, params)
            row = result.fetchone()
            self.db.commit()
            
            return {
                "id": row.id,
                "nome": row.nome,
                "email": row.email,
                "telefone": row.telefone,
                "cpf_cnpj": row.cpf_cnpj,
                "endereco": row.endereco,
                "cidade": row.cidade,
                "estado": row.estado,
                "cep": row.cep,
                "area_total_hectares": row.area_total_hectares,
                "ativo": row.ativo,
                "criado_em": row.criado_em if row.criado_em else None,
            }
        except Exception as e:
            print(f"Erro ao criar cliente: {e}")
            self.db.rollback()
            raise

    def atualizar(self, cliente_id: str, **kwargs) -> dict:
        """Atualiza um cliente existente."""
        try:
            # Verificar se cliente existe
            check_query = text("SELECT id FROM clientes WHERE id = :id")
            result = self.db.execute(check_query, {"id": cliente_id})
            if not result.fetchone():
                raise ValueError("Cliente não encontrado")
            
            # Construir query de atualização dinamicamente
            update_fields = []
            params = {"id": cliente_id}
            
            for key, value in kwargs.items():
                if value is not None and key in ['nome', 'cpf_cnpj', 'telefone', 'email', 
                                               'endereco', 'cidade', 'estado', 'cep', 
                                               'area_total_hectares', 'data_nascimento']:
                    update_fields.append(f"{key} = :{key}")
                    params[key] = value
            
            if not update_fields:
                raise ValueError("Nenhum campo válido para atualizar")
            
            update_fields.append("criado_em = criado_em")  # Manter data de criação
            
            update_query = text(f"""
                UPDATE clientes 
                SET {', '.join(update_fields)}
                WHERE id = :id
                RETURNING id, nome, email, telefone, cpf_cnpj, endereco, cidade, 
                         estado, cep, area_total_hectares, ativo, criado_em
            """)
            
            result = self.db.execute(update_query, params)
            row = result.fetchone()
            self.db.commit()
            
            return {
                "id": row.id,
                "nome": row.nome,
                "email": row.email,
                "telefone": row.telefone,
                "cpf_cnpj": row.cpf_cnpj,
                "endereco": row.endereco,
                "cidade": row.cidade,
                "estado": row.estado,
                "cep": row.cep,
                "area_total_hectares": row.area_total_hectares,
                "ativo": row.ativo,
                "criado_em": row.criado_em if row.criado_em else None,
            }
        except Exception as e:
            print(f"Erro ao atualizar cliente {cliente_id}: {e}")
            self.db.rollback()
            raise

    def excluir(self, cliente_id: str) -> bool:
        """Exclui um cliente (desativa logicamente)."""
        try:
            # Verificar se cliente existe
            check_query = text("SELECT id FROM clientes WHERE id = :id")
            result = self.db.execute(check_query, {"id": cliente_id})
            if not result.fetchone():
                raise ValueError("Cliente não encontrado")
            
            # Desativar cliente em vez de excluir
            update_query = text("UPDATE clientes SET ativo = 0 WHERE id = :id")
            self.db.execute(update_query, {"id": cliente_id})
            self.db.commit()
            
            return True
        except Exception as e:
            print(f"Erro ao excluir cliente {cliente_id}: {e}")
            self.db.rollback()
            raise