# backend/states.py
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from typing_extensions import TypedDict, Annotated
from agents import get_llm_with_prompt
from schemas import GoogleAdTransparencyParameters
from tools import serpapi_ad_search
import json
import uuid
import streamlit as st

def init_session_state():
    if "history" not in st.session_state:
        st.session_state["history"] = []
        st.session_state["config"] = {"configurable": {"thread_id": str(uuid.uuid4())}}
        st.session_state["tool_selection"] = "Google Ads Transparency"
        st.session_state["manual_input"] = {}
        st.session_state["manual_trigger"] = False
        st.session_state["manual_status"] = ""

with open("country_codes.json") as f:
    COUNTRY_TO_CODE = {v: k for k, v in json.load(f).items()}

class State(TypedDict):
    messages: Annotated[list, add_messages]
    tool_call: dict

def collect_user_input_node(state):
    if st.session_state.get("manual_trigger"):
        manual_data = st.session_state.get("manual_input", {})
        st.session_state["manual_trigger"] = False

        if "region" in manual_data and manual_data["region"] in COUNTRY_TO_CODE:
            manual_data["region"] = COUNTRY_TO_CODE[manual_data["region"]]

        tool_call = {
            "name": "serpapi_ad_search",
            "args": manual_data,
            "id": str(uuid.uuid4())
        }
        return {"tool_call": tool_call}

    messages, llm = get_llm_with_prompt(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}

def execute_tool_call_node(state):
    ai_msg = state["messages"][-1]
    return {"messages": [AIMessage(content="Preparing parameters for formatting.", tool_calls=ai_msg.tool_calls)]}

def format_api_params_node(state):
    if "tool_call" in state:
        return {"tool_call": state["tool_call"]}

    tool_call = state["messages"][-1].tool_calls[0]
    raw_params = tool_call["args"]

    if "region" in raw_params:
        region = raw_params["region"]
        code = COUNTRY_TO_CODE.get(region)
        if not code:
            return {"messages": [AIMessage(content=f"Invalid region name: {region}. Please provide a valid country.")]}
        raw_params["region"] = code

    return {
        "tool_call": {"name": tool_call["name"], "args": raw_params, "id": tool_call["id"]}
    }

def finalize_tool_run_node(state):
    tool_call = state["tool_call"]
    params = GoogleAdTransparencyParameters.model_validate(tool_call["args"])
    result = serpapi_ad_search.invoke({"params": params})
    return {
        "messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]
    }

def get_next_state(state):
    if "tool_call" in state:
        return "format_api_params"
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "execute_tool_call"
    if isinstance(last, HumanMessage):
        return "collect_user_input"
    return END

memory = MemorySaver()
workflow = StateGraph(State)
workflow.add_node("collect_user_input", collect_user_input_node)
workflow.add_node("execute_tool_call", execute_tool_call_node)
workflow.add_node("format_api_params", format_api_params_node)
workflow.add_node("finalize_tool_run", finalize_tool_run_node)

workflow.add_edge(START, "collect_user_input")
workflow.add_conditional_edges("collect_user_input", get_next_state, ["execute_tool_call", "format_api_params", "collect_user_input", END])
workflow.add_edge("execute_tool_call", "format_api_params")
workflow.add_edge("format_api_params", "finalize_tool_run")
workflow.add_edge("finalize_tool_run", END)

graph = workflow.compile(checkpointer=memory)

if st.session_state.get("manual_trigger"):
    with st.spinner("Processing manual input..."):
        try:
            for step in graph.stream(
                {"messages": st.session_state["history"]},
                config=st.session_state["config"],
                stream_mode="updates"
            ):
                step_data = next(iter(step.values()))
                if "messages" in step_data:
                    st.session_state["history"].extend(step_data["messages"])
            st.session_state["manual_status"] = "✅ Successfully executed manual input."
        except Exception as e:
            st.session_state["manual_status"] = f"❌ Error: {str(e)}"
