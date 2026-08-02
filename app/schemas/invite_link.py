from pydantic import BaseModel


class CreateInviteLinkRequest(BaseModel):
    name: str
    source: str | None = None
    campaign: str | None = None


class InviteLinkResponse(BaseModel):
    id: int
    channel_id: int
    invite_link: str
    name: str | None = None
    source: str | None = None
    campaign: str | None = None
