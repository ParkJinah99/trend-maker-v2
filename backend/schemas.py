# backend/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class GoogleAdTransparencyParameters(BaseModel):
    advertiser_id: Optional[str] = Field(None)
    text: Optional[str] = Field(None)
    platform: Optional[str] = Field(None)
    political_ads: Optional[bool] = Field(False)
    region: Optional[str] = Field(None)
    start_date: Optional[str] = Field(None)
    end_date: Optional[str] = Field(None)
    creative_format: Optional[str] = Field(None)
    num: Optional[int] = Field(10)
    next_page_token: Optional[str] = Field(None)
    no_cache: Optional[bool] = Field(None)
    async_: Optional[bool] = Field(None, alias="async")
    zero_trace: Optional[bool] = Field(None)
    output: Optional[str] = Field("json")

    def to_api_params(self, COUNTRY_TO_CODE):
        params = self.model_dump(exclude_none=True, by_alias=True)
        if "region" in params:
            params["region"] = COUNTRY_TO_CODE.get(params["region"], params["region"])
        if "async_" in params:
            params["async"] = params.pop("async_")
        return params


class NaverAdSearchParameters(BaseModel):
    query: str = Field(..., description="Search query for Naver")
    page: Optional[int] = Field(1)
    where: Optional[str] = Field("nexearch")  # could be web, news, image, etc.
    device: Optional[str] = Field("desktop")
    output: Optional[str] = Field("json")
    async_: Optional[bool] = Field(None, alias="async")
    no_cache: Optional[bool] = Field(None)
    zero_trace: Optional[bool] = Field(None)

    def to_api_params(self):
        params = self.model_dump(exclude_none=True, by_alias=True)
        params["engine"] = "naver"
        return params


class GoogleAdSearchParameters(BaseModel):
    q: str = Field(..., description="Search keywords")
    location: Optional[str] = Field(None)
    language: Optional[str] = Field(None)
    device: Optional[str] = Field(None)   # desktop | mobile | tablet
    page: Optional[int] = Field(1)
    num: Optional[int] = Field(10)
    start: Optional[int] = Field(None)
    safe: Optional[str] = Field(None)
    async_: Optional[bool] = Field(None, alias="async")
    no_cache: Optional[bool] = Field(None)
    output: Optional[str] = Field("json")

    def to_api_params(self):
        p = self.model_dump(exclude_none=True, by_alias=True)
        p["engine"] = "google"
        return p

class YouTubeAdSearchParameters(BaseModel):
    search_query: str
    hl: Optional[str] = None
    gl: Optional[str] = None
    num: Optional[int] = 20
    async_: Optional[bool] = Field(None, alias="async")
    no_cache: Optional[bool] = None
    output: Optional[str] = "json"

    def to_api_params(self):
        p = self.model_dump(exclude_none=True, by_alias=True)
        p["engine"] = "youtube"
        return p
