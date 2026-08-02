import socks
from telethon import TelegramClient

from app.config import settings


def create_mtproto_client() -> TelegramClient:
    proxy = None

    if settings.mtproto_proxy_host and settings.mtproto_proxy_port:
        proxy_type = socks.SOCKS5

        if settings.mtproto_proxy_type == "socks4":
            proxy_type = socks.SOCKS4

        proxy = (
            proxy_type,
            settings.mtproto_proxy_host,
            settings.mtproto_proxy_port,
        )

    return TelegramClient(
        settings.mtproto_session_name,
        settings.telegram_api_id,
        settings.telegram_api_hash,
        proxy=proxy,
        connection_retries=5,
        timeout=20,
    )
