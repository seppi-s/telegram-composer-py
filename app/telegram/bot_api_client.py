import httpx

from app.config import settings


class TelegramBotApiClient:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{settings.bot_token}"

    async def create_chat_invite_link(
        self,
        telegram_chat_id: int,
        name: str,
    ) -> dict:
        url = f"{self.base_url}/createChatInviteLink"

        payload = {
            "chat_id": telegram_chat_id,
            "name": name,
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, json=payload)
            data = response.json()

        if not data.get("ok"):
            raise RuntimeError(f"Telegram createChatInviteLink failed: {data}")

        return data["result"]
