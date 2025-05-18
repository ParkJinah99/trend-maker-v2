# backend/st_ui.py
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from states import graph

def init_session_state():
    import uuid
    if "history" not in st.session_state:
        st.session_state["history"] = []
        st.session_state["config"] = {"configurable": {"thread_id": str(uuid.uuid4())}}

def handle_user_input(user_input):
    st.session_state["history"].append(HumanMessage(content=user_input))

    with st.spinner("Processing..."):
        for step in graph.stream(
            {"messages": st.session_state["history"]},
            config=st.session_state["config"],
            stream_mode="updates"
        ):
            step_data = next(iter(step.values()))

            # Optional debug display
            with st.expander("Debug Step", expanded=False):
                st.json(step_data)

            if "messages" in step_data:
                st.session_state["history"].extend(step_data["messages"])


def display_chat_history():
    for msg in st.session_state["history"]:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)