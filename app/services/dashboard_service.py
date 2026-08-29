"""
Precision VRT Solo - Serviço do Módulo Dashboard
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func, text

from core.seguranca.permissions import get_permissoes


class DashboardService:
    """
    Serviço central do módulo Dashboard.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session, user_data: dict = None):
        self.db = db
        self.user_data = user_data or {}

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db, self.user_data)

    def get_dados(self) -> dict:
        """Busca os dados do dashboard."""
        return {
            # --- Usuário logado ---
            "nome_usuario": self._get_nome_usuario(),
            "saudacao": self._get_saudacao(),
            "data_atual": self._get_data_atual(),
            "hora_atual": self._get_hora_atual(),
            "aniversariantes": self._get_aniversariantes(),
            "pendencias_usuario": self._get_pendencias_usuario(),

            # --- 2. Clientes ---
            "total_clientes": self._get_total_clientes(),
            "total_fazendas": self._get_total_fazendas(),
            "area_total_cadastrada": self._get_area_total_cadastrada(),

            # --- 3. Operação ---
            "processamentos_realizados": self._get_processamentos_realizados(),
            "prescricoes_geradas": self._get_prescricoes_geradas(),
            "pdfs_emitidos": self._get_pdfs_emitidos(),

            # --- 4. Módulos Técnicos ---
            "modulos_tecnicos": {
                "fertilidade": {"nome": "Fertilidade", "operacoes": 0},
                "compactacao": {"nome": "Compactação", "operacoes": 0},
                "satelite": {"nome": "Índices de Satélite", "operacoes": 0},
                "nematoides": {"nome": "Nematoides", "operacoes": 0},
            },

            # --- 5. Comercial ---
            "orcamentos": self._get_orcamentos(),
            "vendas": self._get_vendas(),

            # --- 6. Oportunidades ---
            "oportunidades": [],

            # --- 7. Avisos ---
            "notificacoes": [],
            "lembretes": [],

            # --- 8. Clima ---
            "clima": self._get_clima(),
        }

    # ------------------------------------------------------------------
    # Usuário logado
    # ------------------------------------------------------------------

    def _get_nome_usuario(self) -> str | None:
        try:
            # Obter nome do usuário autenticado
            return self.user_data.get('nome') or self.user_data.get('username') or 'Usuário'
        except Exception:
            return None

    def _get_saudacao(self) -> str:
        hora = datetime.now().hour
        if 5 <= hora < 12:
            return "Bom dia"
        elif 12 <= hora < 18:
            return "Boa tarde"
        else:
            return "Boa noite"

    def _get_data_atual(self) -> str:
        return datetime.now().strftime("%d/%m/%Y")

    def _get_hora_atual(self) -> str:
        return datetime.now().strftime("%H:%M")

    def _get_pendencias_usuario(self) -> int:
        try:
            # Se existir tabela de tarefas/pendências no futuro
            from models.tarefa import Tarefa
            return self.db.query(Tarefa).filter(Tarefa.status == "pendente").count()
        except Exception:
            return 0

    # ------------------------------------------------------------------
    # Consultas reais com fallback seguro
    # ------------------------------------------------------------------


    def _get_clima(self) -> dict | None:
        try:
            from db.database import SessionLocal
            db_local = SessionLocal()
            try:
                result = db_local.execute(
                    text("SELECT valor FROM configuracoes WHERE chave = 'cidade_padrao' LIMIT 1")
                )
                row = result.fetchone()
                cidade = row[0] if row and row[0] else None
                if not cidade:
                    return None
                return self._consultar_clima(cidade)
            finally:
                db_local.close()
        except Exception:
            return None

    def _consultar_clima(self, cidade: str) -> dict | None:
        try:
            import urllib.request
            import urllib.parse
            import json
            url = (
                "https://wttr.in/" + urllib.parse.quote(cidade)
                + "?format=%C|%t|%T|%m|%M&lang=pt"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw = resp.read().decode("utf-8").strip()
            parts = raw.split("|")
            if len(parts) >= 2:
                return {
                    "cidade": cidade,
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "condicao": parts[0].strip(),
                    "temp_min": parts[2].strip() if len(parts) > 2 else "—",
                    "temp_max": parts[1].strip() if len(parts) > 1 else "—",
                }
            return None
        except Exception:
            return None

    def _get_total_clientes(self) -> int:
        try:
            from models.cliente_sql import Cliente
            from db.database import SessionLocal
            db_local = SessionLocal()
            try:
                count = db_local.query(Cliente).filter(Cliente.ativo == True).count()
                return count
            finally:
                db_local.close()
        except Exception as e:
            print(f"Erro ao buscar clientes: {e}")
            return 0

    def _get_total_fazendas(self) -> int:
        try:
            from db.database import SessionLocal
            db_local = SessionLocal()
            try:
                result = db_local.execute(text('SELECT COUNT(*) FROM fazendas'))
                count = result.fetchone()[0]
                return count
            finally:
                db_local.close()
        except Exception as e:
            print(f"Erro ao buscar fazendas: {e}")
            return 0

    def _get_area_total_cadastrada(self) -> float:
        try:
            from db.database import SessionLocal
            db_local = SessionLocal()
            try:
                result = db_local.execute(text('SELECT COALESCE(SUM(hectares_total), 0) FROM fazendas'))
                total = result.fetchone()[0]
                return float(total) if total is not None else 0
            finally:
                db_local.close()
        except Exception as e:
            print(f"Erro ao buscar área total: {e}")
            return 0

    def _get_processamentos_realizados(self) -> int:
        try:
            from db.database import SessionLocal
            db_local = SessionLocal()
            try:
                # Usar tabela de clientes como indicador de processamento
                result = db_local.execute(text('SELECT COUNT(*) FROM clientes WHERE ativo = 1'))
                count = result.fetchone()[0]
                return count
            finally:
                db_local.close()
        except Exception as e:
            print(f"Erro ao buscar processamentos: {e}")
            return 0

    def _get_prescricoes_geradas(self) -> int:
        try:
            from db.database import SessionLocal
            db_local = SessionLocal()
            try:
                # Usar tabela de prescrições reais
                result = db_local.execute(text('SELECT COUNT(*) FROM prescricao'))
                count = result.fetchone()[0]
                return count
            finally:
                db_local.close()
        except Exception as e:
            print(f"Erro ao buscar prescrições: {e}")
            return 0

    def _get_pdfs_emitidos(self) -> int:
        try:
            from db.database import SessionLocal
            db_local = SessionLocal()
            try:
                # Usar tabela de orçamentos como indicador de PDFs
                result = db_local.execute(text('SELECT COUNT(*) FROM orcamentos WHERE status = "emitido"'))
                count = result.fetchone()[0]
                return count
            finally:
                db_local.close()
        except Exception as e:
            print(f"Erro ao buscar laudos: {e}")
            return 0

    def _get_orcamentos(self) -> int:
        try:
            from models.orcamento import Orcamento
            from db.database import SessionLocal
            db_local = SessionLocal()
            try:
                count = db_local.query(Orcamento).count()
                return count
            finally:
                db_local.close()
        except Exception as e:
            print(f"Erro ao buscar orçamentos: {e}")
            return 0

    def _get_vendas(self) -> int:
        try:
            from db.database import SessionLocal
            db_local = SessionLocal()
            try:
                # Usar orçamentos aprovados como indicador de vendas
                result = db_local.execute(text('SELECT COUNT(*) FROM orcamentos WHERE status = "aprovado"'))
                count = result.fetchone()[0]
                return count
            finally:
                db_local.close()
        except Exception as e:
            print(f"Erro ao buscar vendas: {e}")
            return 0

    def _get_aniversariantes(self) -> list:
        try:
            from db.database import SessionLocal
            db_local = SessionLocal()
            try:
                from datetime import datetime
                hoje = datetime.now()
                mes, dia = hoje.month, hoje.day
                result = db_local.execute(text(
                    "SELECT nome FROM clientes WHERE ativo = 1 "
                    "AND data_nascimento IS NOT NULL "
                    "AND strftime('%m-%d', data_nascimento) = ?"
                ), (f"{dia:02d}-{mes:02d}",))
                aniversariantes = [{"nome": row[0]} for row in result.fetchall()]
                return aniversariantes
            finally:
                db_local.close()
        except Exception as e:
            print(f"Erro ao buscar aniversariantes: {e}")
            return []
