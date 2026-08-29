"""
Precision VRT Solo - Servico do Modulo Orcamentos
Toda consulta ao banco e regra de negocio centralizada aqui.
"""
import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.orcamento_sql import Orcamento as OrcamentoSQL
from models.cliente_sql import Cliente
from core.seguranca.permissions import get_permissoes


class OrcamentosService:
    """
    Servico central do modulo Orcamentos.
    Responsavel por toda consulta ao banco e regra de negocio.
    """

    def __init__(self, db: Session, tenant_id: str = 'default'):
        self.db = db
        self.tenant_id = tenant_id

    def buscar_permissoes(self) -> dict:
        """Busca as permissoes do usuario no banco."""
        return get_permissoes(self.db)

    def listar_orcamentos(self, status: str = None, limit: int = 100):
        """Lista todos os orcamentos do tenant, com filtro opcional de status.

        Args:
            status: Filtra por status especifico (rascunho, enviado, aprovado, etc.)
            limit: Limite maximo de registros.

        Returns:
            Lista de dicionarios com dados do orcamento + nome do cliente.
        """
        query = self.db.query(OrcamentoSQL).filter(
            OrcamentoSQL.tenant_id == self.tenant_id
        )
        if status:
            query = query.filter(OrcamentoSQL.status == status)
        query = query.order_by(OrcamentoSQL.criado_em.desc()).limit(limit)

        resultados = query.all()
        retorno = []
        for orc in resultados:
            d = orc.to_dict()
            # Enriquecer com nome do cliente
            cliente = self.db.query(Cliente).filter(
                Cliente.id == orc.cliente_id
            ).first()
            d['cliente_nome'] = cliente.nome if cliente else 'N/A'
            retorno.append(d)
        return retorno

    def buscar_por_id(self, orcamento_id: str):
        """Busca um orcamento pelo ID (UUID string).

        Args:
            orcamento_id: UUID do orcamento.

        Returns:
            Dicionario com dados completos ou None se nao encontrado.
        """
        orcamento = self.db.query(OrcamentoSQL).filter(
            and_(
                OrcamentoSQL.id == orcamento_id,
                OrcamentoSQL.tenant_id == self.tenant_id
            )
        ).first()

        if not orcamento:
            return None

        d = orcamento.to_dict()

        # Enriquecer com nome do cliente
        cliente = self.db.query(Cliente).filter(
            Cliente.id == orcamento.cliente_id
        ).first()
        d['cliente_nome'] = cliente.nome if cliente else 'N/A'
        d['cliente_email'] = cliente.email if cliente else None

        return d

    def listar_clientes_ativos(self):
        """Lista todos os clientes ativos do tenant para uso em formularios.

        Returns:
            Lista de dicionarios com id e nome.
        """
        clientes = self.db.query(Cliente).filter(
            and_(Cliente.tenant_id == self.tenant_id, Cliente.ativo == True)
        ).order_by(Cliente.nome).all()

        return [{"id": c.id, "nome": c.nome, "email": c.email} for c in clientes]

    def salvar_orcamento(self, dados: dict):
        """Salva um novo orcamento ou atualiza existente.

        Fluxo:
        1. Calcula valor liquido a partir de bruto e desconto.
        2. Cria Orcamento com tenant_id do contexto.
        3. Persiste no banco.

        Args:
            dados: Dicionario com cliente_id, valor_total_bruto,
                   desconto_percentual, observacoes, etc.

        Returns:
            Dicionario com o ID do orcamento salvo e dados atualizados.
        """
        cliente_id = dados.get('cliente_id')
        valor_bruto = self._parse_decimal(dados.get('valor_total_bruto', 0))
        desconto = self._parse_decimal(dados.get('desconto_percentual', 0))
        valor_liquido = valor_bruto * (1 - desconto / 100)

        if not cliente_id:
            raise ValueError("cliente_id e obrigatorio.")
        if valor_bruto <= 0:
            raise ValueError("valor_total_bruto deve ser maior que zero.")

        orcamento = OrcamentoSQL(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            cliente_id=cliente_id,
            usuario_id=dados.get('usuario_id'),
            valor_total_bruto=valor_bruto,
            desconto_percentual=desconto,
            valor_total_liquido=valor_liquido,
            status=dados.get('status', 'rascunho'),
        )
        self.db.add(orcamento)
        self.db.flush()

        self._registrar_auditoria(
            "criar", "orcamentos", dados.get('usuario_id'),
            f"Orcamento {orcamento.id} criado. Valor: R$ {valor_liquido:.2f}"
        )

        return {
            "id": orcamento.id,
            "cliente_id": orcamento.cliente_id,
            "valor_total_bruto": float(orcamento.valor_total_bruto),
            "desconto_percentual": float(orcamento.desconto_percentual),
            "valor_total_liquido": float(orcamento.valor_total_liquido),
            "status": orcamento.status,
            "data_emissao": orcamento.data_emissao.isoformat() if orcamento.data_emissao else None,
            "criado_em": orcamento.criado_em.isoformat() if orcamento.criado_em else None,
        }

    def aprovar_orcamento(self, orcamento_id: str, usuario_id: str):
        """Aprova um orcamento existente.

        Args:
            orcamento_id: UUID do orcamento.
            usuario_id: ID do usuario que esta aprovando.

        Returns:
            Dicionario com status atualizado.
        """
        orcamento = self.db.query(OrcamentoSQL).filter(
            and_(
                OrcamentoSQL.id == orcamento_id,
                OrcamentoSQL.tenant_id == self.tenant_id
            )
        ).first()

        if not orcamento:
            raise ValueError(f"Orcamento {orcamento_id} nao encontrado.")

        status_anterior = orcamento.status
        orcamento.status = 'aprovado'
        orcamento.atualizado_em = datetime.utcnow()
        self.db.flush()

        self._registrar_auditoria(
            "alterar", "orcamentos", usuario_id,
            f"Orcamento {orcamento_id} aprovado (status: {status_anterior} -> aprovado)"
        )

        return {
            "id": orcamento.id,
            "status": orcamento.status,
            "atualizado_em": orcamento.atualizado_em.isoformat() if orcamento.atualizado_em else None,
        }

    def gerar_pdf(self, orcamento_id: str) -> bytes:
        """Gera o PDF de um orcamento.

        Usa WeasyPrint para renderizar um HTML simples com os dados do orcamento.

        Args:
            orcamento_id: UUID do orcamento.

        Returns:
            Bytes do PDF gerado.
        """
        orcamento = self.buscar_por_id(orcamento_id)
        if not orcamento:
            raise ValueError(f"Orcamento {orcamento_id} nao encontrado.")

        html_content = self._render_template_orcamento_pdf(orcamento)

        try:
            from weasyprint import HTML
            pdf_bytes = HTML(
                string=html_content,
                base_url="."
            ).write_pdf()
            return pdf_bytes
        except ImportError:
            # Fallback: retornar HTML como bytes se WeasyPrint nao disponivel
            return html_content.encode('utf-8')

    @staticmethod
    def _parse_decimal(valor):
        """Converte string/Decimal/float para float."""
        if valor is None:
            return 0.0
        if isinstance(valor, (int, float)):
            return float(valor)
        try:
            return float(str(valor).replace(',', '.').replace('R$', '').strip())
        except (ValueError, TypeError):
            return 0.0

    def _render_template_orcamento_pdf(self, orcamento: dict) -> str:
        """Renderiza um HTML simples para o PDF do orcamento."""
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Orcamento #{orcamento.get('id', '')[:8]}</title></head>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; }}
  .header {{ border-bottom: 2px solid #2B6B3F; padding-bottom: 10px; margin-bottom: 20px; }}
  .section {{ margin-bottom: 20px; }}
  .label {{ font-weight: bold; color: #555; }}
  .value {{ color: #333; }}
  .total {{ font-size: 18px; font-weight: bold; color: #2B6B3F; }}
  .status-{{ orcamento.get('status', '') }} {{ background: #E8A838; color: #fff; padding: 2px 8px; border-radius: 4px; }}
</style>
</head>
<body>
  <div class="header">
    <h1>Precision VRT Solo - Orcamento</h1>
    <p class="value"># {orcamento.get('id', '')}</p>
  </div>
  <div class="section">
    <p><span class="label">Cliente:</span> <span class="value">{orcamento.get('cliente_nome', 'N/A')}</span></p>
    <p><span class="label">Email:</span> <span class="value">{orcamento.get('cliente_email', 'N/A')}</span></p>
  </div>
  <div class="section">
    <p><span class="label">Data Emissao:</span> <span class="value">{orcamento.get('data_emissao', 'N/A')}</span></p>
    <p><span class="label">Status:</span> <span class="value">{orcamento.get('status', 'N/A')}</span></p>
  </div>
  <div class="section">
    <table width="100%" cellpadding="5" cellspacing="0" border="0" style="border-top: 1px solid #ddd; border-bottom: 1px solid #ddd;">
      <tr><td class="label">Valor Bruto:</td><td align="right">R$ {orcamento.get('valor_total_bruto', 0):,.2f}</td></tr>
      <tr><td class="label">Desconto:</td><td align="right">{orcamento.get('desconto_percentual', 0)}%</td></tr>
      <tr><td class="label total">Valor Liquido:</td><td align="right" class="total">R$ {orcamento.get('valor_total_liquido', 0):,.2f}</td></tr>
    </table>
  </div>
</body>
</html>"""

    def _registrar_auditoria(self, tipo_acao: str, modulo: str, usuario_id: str, acao: str, sucesso: bool = True, mensagem: str = None):
        """Registra um evento de auditoria no banco."""
        try:
            from models.auditoria import AuditoriaEvento
            evento = AuditoriaEvento(
                tipo_acao=tipo_acao,
                modulo=modulo,
                usuario_id=usuario_id or 0,
                usuario_nome="admin",
                acao=acao,
                sucesso=sucesso,
                mensagem=mensagem,
            )
            self.db.add(evento)
            self.db.flush()
        except Exception:
            pass  # Audit logging is best-effort
