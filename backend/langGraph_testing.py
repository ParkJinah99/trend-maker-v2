import streamlit as st
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langchain.tools import Tool
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from typing import Annotated, Optional
from pydantic import BaseModel, Field, model_validator
from dotenv import load_dotenv
import uuid, os, requests, json

from langchain_openai import ChatOpenAI
from langchain.tools import tool

# --- Environment Setup ---
os.environ["LANGCHAIN_API_KEY"] = "your_langsmith_api_key"
os.environ["LANGCHAIN_PROJECT"] = "AdSearchAssistant"
load_dotenv()

# --- Load Region Mapping ---
with open("google-ads-transparency-center-regions.json") as f:
    REGION_MAP = json.load(f)
    COUNTRY_TO_CODE = {v: k for k, v in REGION_MAP.items()}

# --- Tool Schema ---
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

    def to_api_params(self):
        params = self.model_dump(exclude_none=True, by_alias=True)
        if "region" in params:
            params["region"] = COUNTRY_TO_CODE.get(params["region"], params["region"])
        if "async_" in params:
            params["async"] = params.pop("async_")
        return params

# --- Tool Function ---
@tool
def serpapi_ad_search(params: GoogleAdTransparencyParameters) -> str:
    """
    Perform a Google Ads Transparency Center search using SerpAPI with the provided parameters.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    base_url = "https://serpapi.com/search"

    query_params = {
        "api_key": api_key,
        "engine": "google_ads_transparency_center",
        **params.to_api_params()
    }

    response = requests.get(base_url, params=query_params)
    if response.status_code != 200:
        return f"SerpAPI error: {response.status_code} - {response.text}"

    data = response.json()
    ads = data.get("ad_creatives", [])
    if not ads:
        return "No ads found."

    formatted_ads = []
    for i, ad in enumerate(ads[:5], 1):
        formatted_ads.append(
            f"**Ad #{i}**\n"
            f"- Title: {ad.get('title', 'No title')}\n"
            f"- Advertiser: {ad.get('advertiser_name', 'Unknown')}\n"
            f"- Region: {ad.get('region', 'N/A')}\n"
            f"- Platform: {ad.get('platform', 'N/A')}\n"
            f"- Run Date: {ad.get('run_date', 'N/A')}"
        )

    return "\n\n".join(formatted_ads)

# --- LLM Setup ---
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
2. Validate values (e.g., correct date format, valid platform values).
3. Once all necessary fields are collected, summarize them as a JSON object using the correct parameter names.
4. End with this exact message: 
   > "Shall I proceed to search with these parameters?"

Only call the tool after the user replies "yes".

If the user wants to update parameters, allow that before calling the tool.
"""

# --- Node Functions ---
def collect_user_input_node(state):
    messages = [SystemMessage(content=chat_agent_template)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def execute_tool_call_node(state):
    ai_msg = state["messages"][-1]
    tool_call = ai_msg.tool_calls[0]
    return {"messages": [AIMessage(content="Preparing parameters for formatting.", tool_calls=[tool_call])]}  # Fixed: added content

def format_api_params_node(state):
    tool_call = state["messages"][-1].tool_calls[0]
    raw_params = tool_call["args"]

    # Convert region name to code
    if "region" in raw_params:
        region_name = raw_params["region"]
        region_code = COUNTRY_TO_CODE.get(region_name)
        if not region_code:
            return {"messages": [
                AIMessage(content=f"Invalid region name: {region_name}. Please provide a valid country.")
            ]}
        raw_params["region"] = region_code

    if "async_" in raw_params:
        raw_params["async"] = raw_params.pop("async_")

    formatted = {k: v for k, v in raw_params.items() if v is not None}

    return {"messages": [
        AIMessage(content="Formatted parameters.", tool_calls=[{
            "name": "serpapi_ad_search",
            "args": formatted,
            "id": tool_call["id"]
        }])
    ]}

def confirm_tool_execution_node(state):
    return {"messages": [
        AIMessage(content="Shall I proceed to search with these parameters? Please say 'yes' to confirm or 'no' to update.")
    ]}

def finalize_tool_run_node(state):
    tool_call = state["messages"][-1].tool_calls[0]
    tool_input = GoogleAdTransparencyParameters.model_validate(tool_call["args"])
    tool_output = serpapi_ad_search.invoke({"params": tool_input})  # Pass wrapped for @tool

    return {
        "messages": [
            ToolMessage(content=tool_output, tool_call_id=tool_call["id"])
        ]
    }

# --- Graph State Definition ---
class State(TypedDict):
    messages: Annotated[list, add_messages]

def get_next_state(state):
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "execute_tool_call"
    elif isinstance(last, HumanMessage) and last.content.strip().lower() == "yes":
        return "finalize_tool_run"
    elif isinstance(last, HumanMessage):
        return "collect_user_input"
    return END

# --- LangGraph Build ---
memory = MemorySaver()
workflow = StateGraph(State)
workflow.add_node("collect_user_input", collect_user_input_node)
workflow.add_node("execute_tool_call", execute_tool_call_node)
workflow.add_node("format_api_params", format_api_params_node)
workflow.add_node("confirm_tool_execution", confirm_tool_execution_node)
workflow.add_node("finalize_tool_run", finalize_tool_run_node)

workflow.add_edge(START, "collect_user_input")
workflow.add_conditional_edges("collect_user_input", get_next_state, ["execute_tool_call", "collect_user_input", END])
workflow.add_edge("execute_tool_call", "format_api_params")
workflow.add_edge("format_api_params", "confirm_tool_execution")
workflow.add_conditional_edges("confirm_tool_execution", get_next_state, ["finalize_tool_run", "collect_user_input", END])
workflow.add_edge("finalize_tool_run", END)

graph = workflow.compile(checkpointer=memory)

# --- Streamlit UI ---
st.title("Ad Search Assistant (LangGraph + SerpAPI)")

if "history" not in st.session_state:
    st.session_state["history"] = []
    st.session_state["config"] = {"configurable": {"thread_id": str(uuid.uuid4())}}

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state["history"].append(HumanMessage(content=user_input))
    for step in graph.stream({"messages": st.session_state["history"]}, config=st.session_state["config"], stream_mode="updates"):
        last_msg = next(iter(step.values()))["messages"][-1]
        st.session_state["history"].append(last_msg)

# Display chat history
for msg in st.session_state["history"]:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, (AIMessage, ToolMessage)):
        with st.chat_message("assistant"):
            st.markdown(msg.content)
