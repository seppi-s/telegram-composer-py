from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TelegramUser(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


class ChatMemberStatus(BaseModel):
    user: TelegramUser
    status: str


class Chat(BaseModel):
    id: int
    title: Optional[str] = None
    username: Optional[str] = None
    type: str


class ChatMemberUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chat: Chat
    from_: TelegramUser = Field(alias="from")
    date: int
    old_chat_member: ChatMemberStatus
    new_chat_member: ChatMemberStatus
    invite_link: Optional[dict] = None


class Message(BaseModel):
    message_id: int
    date: int
    chat: Chat
    text: Optional[str] = None


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Message] = None
    channel_post: Optional[Message] = None
    my_chat_member: Optional[ChatMemberUpdate] = None
    chat_member: Optional[ChatMemberUpdate] = None