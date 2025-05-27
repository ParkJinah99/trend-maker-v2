import os
import json
import requests
from dotenv import load_dotenv
from langchain.tools import tool

from schemas import (
    GoogleAdTransparencyParameters,
    NaverAdSearchParameters,
    GoogleAdSearchParameters,
    YouTubeAdSearchParameters,
)

load_dotenv()

# helper ----------------------------------------------------------------------

def _cap(items, n):
    return items if n is None else items[: n]

# ---------------------------------------------------------------------------- #
# Google Ads Transparency Center                                               #
# ---------------------------------------------------------------------------- #

@tool
def google_ad_transparency(params: GoogleAdTransparencyParameters) -> str:
    """Perform a Google **Ads Transparency Center** search (engine=`google_ads_transparency_center`).

    REQUIRED:
    - `advertiser_id` (comma‑separated advertiser IDs) **OR**
    - `text` — free‑text search phrase

    OPTIONAL:
    - `region` — country name, e.g. "Australia"
    - `platform` — PLAY, MAPS, SEARCH, SHOPPING, YOUTUBE
    - `political_ads` — boolean
    - `start_date` / `end_date` — YYYYMMDD
    - `creative_format` — text, image, or video
    - `num` — max creatives to return (default 10)

    RETURNS: markdown string with one block per creative (title, advertiser,
    region, platform, run date)."""
    api_key = os.getenv("SERPAPI_API_KEY")
    with open("country_codes.json") as f:
        COUNTRY_TO_CODE = {v: k for k, v in json.load(f).items()}

    r = requests.get(
        "https://serpapi.com/search",
        params={
            "api_key": api_key,
            "engine": "google_ads_transparency_center",
            **params.to_api_params(COUNTRY_TO_CODE),
        },
        timeout=30,
    )
    if r.status_code != 200:
        return f"SerpAPI error: {r.status_code} – {r.text}"

    ads = r.json().get("ad_creatives", [])
    limit = params.num or len(ads)
    return "\n\n".join(
        f"Ad {i+1}\nTitle: {a.get('title','N/A')}\nAdvertiser: {a.get('advertiser_name','N/A')}\nRegion: {a.get('region','N/A')}\nPlatform: {a.get('platform','N/A')}\nRun Date: {a.get('run_date','N/A')}"
        for i, a in enumerate(_cap(ads, limit))
    )

# ---------------------------------------------------------------------------- #
# Naver Ads                                                                    #
# ---------------------------------------------------------------------------- #

@tool
def serpapi_naver_ad_search(params: NaverAdSearchParameters) -> str:
    """Perform a Naver ad search (engine=`naver`).

    REQUIRED:
    - `query` — search phrase

    OPTIONAL:
    - `where` — nexearch, web, video, news, image
    - `page` / `start` — pagination controls
    - `device` — desktop, tablet, or mobile
    - `num` — max ads (image vertical only)

    RETURNS: markdown blocks with title, description, site, link for each ad."""
    api_key = os.getenv("SERPAPI_API_KEY")
    r = requests.get(
        "https://serpapi.com/search",
        params={"api_key": api_key, **params.to_api_params()},
        timeout=30,
    )
    if r.status_code != 200:
        return f"SerpAPI error: {r.status_code} – {r.text}"

    ads = r.json().get("ads_results", [])
    limit = getattr(params, "num", None) or len(ads)
    return "\n\n".join(
        f"Ad {i+1}\nTitle: {a.get('title','')}\nDescription: {a.get('description','')}\nSite: {a.get('site','')}\nLink: {a.get('link','')}"
        for i, a in enumerate(_cap(ads, limit))
    )

# ---------------------------------------------------------------------------- #
# Google Sponsored Ads                                                         #
# ---------------------------------------------------------------------------- #

@tool
def google_ads_search(params: GoogleAdSearchParameters) -> str:
    """Perform a Google search‑page sponsored ads query (engine=`google`).

    REQUIRED:
    - `q` — keywords

    OPTIONAL:
    - `hl` — language code
    - `gl` — country code
    - `device` — desktop, mobile, tablet
    - `num` — max ads (default 10)

    RETURNS: markdown list with title, displayed URL, link for each ad."""
    api_key = os.getenv("SERPAPI_API_KEY")
    r = requests.get(
        "https://serpapi.com/search",
        params={"api_key": api_key, **params.to_api_params()},
        timeout=30,
    )
    if r.status_code != 200:
        return f"SerpAPI error: {r.status_code} – {r.text}"

    ads = r.json().get("ads", [])
    limit = params.num or len(ads)
    return "\n\n".join(
        f"Ad {i+1}\nTitle: {a.get('title','N/A')}\nDisplayed URL: {a.get('displayed_link','N/A')}\nLink: {a.get('link','N/A')}"
        for i, a in enumerate(_cap(ads, limit))
    )

# ---------------------------------------------------------------------------- #
# YouTube Ads                                                                  #
# ---------------------------------------------------------------------------- #

@tool
def youtube_ads_search(params: YouTubeAdSearchParameters) -> str:
    """Perform a YouTube ad results search (engine=`youtube`).

    REQUIRED:
    - `search_query` — keywords

    OPTIONAL:
    - `hl`, `gl`, `num`

    RETURNS: markdown list with title, channel, link for each ad."""
    api_key = os.getenv("SERPAPI_API_KEY")
    r = requests.get(
        "https://serpapi.com/search",
        params={"api_key": api_key, **params.to_api_params()},
        timeout=30,
    )
    if r.status_code != 200:
        return f"SerpAPI error: {r.status_code} – {r.text}"

    ads = r.json().get("ads_results", []) or r.json().get("top_ads", [])
    limit = params.num or len(ads)
    return "\n\n".join(
        f"Ad {i+1}\nTitle: {a.get('title','N/A')}\nChannel: {a.get('channel_name','N/A')}\nLink: {a.get('link','N/A')}"
        for i, a in enumerate(_cap(ads, limit))
    )
