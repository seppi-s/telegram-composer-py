from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.models  # noqa: F401
from app.api.reports import router as reports_router
from app.api.bot_reports import router as bot_reports_router
from app.api.invite_links import router as invite_links_router
from app.api.members import router as members_router
from app.config import settings
from app.db.session import get_db
from app.schemas.telegram import TelegramUpdate
from app.telegram.webhook_handler import TelegramWebhookHandler
from app.api.analytics import router as analytics_router
from app.api.post_stats import router as post_stats_router
from app.api.mtproto import router as mtproto_router
app = FastAPI(
    title="Telegram Analytics API",
    description=(
        "Telegram channel/group analytics API with webhook, members, "
        "events, invite link tracking, and membership lifetime analytics."
    ),
    version="0.1.0",
)


app.include_router(invite_links_router)
app.include_router(members_router)
app.include_router(analytics_router)
app.include_router(reports_router)
app.include_router(bot_reports_router)
app.include_router(post_stats_router)
app.include_router(mtproto_router)

@app.get(
    "/healthz",
    tags=["system"],
)
async def healthz():
    return {
        "status": "ok",
        "env": settings.app_env,
    }


@app.post(
    "/webhook/telegram",
    tags=["telegram-webhook"],
)
async def telegram_webhook(
    update: TelegramUpdate,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
    session: AsyncSession = Depends(get_db),
):
    if x_telegram_bot_api_secret_token != settings.webhook_secret:
        raise HTTPException(
            status_code=403,
            detail="Invalid webhook secret",
        )

    handler = TelegramWebhookHandler(session)

    await handler.handle_update(
        update.model_dump(
            by_alias=True,
            exclude_none=True,
        )
    )

    return {
        "ok": True,
    }