from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from typing_extensions import TypedDict, Annotated
from agents import get_llm_with_prompt
from schemas import (
    GoogleAdTransparencyParameters,
    NaverAdSearchParameters,
    GoogleAdSearchParameters,
    YouTubeAdSearchParameters
)
from tools import (
    google_ad_transparency,
    serpapi_naver_ad_search,
    google_ads_search,
    youtube_ads_search
)
import json
import uuid
import streamlit as st

# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------

def _filter_orphan_tool_msgs(msgs: list) -> list:
    """Remove ToolMessages that are not directly preceded by an AIMessage
    containing matching `tool_calls`, preventing OpenAI 400 errors."""
    cleaned = []
    for m in msgs:
        if isinstance(m, ToolMessage):
            if cleaned and isinstance(cleaned[-1], AIMessage) and getattr(cleaned[-1], "tool_calls", None):
                cleaned.append(m)
        else:
            cleaned.append(m)
    return cleaned


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

with open("country_codes.json") as f:
    COUNTRY_TO_CODE = {v: k for k, v in json.load(f).items()}

TOOL_NAME_BY_UI = {
    "Google Ads Transparency": "google_ad_transparency",
    "Google Ad Results": "google_ads_search",
    "Naver Ads": "serpapi_naver_ad_search",
    "YouTube Ads": "youtube_ads_search"
}


# -----------------------------------------------------------------------------
# Typed state
# -----------------------------------------------------------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]
    tool_call: dict | None


# -----------------------------------------------------------------------------
# Node functions
# -----------------------------------------------------------------------------

def collect_user_input_node(state: State):
    """Handle manual‑input shortcut or route conversation to the LLM."""

    # Manual input ----------------------------------------------------------
    if st.session_state.get("manual_trigger"):
        manual_data = st.session_state.pop("manual_input", {})
        st.session_state["manual_trigger"] = False

        tool_name = TOOL_NAME_BY_UI.get(
            st.session_state.get("tool_selection", "Google Ads Transparency"),
            "google_ad_transparency",
        )

        # Region name → code for Google Transparency
        if tool_name == "google_ad_transparency" and manual_data.get("region") in COUNTRY_TO_CODE:
            manual_data["region"] = COUNTRY_TO_CODE[manual_data["region"]]

        return {
            "tool_call": {
                "name": tool_name,
                "args": manual_data,
                "id": str(uuid.uuid4()),
            }
        }

    # Conversational route ---------------------------------------------------
    cleaned_history = _filter_orphan_tool_msgs(state["messages"])
    messages, llm = get_llm_with_prompt(cleaned_history)
    response = llm.invoke(messages)
    return {"messages": [response]}


def execute_tool_call_node(state: State):
    ai_msg = state["messages"][-1]
    return {"messages": [AIMessage(content="Preparing parameters for formatting.", tool_calls=ai_msg.tool_calls)]}


def format_api_params_node(state: State):
    if state.get("tool_call"):
        return {"tool_call": state["tool_call"]}

    tool_call = state["messages"][-1].tool_calls[0]
    raw_params = tool_call["args"].copy()

    if tool_call["name"] == "google_ad_transparency" and "region" in raw_params:
        region = raw_params["region"]
        code = COUNTRY_TO_CODE.get(region)
        if not code:
            return {"messages": [AIMessage(content=f"Invalid region name: {region}. Please provide a valid country.")]}
        raw_params["region"] = code

    return {"tool_call": {**tool_call, "args": raw_params}}


def finalize_tool_run_node(state: State):
    tool_call = state["tool_call"]
    name = tool_call["name"]

    if name == "google_ad_transparency":
        params = GoogleAdTransparencyParameters.model_validate(tool_call["args"])
        result = google_ad_transparency.invoke({"params": params})
    elif name == "google_ads_search":
        params = GoogleAdSearchParameters.model_validate(tool_call["args"])
        result = google_ads_search.invoke({"params": params})
    elif name == "serpapi_naver_ad_search":
        params = NaverAdSearchParameters.model_validate(tool_call["args"])
        result = serpapi_naver_ad_search.invoke({"params": params})
    elif name == "youtube_ads_search":
        # accept either `search_query` or its alias `q`
        args = tool_call["args"].copy()
        if "q" in args and "search_query" not in args:
            args["search_query"] = args.pop("q")
        params = YouTubeAdSearchParameters.model_validate(args)
        result = youtube_ads_search.invoke({"params": params})
    else:
        result = f"Unknown tool: {name}"

    return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}


# -----------------------------------------------------------------------------
# Graph wiring
# -----------------------------------------------------------------------------

memory = MemorySaver()
workflow = StateGraph(State)
workflow.add_node("collect_user_input", collect_user_input_node)
workflow.add_node("execute_tool_call", execute_tool_call_node)
workflow.add_node("format_api_params", format_api_params_node)
workflow.add_node("finalize_tool_run", finalize_tool_run_node)

workflow.add_edge(START, "collect_user_input")
workflow.add_conditional_edges(
    "collect_user_input",
    lambda s: "format_api_params" if s.get("tool_call") else (
        "execute_tool_call" if isinstance(s["messages"][-1], AIMessage) and s["messages"][-1].tool_calls else "collect_user_input"
    ),
    ["execute_tool_call", "format_api_params", "collect_user_input"],
)
workflow.add_edge("execute_tool_call", "format_api_params")
workflow.add_edge("format_api_params", "finalize_tool_run")
workflow.add_edge("finalize_tool_run", END)

graph = workflow.compile(checkpointer=memory)
