from pydantic import BaseModel, Field
from typing import Optional

class AdSearchParams(BaseModel):
    advertiser_id: Optional[str] = Field(None, description="Google Advertiser ID (e.g. AR123456789)")
    text: Optional[str] = Field(None, description="Search term or domain (e.g. apple.com)")
    region: Optional[str] = Field(None, description="Region code (e.g. US, KR, 2840)")
    political_ads: Optional[bool] = Field(False, description="Whether to only include political ads")
    creative_format: Optional[str] = Field(None, description="Format of ad: text, image, video")
    start_date: Optional[str] = Field(None, description="Start date (YYYYMMDD)")
    end_date: Optional[str] = Field(None, description="End date (YYYYMMDD)")
    platform: Optional[str] = Field(None, description="Platform: PLAY, MAPS, SEARCH, SHOPPING, YOUTUBE")
