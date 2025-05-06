from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import os
import requests
import json


class AdSearchParams(BaseModel):
    advertiser_id: Optional[str] = Field(default=None, description="Advertiser ID or domain")
    text: Optional[str] = Field(default=None, description="Search text or brand name")
    region: Optional[str] = Field(default=None, description="Region code (e.g., US, KR)")
    political_ads: Optional[bool] = Field(default=False, description="Only political ads?")
    creative_format: Optional[str] = Field(default=None, description="Ad format (text, image, video)")
    start_date: Optional[str] = Field(default=None, description="Start date (YYYYMMDD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYYMMDD)")
    platform: Optional[str] = Field(default=None, description="Platform (YOUTUBE, PLAY, MAPS, SEARCH, SHOPPING)")


class SerpAPIAdsTool(BaseTool):
    name: str = "search_ads_transparency"
    description: str = (
        "Use this tool to fetch ads from the Google Ads Transparency Center using SerpAPI. "
        "Accepts a JSON string with fields like advertiser_id or text, and optional fields like region, "
        "platform, political_ads, start_date, end_date, and creative_format."
    )
    args_schema: Optional[Type[BaseModel]] = None  # Accepts raw JSON string

    def _run(self, tool_input: str) -> str:
        try:
            params_dict = json.loads(tool_input)
        except json.JSONDecodeError:
            return "Invalid input: could not parse JSON string."

        if not params_dict.get("advertiser_id") and not params_dict.get("text"):
            return "Error: Either advertiser_id or text must be provided."

        params = {
            "engine": "google_ads_transparency_center",
            "api_key": os.getenv("SERPAPI_API_KEY"),
            **{k: v for k, v in params_dict.items() if v is not None}
        }

        response = requests.get("https://serpapi.com/search.json", params=params)
        if response.status_code != 200:
            return f"SerpAPI error: {response.text}"

        ads = response.json().get("ad_creatives", [])[:5]
        if not ads:
            return "No ads found."

        return "\n\n".join([
            f"{ad.get('advertiser', 'Unknown')} - {ad.get('format')} - {ad.get('details_link')}"
            for ad in ads
        ])

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")
