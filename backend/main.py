# backend/main.py
import streamlit as st
from st_ui import handle_user_input, display_chat_history
from states import init_session_state, graph
from manual_ui import render_manual_input
from langchain_core.messages import HumanMessage

st.set_page_config(layout="wide")
st.title("Ad Search Assistant (LangGraph + SerpAPI)")

st.session_state["HumanMessage"] = HumanMessage  # fallback for manual_ui
init_session_state()

col1, col2 = st.columns([1, 2])

with col1:
    render_manual_input()
    if st.session_state.get("manual_status"):
        st.sidebar.markdown(st.session_state["manual_status"])

with col2:
    user_input = st.chat_input("Type your message...")
    if user_input:
        handle_user_input(user_input)

    # If manual input was triggered, add it as a HumanMessage for tracking
    if st.session_state.get("manual_trigger"):
        manual_input = st.session_state.get("manual_input", {})
        param_summary = "\n".join(f"{k}: {v}" for k, v in manual_input.items() if v)
        summary_message = f"Manual input submitted:\n{param_summary}"
        st.session_state["history"].append(HumanMessage(content=summary_message))
        handle_user_input("")  # trigger graph

    display_chat_history()
