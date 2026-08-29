"""
Precision VRT Solo - Serviço do Módulo Financeiro
Implementação REAL usando apenas estruturas comprovadas no banco.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.seguranca.permissions import get_permissoes


class FinanceiroService:
    """
    Serviço central do módulo Financeiro.
    Responsável por toda consulta ao banco e regra de negócio.
    Implementação REAL usando tabela orcamentos existente.
    """

    def __init__(self, db: Session, user_data: dict = None):
        self.db = db
        self.user_data = user_data or {}

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db, self.user_data)

    def listar_orcamentos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os orçamentos existentes no banco.
        Fonte real: tabela orcamentos
        """
        try:
            # Aplicar filtro por tenant se existir
            tenant_filter = ""
            tenant_id = self.user_data.get('tenant_id')
            if tenant_id:
                tenant_filter = "AND tenant_id = :tenant_id"
                
            result = self.db.execute(text(f"""
                SELECT id, tenant_id, cliente_id, usuario_id, data_emissao, 
                       valor_total_bruto, desconto_percentual, valor_total_liquido, 
                       status, criado_em, atualizado_em
                FROM orcamentos 
                WHERE status != 'excluido' {tenant_filter}
                ORDER BY data_emissao DESC
            """), {'tenant_id': tenant_id} if tenant_id else {})
            
            orcamentos = []
            for row in result.fetchall():
                orcamentos.append({
                    "id": row[0],
                    "tenant_id": row[1],
                    "cliente_id": row[2],
                    "usuario_id": row[3],
                    "data_emissao": str(row[4]) if row[4] else None,
                    "valor_total_bruto": float(row[5]) if row[5] else 0,
                    "desconto_percentual": float(row[6]) if row[6] else 0,
                    "valor_total_liquido": float(row[7]) if row[7] else 0,
                    "status": row[8],
                    "criado_em": str(row[9]) if row[9] else None,
                    "atualizado_em": str(row[10]) if row[10] else None
                })
            return orcamentos
        except Exception as e:
            print(f"Erro ao listar orçamentos: {e}")
            return []

    def listar_clientes_ativos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os clientes ativos no banco.
        Fonte real: tabela clientes
        """
        try:
            # Aplicar filtro por tenant se existir
            tenant_filter = ""
            tenant_id = self.user_data.get('tenant_id')
            if tenant_id:
                tenant_filter = "AND tenant_id = :tenant_id"
                
            result = self.db.execute(text(f"""
                SELECT id, tenant_id, nome, cpf_cnpj, telefone, email, cidade, 
                       estado, area_total_hectares, ativo, criado_em
                FROM clientes 
                WHERE ativo = 1 {tenant_filter}
                ORDER BY nome ASC
            """), {'tenant_id': tenant_id} if tenant_id else {})
            
            clientes = []
            for row in result.fetchall():
                clientes.append({
                    "id": row[0],
                    "tenant_id": row[1],
                    "nome": row[2],
                    "cpf_cnpj": row[3],
                    "telefone": row[4],
                    "email": row[5],
                    "cidade": row[6],
                    "estado": row[7],
                    "area_total_hectares": float(row[8]) if row[8] else 0,
                    "ativo": row[9],
                    "criado_em": str(row[10]) if row[10] else None
                })
            return clientes
        except Exception as e:
            print(f"Erro ao listar clientes ativos: {e}")
            return []

    def salvar_orcamento(self, cliente_id: str, dados_orcamento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Salva um novo orçamento no banco.
        Fonte real: tabela orcamentos
        
        Parâmetros esperados:
        - cliente_id: ID do cliente
        - dados_orcamento: Dict com valor_total_bruto, desconto_percentual, status
        """
        try:
            # Validar permissão
            user_permissions = self.user_data.get('permissions', [])
            if 'financeiro:write' not in user_permissions:
                return {"success": False, "detail": "Permissão necessária: financeiro:write"}
            
            # Validar dados obrigatórios
            if not cliente_id:
                return {"success": False, "detail": "ID do cliente obrigatório"}
                
            valor_total_bruto = dados_orcamento.get('valor_total_bruto', 0)
            desconto_percentual = dados_orcamento.get('desconto_percentual', 0)
            status = dados_orcamento.get('status', 'rascunho')
            
            # Calcular valor total líquido
            desconto_valor = (valor_total_bruto * desconto_percentual) / 100
            valor_total_liquido = valor_total_bruto - desconto_valor
            
            # Inserir orçamento
            result = self.db.execute(text("""
                INSERT INTO orcamentos (
                    tenant_id, cliente_id, usuario_id, data_emissao,
                    valor_total_bruto, desconto_percentual, valor_total_liquido,
                    status, criado_em
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """), (
                self.user_data.get('tenant_id', 'default'),
                cliente_id,
                self.user_data.get('user_id'),
                datetime.now(),
                valor_total_bruto,
                desconto_percentual,
                valor_total_liquido,
                status,
                datetime.now()
            ))
            
            self.db.commit()
            
            # Retornar orçamento criado
            orcamento_id = result.lastrowid
            if orcamento_id:
                return {
                    "success": True, 
                    "message": "Orçamento salvo com sucesso",
                    "orcamento": self._obter_orcamento(orcamento_id)
                }
            else:
                return {"success": False, "detail": "Erro ao salvar orçamento"}
                
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao salvar orçamento: {e}")
            return {"success": False, "detail": f"Erro ao salvar orçamento: {str(e)}"}

    def _obter_orcamento(self, orcamento_id: str) -> Optional[Dict[str, Any]]:
        """Obter um orçamento específico pelo ID (método auxiliar)."""
        try:
            result = self.db.execute(text("""
                SELECT id, tenant_id, cliente_id, usuario_id, data_emissao, 
                       valor_total_bruto, desconto_percentual, valor_total_liquido, 
                       status, criado_em, atualizado_em
                FROM orcamentos 
                WHERE id = ? AND status != 'excluido'
            """), (orcamento_id,))
            
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "tenant_id": row[1],
                    "cliente_id": row[2],
                    "usuario_id": row[3],
                    "data_emissao": str(row[4]) if row[4] else None,
                    "valor_total_bruto": float(row[5]) if row[5] else 0,
                    "desconto_percentual": float(row[6]) if row[6] else 0,
                    "valor_total_liquido": float(row[7]) if row[7] else 0,
                    "status": row[8],
                    "criado_em": str(row[9]) if row[9] else None,
                    "atualizado_em": str(row[10]) if row[10] else None
                }
            return None
        except Exception as e:
            print(f"Erro ao obter orçamento: {e}")
            return None