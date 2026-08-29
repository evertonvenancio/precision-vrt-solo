"""Configurações da Central de Comunicação (WhatsApp/E-mail).

Carrega variáveis de ambiente usadas pelos serviços de envio de
mensagens via WhatsApp Business API (Meta Cloud API) e SMTP.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WhatsAppConfig:
    """Credenciais da WhatsApp Business Cloud API (Meta).

    Attributes:
        api_url: Endpoint base da Graph API.
        phone_number_id: ID do número remetente cadastrado na Meta.
        access_token: Token permanente/temporário do app Meta.
        api_version: Versão da Graph API (ex.: ``v20.0``).
        timeout: Timeout (s) das requisições HTTP.
    """

    api_url: str
    phone_number_id: str
    access_token: str
    api_version: str = "v20.0"
    timeout: int = 30

    @property
    def messages_endpoint(self) -> str:
        """URL completa para envio de mensagens."""
        return f"{self.api_url}/{self.api_version}/{self.phone_number_id}/messages"

    @property
    def media_endpoint(self) -> str:
        """URL completa para upload de mídia (PDFs, imagens)."""
        return f"{self.api_url}/{self.api_version}/{self.phone_number_id}/media"


@dataclass(frozen=True)
class EmailConfig:
    """Credenciais SMTP para envio de e-mails.

    Attributes:
        host: Host do servidor SMTP.
        port: Porta SMTP (587 TLS, 465 SSL).
        username: Usuário de autenticação.
        password: Senha/app password.
        use_tls: Se ``True`` usa STARTTLS.
        use_ssl: Se ``True`` usa SMTPS (SSL direto).
        from_email: Endereço remetente exibido.
        from_name: Nome exibido do remetente.
        timeout: Timeout (s) da conexão SMTP.
    """

    host: str
    port: int
    username: str
    password: str
    from_email: str
    from_name: str = "Precision VRT"
    use_tls: bool = True
    use_ssl: bool = False
    timeout: int = 30


def _require(name: str) -> str:
    """Lê variável de ambiente obrigatória."""
    value = os.getenv(name, "").strip()
    if not value:
        logger.warning("Variável de ambiente ausente: %s", name)
    return value


@lru_cache(maxsize=1)
def get_whatsapp_config() -> WhatsAppConfig:
    """Retorna instância cacheada de :class:`WhatsAppConfig`."""
    return WhatsAppConfig(
        api_url=os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com"),
        phone_number_id=_require("WHATSAPP_PHONE_NUMBER_ID"),
        access_token=_require("WHATSAPP_ACCESS_TOKEN"),
        api_version=os.getenv("WHATSAPP_API_VERSION", "v20.0"),
        timeout=int(os.getenv("WHATSAPP_TIMEOUT", "30")),
    )


@lru_cache(maxsize=1)
def get_email_config() -> EmailConfig:
    """Retorna instância cacheada de :class:`EmailConfig`."""
    return EmailConfig(
        host=_require("SMTP_HOST"),
        port=int(os.getenv("SMTP_PORT", "587")),
        username=_require("SMTP_USERNAME"),
        password=_require("SMTP_PASSWORD"),
        from_email=_require("SMTP_FROM_EMAIL"),
        from_name=os.getenv("SMTP_FROM_NAME", "Precision VRT"),
        use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        use_ssl=os.getenv("SMTP_USE_SSL", "false").lower() == "true",
        timeout=int(os.getenv("SMTP_TIMEOUT", "30")),
    )


# Template padrão de mensagem de aniversário.
MENSAGEM_ANIVERSARIO_PADRAO: str = (
    "🎉 Feliz aniversário, {nome}! 🎂\n\n"
    "Toda a equipe da Precision VRT deseja um dia incrível "
    "e um ano repleto de conquistas. Conte sempre conosco!"
)
