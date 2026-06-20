from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class ClickResponse(BaseModel):
    url_id: int
    short_code: str
    clicked_at: datetime

class AnalyticsBreakdown(BaseModel):
    daily: Dict[str, int] = Field(default_factory=dict)
    weekly: Dict[str, int] = Field(default_factory=dict)
    monthly: Dict[str, int] = Field(default_factory=dict)

class AnalyticsSummary(BaseModel):
    total_clicks: int
    short_code: str
    original_url: str

class URLStats(BaseModel):
    short_code: str
    total_clicks: int
    recent_clicks: List[ClickResponse]
    breakdown: AnalyticsBreakdown