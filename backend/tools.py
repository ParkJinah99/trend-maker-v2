# bakcend/tools.py
import os, requests
from dotenv import load_dotenv
from langchain.tools import tool
from schemas import GoogleAdTransparencyParameters, NaverAdSearchParameters
import json

load_dotenv()
@tool
def serpapi_ad_search(params: GoogleAdTransparencyParameters) -> str:
    """
    Perform a Google Ads Transparency Center search using SerpAPI with the provided parameters and return the results.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    base_url = "https://serpapi.com/search"

    with open("country_codes.json") as f:
        COUNTRY_TO_CODE = {v: k for k, v in json.load(f).items()}
    query_params = {
        "api_key": api_key,
        "engine": "google_ads_transparency_center",
        **params.to_api_params(COUNTRY_TO_CODE)
    }

    response = requests.get(base_url, params=query_params)
    if response.status_code != 200:
        return f"SerpAPI error: {response.status_code} - {response.text}"

    ads = response.json().get("ad_creatives", [])
    if not ads:
        return "No ads found."

    return "\n\n".join(
        f"**Ad #{i+1}**\n- Title: {ad.get('title', 'No title')}\n"
        f"- Advertiser: {ad.get('advertiser_name', 'Unknown')}\n"
        f"- Region: {ad.get('region', 'N/A')}\n"
        f"- Platform: {ad.get('platform', 'N/A')}\n"
        f"- Run Date: {ad.get('run_date', 'N/A')}"
        for i, ad in enumerate(ads[:5])
    )


@tool
def serpapi_naver_ad_search(params: NaverAdSearchParameters) -> str:
    """
    Perform a Naver ad search using SerpAPI and return the top ad results.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    base_url = "https://serpapi.com/search"

    query_params = {
        "api_key": api_key,
        **params.to_api_params()
    }

    response = requests.get(base_url, params=query_params)
    if response.status_code != 200:
        return f"Naver API error: {response.status_code} - {response.text}"

    ads = response.json().get("ads_results", [])
    if not ads:
        return "No Naver ads found."

    return "\n\n".join(
        f"**{ad.get('title', '')}**\n- {ad.get('description', '')}\n- Site: {ad.get('site', '')}\n- Link: {ad.get('link', '')}"
        for ad in ads[:5]
    )
