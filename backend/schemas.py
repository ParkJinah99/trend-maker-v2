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
