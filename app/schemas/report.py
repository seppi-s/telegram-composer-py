from pydantic import BaseModel


class TopInviteLinkReportItem(BaseModel):
    invite_link_id: int | None
    name: str | None = None
    source: str | None = None
    campaign: str | None = None
    invite_link: str | None = None
    joined: int
    left: int
    net_growth: int
    churn_rate: float


class DailyReportResponse(BaseModel):
    channel_id: int
    title: str | None = None

    joined_today: int
    left_today: int
    net_growth_today: int
    churn_rate_today: float

    joined_7d: int
    left_7d: int
    net_growth_7d: int
    churn_rate_7d: float

    top_invite_links: list[TopInviteLinkReportItem]
    text_report: str
