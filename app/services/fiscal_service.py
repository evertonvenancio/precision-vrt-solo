"""Integração fiscal com PlugNotas / eNotas.

Este serviço NÃO é um software contábil. Ele apenas envia os dados do
orçamento ao provedor parceiro, persiste o protocolo/DANFE e expõe o
resultado para o contador acompanhar.
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from models.fiscal import NotaFiscal, ProvedorFiscal, StatusNota

logger = logging.getLogger(__name__)

URLS_PROVEDOR: dict[ProvedorFiscal, dict[str, str]] = {
    ProvedorFiscal.PLUGNOTAS: {
        "producao": "https://api.plugnotas.com.br",
        "homologacao": "https://api.sandbox.plugnotas.com.br",
    },
    ProvedorFiscal.ENOTAS: {
        "producao": "https://api.enotasgw.com.br/v2",
        "homologacao": "https://api.enotasgw.com.br/v2",
    },
}

TIMEOUT_HTTP = httpx.Timeout(30.0, connect=10.0)


class FiscalError(Exception):
    """Erro genérico da integração fiscal."""


class FiscalService:
    """Geração de pré-notas via API parceira."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------ #
    # API pública                                                         #
    # ------------------------------------------------------------------ #

    def gerar_pre_nota(self, orcamento_id: UUID) -> NotaFiscal:
        """Envia o orçamento para o provedor e persiste o resultado.

        Args:
            orcamento_id: UUID do orçamento a ser faturado.

        Returns:
            Registro :class:`NotaFiscal` atualizado com status, protocolo,
            link da DANFE e mensagem da SEFAZ.

        Raises:
            FiscalError: Configuração ausente, orçamento inválido ou falha
                irrecuperável no provedor.
        """
        orcamento = self._carregar_orcamento(orcamento_id)
        config = self._carregar_config(orcamento.tenant_id)
        payload = self._montar_payload(orcamento, config)

        nota = NotaFiscal(
            tenant_id=orcamento.tenant_id,
            orcamento_id=orcamento_id,
            provedor=config.provedor,
            status=StatusNota.PROCESSANDO,
            valor_total=float(orcamento.valor_total or 0),
            payload_envio=payload,
        )
        self.db.add(nota)
        self.db.flush()

        try:
            resposta = self._enviar_provedor(config, payload)
            self._aplicar_resposta(nota, config.provedor, resposta)
        except httpx.HTTPError as exc:
            logger.exception("Erro HTTP ao emitir nota %s", nota.id)
            nota.status = StatusNota.ERRO
            nota.mensagem_sefaz = f"Falha de comunicação: {exc!s}"
        except FiscalError as exc:
            logger.warning("Erro fiscal ao emitir nota %s: %s", nota.id, exc)
            nota.status = StatusNota.REJEITADA
            nota.mensagem_sefaz = str(exc)

        self.db.commit()
        self.db.refresh(nota)
        return nota

    # ------------------------------------------------------------------ #
    # Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _carregar_orcamento(self, orcamento_id: UUID):
        from models.orcamento import Orcamento  # import local p/ evitar ciclo

        orcamento = self.db.get(Orcamento, orcamento_id)
        if orcamento is None:
            raise FiscalError(f"Orçamento {orcamento_id} não encontrado")
        return orcamento

    def _carregar_config(self, tenant_id: UUID) -> ConfigFiscal:
        from sqlalchemy import select

        config = self.db.execute(
            select(ConfigFiscal).where(ConfigFiscal.tenant_id == tenant_id)
        ).scalar_one_or_none()
        if config is None:
            raise FiscalError("Configuração fiscal não cadastrada para o tenant")
        return config

    def _montar_payload(self, orcamento: Any, config: ConfigFiscal) -> dict:
        """Monta o payload padronizado (PlugNotas v2 / NFS-e).

        A estrutura abaixo é compatível com o endpoint /nfse do PlugNotas.
        Ajustar campos específicos por município conforme necessidade.
        """
        cliente = getattr(orcamento, "cliente", None)
        itens = getattr(orcamento, "itens", []) or []

        servicos = [
            {
                "descricao": getattr(it, "descricao", "Serviço técnico agronômico"),
                "valor": float(getattr(it, "valor_total", 0) or 0),
                "quantidade": float(getattr(it, "quantidade", 1) or 1),
                "codigo": getattr(it, "codigo_servico", "1.01"),
            }
            for it in itens
        ] or [
            {
                "descricao": "Serviço técnico agronômico (orçamento)",
                "valor": float(orcamento.valor_total or 0),
                "quantidade": 1,
                "codigo": "1.01",
            }
        ]

        return {
            "idIntegracao": str(orcamento.id),
            "prestador": {"cpfCnpj": config.cnpj_emitente},
            "tomador": {
                "cpfCnpj": getattr(cliente, "cpf_cnpj", "") if cliente else "",
                "razaoSocial": getattr(cliente, "nome", "") if cliente else "",
                "email": getattr(cliente, "email", None) if cliente else None,
                "endereco": getattr(cliente, "endereco_dict", None) if cliente else None,
            },
            "servico": {
                "valores": {
                    "servico": float(orcamento.valor_total or 0),
                    "deducoes": 0,
                },
                "itens": servicos,
            },
            "ambiente": config.ambiente,
        }

    def _enviar_provedor(self, config: ConfigFiscal, payload: dict) -> dict:
        base = URLS_PROVEDOR[config.provedor][config.ambiente]
        if config.provedor is ProvedorFiscal.PLUGNOTAS:
            url = f"{base}/nfse"
            headers = {
                "x-api-key": config.chave_api,
                "Content-Type": "application/json",
            }
        else:  # eNotas
            url = f"{base}/empresas/{config.cnpj_emitente}/nfes"
            headers = {
                "Authorization": f"Basic {config.chave_api}",
                "Content-Type": "application/json",
            }

        with httpx.Client(timeout=TIMEOUT_HTTP) as client:
            resp = client.post(url, json=payload, headers=headers)
        logger.info(
            "Provedor %s respondeu %s para orcamento=%s",
            config.provedor.value,
            resp.status_code,
            payload.get("idIntegracao"),
        )
        if resp.status_code >= 500:
            resp.raise_for_status()
        try:
            data = resp.json()
        except ValueError as exc:
            raise FiscalError(f"Resposta inválida do provedor: {resp.text[:200]}") from exc
        if resp.status_code >= 400:
            raise FiscalError(
                data.get("message") or data.get("erro") or "Provedor rejeitou a nota"
            )
        return data

    def _aplicar_resposta(
        self,
        nota: NotaFiscal,
        provedor: ProvedorFiscal,
        resposta: dict,
    ) -> None:
        nota.resposta_provedor = resposta
        if provedor is ProvedorFiscal.PLUGNOTAS:
            nota.protocolo = resposta.get("protocolo") or resposta.get("id")
            nota.numero_nota = (
                (resposta.get("nfse") or {}).get("numero")
                or resposta.get("numero")
            )
            nota.link_danfe = resposta.get("linkDownloadPDF") or resposta.get("pdf")
            nota.link_xml = resposta.get("linkDownloadXML") or resposta.get("xml")
            nota.mensagem_sefaz = resposta.get("mensagem") or "Em processamento"
            estado = (resposta.get("situacao") or "").lower()
        else:
            nota.protocolo = resposta.get("nfeId") or resposta.get("id")
            nota.numero_nota = resposta.get("numero")
            nota.link_danfe = resposta.get("linkDownloadPDF")
            nota.link_xml = resposta.get("linkDownloadXML")
            nota.mensagem_sefaz = resposta.get("mensagem")
            estado = (resposta.get("status") or "").lower()

        if estado in {"autorizada", "autorizado", "concluida", "concluído"}:
            nota.status = StatusNota.AUTORIZADA
        elif estado in {"rejeitada", "rejeitado", "negada"}:
            nota.status = StatusNota.REJEITADA
        elif estado in {"cancelada", "cancelado"}:
            nota.status = StatusNota.CANCELADA
        else:
            nota.status = StatusNota.PROCESSANDO
