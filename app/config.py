from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"

    database_url: str
    async_database_url: str

    bot_token: str
    webhook_secret: str
    webhook_url: str

    telegram_api_id: int
    telegram_api_hash: str
    telegram_phone: str

    mtproto_session_name: str = "telegram_analytics_session"
    mtproto_target_channel: str | None = None

    mtproto_proxy_host: str | None = None
    mtproto_proxy_port: int | None = None
    mtproto_proxy_type: str | None = None

    report_channel_id: int | None = None
    report_target_chat_id: int | None = None
    report_target_chat_ids: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()