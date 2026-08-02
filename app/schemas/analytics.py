from pydantic import BaseModel


class GrowthStatsResponse(BaseModel):
    channel_id: int
    total_joined: int
    total_left: int
    net_growth: int
    churn_rate: float


class SevenDayGrowthResponse(BaseModel):
    channel_id: int
    total_joined_7d: int
    total_left_7d: int
    net_growth_7d: int
    churn_rate_7d: float


class InviteLinkGrowthItem(BaseModel):
    invite_link_id: int | None
    invite_link: str | None = None
    name: str | None = None
    source: str | None = None
    campaign: str | None = None
    total_joined: int
    total_left: int
    net_growth: int
    churn_rate: float


class AnalyticsSummaryResponse(BaseModel):
    growth: GrowthStatsResponse
    seven_day_growth: SevenDayGrowthResponse
    growth_by_invite_link: list[InviteLinkGrowthItem]
