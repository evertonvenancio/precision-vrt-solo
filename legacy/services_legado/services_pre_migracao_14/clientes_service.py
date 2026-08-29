"""
Precision VRT Solo - Serviço do Módulo Clientes
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.seguranca.permissions import get_permissoes


class ClientesService:
    """
    Serviço central do módulo Clientes.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session, user_data: dict = None):
        self.db = db
        self.user_data = user_data or {}

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db, self.user_data)

    def listar(self) -> List[Dict[str, Any]]:
        """Lista todos os clientes ativos do banco."""
        try:
            result = self.db.execute(text("""
                SELECT id, nome, cpf_cnpj, telefone, email, cidade, 
                       estado, area_total_hectares, ativo, criado_em
                FROM clientes 
                WHERE ativo = 1 
                ORDER BY nome ASC
            """))
            
            clientes = []
            for row in result.fetchall():
                clientes.append({
                    "id": row[0],
                    "nome": row[1],
                    "cpf_cnpj": row[2],
                    "telefone": row[3],
                    "email": row[4],
                    "cidade": row[5],
                    "estado": row[6],
                    "area_total_hectares": row[7],
                    "ativo": row[8],
                    "criado_em": str(row[9]) if row[9] else None
                })
            return clientes
        except Exception as e:
            print(f"Erro ao listar clientes: {e}")
            return []

    def obter(self, cliente_id: str) -> Optional[Dict[str, Any]]:
        """Obter um cliente específico pelo ID."""
        try:
            result = self.db.execute(text("""
                SELECT id, nome, cpf_cnpj, telefone, email, cidade, 
                       estado, area_total_hectares, ativo, criado_em
                FROM clientes 
                WHERE id = ? AND ativo = 1
            """), (cliente_id,))
            
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "nome": row[1],
                    "cpf_cnpj": row[2],
                    "telefone": row[3],
                    "email": row[4],
                    "cidade": row[5],
                    "estado": row[6],
                    "area_total_hectares": row[7],
                    "ativo": row[8],
                    "criado_em": str(row[9]) if row[9] else None
                }
            return None
        except Exception as e:
            print(f"Erro ao obter cliente: {e}")
            return None

    def criar(self, nome: str, cpf_cnpj: str, telefone: str, email: str, 
              cidade: str, estado: str, area_total_hectares: float = 0.0) -> Dict[str, Any]:
        """Criar um novo cliente no banco."""
        try:
            # Verificar se email já existe
            result = self.db.execute(text("SELECT id FROM clientes WHERE email = ?"), (email,))
            if result.fetchone():
                return {"success": False, "detail": "Email já cadastrado"}
            
            # Inserir novo cliente
            result = self.db.execute(text("""
                INSERT INTO clientes (
                    nome, cpf_cnpj, telefone, email, cidade, estado, 
                    area_total_hectares, ativo, criado_em
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            """), (nome, cpf_cnpj, telefone, email, cidade, estado, area_total_hectares, datetime.now()))
            
            self.db.commit()
            
            # Retornar cliente criado
            cliente_id = result.lastrowid
            if cliente_id:
                return {
                    "success": True, 
                    "message": "Cliente criado com sucesso",
                    "cliente": self.obter(cliente_id)
                }
            else:
                return {"success": False, "detail": "Erro ao criar cliente"}
                
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao criar cliente: {e}")
            return {"success": False, "detail": f"Erro ao criar cliente: {str(e)}"}

    def atualizar(self, cliente_id: str, nome: str, cpf_cnpj: str, telefone: str, 
                  email: str, cidade: str, estado: str, area_total_hectares: float = 0.0) -> Dict[str, Any]:
        """Atualizar um cliente existente."""
        try:
            # Verificar se cliente existe
            cliente = self.obter(cliente_id)
            if not cliente:
                return {"success": False, "detail": "Cliente não encontrado"}
            
            # Verificar se email já existe para outro cliente
            result = self.db.execute(text("SELECT id FROM clientes WHERE email = ? AND id != ?"), (email, cliente_id))
            if result.fetchone():
                return {"success": False, "detail": "Email já cadastrado para outro cliente"}
            
            # Atualizar cliente
            self.db.execute(text("""
                UPDATE clientes 
                SET nome = ?, cpf_cnpj = ?, telefone = ?, email = ?, 
                    cidade = ?, estado = ?, area_total_hectares = ?, 
                    atualizado_em = ?
                WHERE id = ?
            """), (nome, cpf_cnpj, telefone, email, cidade, estado, area_total_hectares, datetime.now(), cliente_id))
            
            self.db.commit()
            
            return {
                "success": True, 
                "message": "Cliente atualizado com sucesso",
                "cliente": self.obter(cliente_id)
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao atualizar cliente: {e}")
            return {"success": False, "detail": f"Erro ao atualizar cliente: {str(e)}"}

    def excluir(self, cliente_id: str, justificativa: str) -> Dict[str, Any]:
        """Excluir um cliente (marcar como inativo)."""
        try:
            # Verificar se cliente existe
            cliente = self.obter(cliente_id)
            if not cliente:
                return {"success": False, "detail": "Cliente não encontrado"}
            
            # Verificar se usuário tem permissão para excluir clientes
            user_permissions = self.user_data.get('permissions', [])
            if 'clientes:delete' not in user_permissions:
                return {"success": False, "detail": "Permissão necessária: clientes:delete"}
            
            # Marcar cliente como inativo
            self.db.execute(text("""
                UPDATE clientes 
                SET ativo = 0, atualizado_em = ?
                WHERE id = ?
            """), (datetime.now(), cliente_id))
            
            # Registrar exclusão (opcional)
            self.db.execute(text("""
                INSERT INTO exclusoes_clientes (cliente_id, justificativa, excluido_por, excluido_em)
                VALUES (?, ?, ?, ?)
            """), (cliente_id, justificativa, self.user_data.get('username'), datetime.now()))
            
            self.db.commit()
            
            return {
                "success": True, 
                "message": "Cliente excluído com sucesso",
                "redirect": "/clientes"
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao excluir cliente: {e}")
            return {"success": False, "detail": f"Erro ao excluir cliente: {str(e)}"}
