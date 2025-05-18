# backend/agents.py
from langchain_openai import ChatOpenAI
from tools import serpapi_ad_search

llm = ChatOpenAI(temperature=0)
tools = [serpapi_ad_search]
llm_with_tools = llm.bind_tools(tools)

chat_agent_template = """
You are a helpful assistant designed to guide a user in forming a structured and well-defined ad search request using the Google Ads Transparency Center via SerpAPI.

Your goal is to collect the following parameters from the user:

REQUIRED:
- `advertiser_id` (a comma-separated list of advertiser IDs) OR
- `text` (a search phrase)

OPTIONAL:
- `region` (country name, e.g., "Australia")
- `platform` (one of: PLAY, MAPS, SEARCH, SHOPPING, YOUTUBE)
- `political_ads` (true/false)
- `start_date` (format: YYYYMMDD)
- `end_date` (format: YYYYMMDD)
- `creative_format` (text/image/video)
- `num` (maximum number of results, default is 10)

---

INSTRUCTIONS:
1. Ask the user for any missing required fields.
2. Always begin your response by summarizing the parameters collected so far in JSON format.
3. Validate values (e.g., correct date format, valid platform values).
4. List the remaining optional fields available and ask if the user wants to include any of them.
5. Once all necessary fields are collected, summarize them again as a JSON object using the correct parameter names.
6. End with this exact message:
   > "Shall I proceed to search with these parameters?"

Only call the tool after the user replies "yes".

If the user wants to update parameters, allow that before calling the tool.
"""


def get_llm_with_prompt(messages):
    from langchain_core.messages import SystemMessage
    return [SystemMessage(content=chat_agent_template)] + messages, llm_with_tools
