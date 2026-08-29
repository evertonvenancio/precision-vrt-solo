"""Service layer da Central de Comunicação.

Responsável por:
    * Enviar mensagens via WhatsApp Business Cloud API (Meta).
    * Enviar e-mails via SMTP com anexos.
    * Identificar aniversariantes do dia e disparar felicitações,
      garantindo deduplicação por log.
"""

from __future__ import annotations

import logging
import mimetypes
import smtplib
import ssl
from dataclasses import dataclass
from datetime import date, datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from config.comunicacao_config import (  # type: ignore[import-not-found]
    MENSAGEM_ANIVERSARIO_PADRAO,
    EmailConfig,
    WhatsAppConfig,
    get_email_config,
    get_whatsapp_config,
)
from models.comunicacao import (  # type: ignore[import-not-found]
    CanalEnvio,
    LogEnvio,
    StatusEnvio,
    TipoDocumento,
)

logger = logging.getLogger(__name__)


@dataclass
class ResultadoEnvio:
    """Resultado normalizado de um envio."""

    sucesso: bool
    detalhe: str
    resposta: dict[str, Any] | None = None


class ComunicacaoService:
    """Encapsula envio de WhatsApp/E-mail e rotinas de aniversário."""

    def __init__(
        self,
        db: Session,
        whatsapp_config: WhatsAppConfig | None = None,
        email_config: EmailConfig | None = None,
    ) -> None:
        self.db = db
        self._wa_cfg = whatsapp_config
        self._mail_cfg = email_config

    # ------------------------------------------------------------------ #
    # Configs lazy
    # ------------------------------------------------------------------ #
    @property
    def whatsapp_config(self) -> WhatsAppConfig:
        if self._wa_cfg is None:
            self._wa_cfg = get_whatsapp_config()
        return self._wa_cfg

    @property
    def email_config(self) -> EmailConfig:
        if self._mail_cfg is None:
            self._mail_cfg = get_email_config()
        return self._mail_cfg

    # ------------------------------------------------------------------ #
    # WhatsApp
    # ------------------------------------------------------------------ #
    def enviar_whatsapp(
        self,
        numero_destino: str,
        mensagem: str,
        pdf_path: str | None = None,
        *,
        tipo_documento: TipoDocumento = TipoDocumento.NOTIFICACAO,
        documento_id: int | None = None,
        referencia_id: int | None = None,
    ) -> ResultadoEnvio:
        """Envia mensagem (e opcionalmente PDF) via WhatsApp Cloud API.

        Args:
            numero_destino: Número no formato E.164, sem ``+`` (ex.: ``5511999999999``).
            mensagem: Texto da mensagem.
            pdf_path: Caminho local do PDF a anexar. Se ``None``, envia só texto.
            tipo_documento: Categoria para o log.
            documento_id: ID do documento de origem, se houver.
            referencia_id: ID da pessoa destinatária, se houver.

        Returns:
            :class:`ResultadoEnvio` com status e resposta da API.
        """
        cfg = self.whatsapp_config
        numero = numero_destino.lstrip("+").strip()
        headers = {
            "Authorization": f"Bearer {cfg.access_token}",
            "Content-Type": "application/json",
        }

        resposta: dict[str, Any] | None = None
        resultado: ResultadoEnvio

        try:
            with httpx.Client(timeout=cfg.timeout) as client:
                # 1) Anexa PDF (upload de mídia + envio como documento).
                if pdf_path:
                    media_id = self._upload_whatsapp_media(client, cfg, pdf_path)
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": numero,
                        "type": "document",
                        "document": {
                            "id": media_id,
                            "filename": Path(pdf_path).name,
                            "caption": mensagem,
                        },
                    }
                else:
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": numero,
                        "type": "text",
                        "text": {"body": mensagem, "preview_url": False},
                    }

                response = client.post(
                    cfg.messages_endpoint, headers=headers, json=payload
                )
                resposta = self._safe_json(response)
                response.raise_for_status()

            logger.info("WhatsApp enviado para %s", numero)
            resultado = ResultadoEnvio(True, "Mensagem enviada.", resposta)

        except httpx.HTTPStatusError as exc:
            detalhe = f"HTTP {exc.response.status_code} da Meta API."
            logger.error("Falha WhatsApp para %s: %s | %s", numero, detalhe, resposta)
            resultado = ResultadoEnvio(False, detalhe, resposta)
        except httpx.HTTPError as exc:
            detalhe = f"Erro de conexão com a Meta API: {exc}"
            logger.error("Falha WhatsApp para %s: %s", numero, detalhe)
            resultado = ResultadoEnvio(False, detalhe, resposta)
        except FileNotFoundError:
            detalhe = f"Arquivo não encontrado: {pdf_path}"
            logger.error(detalhe)
            resultado = ResultadoEnvio(False, detalhe)
        except Exception as exc:  # noqa: BLE001
            detalhe = f"Erro inesperado: {exc}"
            logger.exception("Falha WhatsApp para %s", numero)
            resultado = ResultadoEnvio(False, detalhe)

        self._registrar_log(
            canal=CanalEnvio.WHATSAPP,
            destinatario=numero,
            mensagem=mensagem,
            anexo_path=pdf_path,
            resultado=resultado,
            tipo_documento=tipo_documento,
            documento_id=documento_id,
            referencia_id=referencia_id,
        )
        return resultado

    def _upload_whatsapp_media(
        self, client: httpx.Client, cfg: WhatsAppConfig, file_path: str
    ) -> str:
        """Faz upload de mídia e devolve o ``media_id``."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(file_path)

        mime = mimetypes.guess_type(path.name)[0] or "application/pdf"
        with path.open("rb") as fh:
            files = {"file": (path.name, fh, mime)}
            data = {"messaging_product": "whatsapp", "type": mime}
            headers = {"Authorization": f"Bearer {cfg.access_token}"}
            resp = client.post(
                cfg.media_endpoint, headers=headers, data=data, files=files
            )
            resp.raise_for_status()
            return resp.json()["id"]

    # ------------------------------------------------------------------ #
    # E-mail
    # ------------------------------------------------------------------ #
    def enviar_email(
        self,
        destino: str,
        assunto: str,
        corpo: str,
        anexo_path: str | None = None,
        *,
        tipo_documento: TipoDocumento = TipoDocumento.NOTIFICACAO,
        documento_id: int | None = None,
        referencia_id: int | None = None,
        html: bool = False,
    ) -> ResultadoEnvio:
        """Envia e-mail (com anexo opcional) via SMTP.

        Args:
            destino: E-mail do destinatário.
            assunto: Assunto.
            corpo: Texto puro ou HTML (ver ``html``).
            anexo_path: Caminho do arquivo a anexar.
            tipo_documento: Categoria para o log.
            documento_id: ID do documento, se houver.
            referencia_id: ID da pessoa, se houver.
            html: Se ``True``, ``corpo`` é tratado como HTML.

        Returns:
            :class:`ResultadoEnvio` com status.
        """
        cfg = self.email_config
        resultado: ResultadoEnvio

        try:
            msg = EmailMessage()
            msg["Subject"] = assunto
            msg["From"] = f"{cfg.from_name} <{cfg.from_email}>"
            msg["To"] = destino

            if html:
                msg.set_content("Seu cliente de e-mail não suporta HTML.")
                msg.add_alternative(corpo, subtype="html")
            else:
                msg.set_content(corpo)

            if anexo_path:
                path = Path(anexo_path)
                if not path.is_file():
                    raise FileNotFoundError(anexo_path)
                mime, _ = mimetypes.guess_type(path.name)
                maintype, subtype = (
                    mime.split("/", 1) if mime else ("application", "octet-stream")
                )
                with path.open("rb") as fh:
                    msg.add_attachment(
                        fh.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=path.name,
                    )

            if cfg.use_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(
                    cfg.host, cfg.port, timeout=cfg.timeout, context=context
                ) as smtp:
                    smtp.login(cfg.username, cfg.password)
                    smtp.send_message(msg)
            else:
                with smtplib.SMTP(cfg.host, cfg.port, timeout=cfg.timeout) as smtp:
                    smtp.ehlo()
                    if cfg.use_tls:
                        smtp.starttls(context=ssl.create_default_context())
                        smtp.ehlo()
                    smtp.login(cfg.username, cfg.password)
                    smtp.send_message(msg)

            logger.info("E-mail enviado para %s", destino)
            resultado = ResultadoEnvio(True, "E-mail enviado.")

        except FileNotFoundError as exc:
            detalhe = f"Arquivo não encontrado: {exc}"
            logger.error(detalhe)
            resultado = ResultadoEnvio(False, detalhe)
        except (smtplib.SMTPException, OSError) as exc:
            detalhe = f"Falha SMTP: {exc}"
            logger.error("Falha e-mail para %s: %s", destino, detalhe)
            resultado = ResultadoEnvio(False, detalhe)
        except Exception as exc:  # noqa: BLE001
            detalhe = f"Erro inesperado: {exc}"
            logger.exception("Falha e-mail para %s", destino)
            resultado = ResultadoEnvio(False, detalhe)

        self._registrar_log(
            canal=CanalEnvio.EMAIL,
            destinatario=destino,
            mensagem=corpo,
            assunto=assunto,
            anexo_path=anexo_path,
            resultado=resultado,
            tipo_documento=tipo_documento,
            documento_id=documento_id,
            referencia_id=referencia_id,
        )
        return resultado

    # ------------------------------------------------------------------ #
    # Aniversariantes
    # ------------------------------------------------------------------ #
    def verificar_aniversariantes(
        self, hoje: date | None = None
    ) -> list[dict[str, Any]]:
        """Retorna clientes e funcionários que fazem aniversário hoje.

        Args:
            hoje: Data de referência (default: ``date.today()``).

        Returns:
            Lista de dicts: ``{id, nome, tipo, email, telefone}``.
        """
        hoje = hoje or date.today()
        aniversariantes: list[dict[str, Any]] = []

        # Importes locais evitam acoplamento rígido caso os models
        # ainda não existam no momento do import.
        try:
            from models.cliente import Cliente  # type: ignore[import-not-found]

            stmt = select(Cliente).where(
                and_(
                    Cliente.data_nascimento.is_not(None),
                    func.extract("month", Cliente.data_nascimento) == hoje.month,
                    func.extract("day", Cliente.data_nascimento) == hoje.day,
                )
            )
            for c in self.db.execute(stmt).scalars():
                aniversariantes.append(
                    {
                        "id": c.id,
                        "nome": getattr(c, "nome", ""),
                        "tipo": "cliente",
                        "email": getattr(c, "email", None),
                        "telefone": getattr(c, "telefone", None),
                    }
                )
        except ImportError:
            logger.warning("Modelo Cliente indisponível; pulando clientes.")

        try:
            from models.funcionario import Funcionario  # type: ignore[import-not-found]

            stmt = select(Funcionario).where(
                and_(
                    Funcionario.data_nascimento.is_not(None),
                    func.extract("month", Funcionario.data_nascimento) == hoje.month,
                    func.extract("day", Funcionario.data_nascimento) == hoje.day,
                )
            )
            for f in self.db.execute(stmt).scalars():
                aniversariantes.append(
                    {
                        "id": f.id,
                        "nome": getattr(f, "nome", ""),
                        "tipo": "funcionario",
                        "email": getattr(f, "email", None),
                        "telefone": getattr(f, "telefone", None),
                    }
                )
        except ImportError:
            logger.warning("Modelo Funcionario indisponível; pulando funcionários.")

        return aniversariantes

    def disparar_parabens_automatico(
        self, template: str | None = None
    ) -> dict[str, int]:
        """Dispara mensagens de aniversário, evitando duplicidade no dia.

        Args:
            template: Template com placeholder ``{nome}``. Se ``None``,
                usa :data:`MENSAGEM_ANIVERSARIO_PADRAO`.

        Returns:
            Dict com ``{total, enviados, falhas, ja_enviados_hoje}``.
        """
        template = template or MENSAGEM_ANIVERSARIO_PADRAO
        pessoas = self.verificar_aniversariantes()

        total = len(pessoas)
        enviados = 0
        falhas = 0
        ja_enviados = 0

        for pessoa in pessoas:
            destino = pessoa.get("telefone") or pessoa.get("email")
            if not destino:
                logger.info("Aniversariante %s sem contato; ignorado.", pessoa["id"])
                continue

            if self._ja_enviado_hoje_aniversario(pessoa["id"]):
                ja_enviados += 1
                continue

            mensagem = template.format(nome=pessoa.get("nome", ""))

            if pessoa.get("telefone"):
                resultado = self.enviar_whatsapp(
                    numero_destino=pessoa["telefone"],
                    mensagem=mensagem,
                    tipo_documento=TipoDocumento.ANIVERSARIO,
                    referencia_id=pessoa["id"],
                )
            else:
                resultado = self.enviar_email(
                    destino=pessoa["email"],
                    assunto="Feliz aniversário! 🎉",
                    corpo=mensagem,
                    tipo_documento=TipoDocumento.ANIVERSARIO,
                    referencia_id=pessoa["id"],
                )

            if resultado.sucesso:
                enviados += 1
            else:
                falhas += 1

        return {
            "total": total,
            "enviados": enviados,
            "falhas": falhas,
            "ja_enviados_hoje": ja_enviados,
        }

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _ja_enviado_hoje_aniversario(self, referencia_id: int) -> bool:
        """Checa se já há log de aniversário com sucesso hoje p/ a pessoa."""
        inicio = datetime.combine(date.today(), datetime.min.time(), tzinfo=timezone.utc)
        stmt = select(func.count(LogEnvio.id)).where(
            and_(
                LogEnvio.referencia_id == referencia_id,
                LogEnvio.tipo_documento == TipoDocumento.ANIVERSARIO,
                LogEnvio.status == StatusEnvio.SUCESSO,
                LogEnvio.enviado_em >= inicio,
            )
        )
        return (self.db.execute(stmt).scalar_one() or 0) > 0

    def _registrar_log(
        self,
        *,
        canal: CanalEnvio,
        destinatario: str,
        mensagem: str | None,
        resultado: ResultadoEnvio,
        assunto: str | None = None,
        anexo_path: str | None = None,
        tipo_documento: TipoDocumento = TipoDocumento.NOTIFICACAO,
        documento_id: int | None = None,
        referencia_id: int | None = None,
    ) -> LogEnvio:
        """Persiste o resultado do envio em ``logs_envio``."""
        log = LogEnvio(
            canal=canal,
            status=StatusEnvio.SUCESSO if resultado.sucesso else StatusEnvio.ERRO,
            tipo_documento=tipo_documento,
            destinatario=destinatario,
            assunto=assunto,
            mensagem=mensagem,
            anexo_path=anexo_path,
            documento_id=documento_id,
            referencia_id=referencia_id,
            erro=None if resultado.sucesso else resultado.detalhe,
            resposta_api=resultado.resposta,
        )
        try:
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
        except Exception:  # noqa: BLE001
            logger.exception("Falha ao gravar log de envio.")
            self.db.rollback()
        return log

    @staticmethod
    def _safe_json(response: httpx.Response) -> dict[str, Any] | None:
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text}
