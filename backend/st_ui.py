import re
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from states import graph


# ─────────────────────── Session‑state initialisation ────────────────────────

def init_session_state() -> None:
    """Ensure `st.session_state` has the keys we rely on."""
    import uuid

    if "history" not in st.session_state:
        st.session_state["history"] = []
        st.session_state["config"] = {
            "configurable": {"thread_id": str(uuid.uuid4())}
        }
        st.session_state.setdefault("show_debug", False)


# ───────────────────────── LangGraph interaction helpers ──────────────────────

def _stream_graph() -> None:
    """Run LangGraph streaming updates and extend chat history."""
    for step in graph.stream(
        {"messages": st.session_state["history"]},
        config=st.session_state["config"],
        stream_mode="updates",
    ):
        step_data = next(iter(step.values()))
        if st.session_state.get("show_debug"):
            with st.expander("🔧 Debug Step", expanded=False):
                st.json(step_data)
        if "messages" in step_data:
            st.session_state["history"].extend(step_data["messages"])


def handle_user_input(user_input: str | None) -> None:
    """Push a HumanMessage (may be blank), run the graph, and gather replies."""
    st.session_state["history"].append(HumanMessage(content=user_input or ""))
    with st.spinner("🤖 Thinking …"):
        _stream_graph()


# ───────────────────────────── Rendering helpers ──────────────────────────────

# Regex to catch standalone image URLs
_IMG_RGX = re.compile(r"https?:[^\s]+\.(?:png|jpg|jpeg|gif|webp)", re.IGNORECASE)


def _render_message(msg):
    """Render a chat message, displaying images inline when detected."""
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        content = msg.content or ""

        # If the message is a ToolMessage we default to the expander for long text
        if isinstance(msg, ToolMessage):
            with st.expander("📝 Ad Results", expanded=True):
                _render_text_or_images(content)
        else:
            _render_text_or_images(content)


def _render_text_or_images(text: str) -> None:
    """Render markdown text and show any detected image URLs as images."""
    # First, display the markdown (this also renders images if written in markdown)
    st.markdown(text)

    # Additionally, detect bare image URLs and embed them explicitly
    for url in _IMG_RGX.findall(text):
        st.image(url, use_column_width=True)


def display_chat_history() -> None:
    chat_box = st.container()
    with chat_box:
        for msg in st.session_state["history"]:
            _render_message(msg)


# ─────────────────────────────── Page entrypoint ──────────────────────────────

def _maybe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def main() -> None:
    st.set_page_config(page_title="Ad Search Assistant", page_icon="🔍", layout="wide")
    st.title("🔍 Ad Search Assistant")
    init_session_state()

    left, right = st.columns([1, 3])

    with left:
        from manual_ui import render_manual_input
        render_manual_input()
        st.checkbox("Show debug steps", key="show_debug")
        if st.session_state.get("manual_status"):
            st.markdown(st.session_state["manual_status"])

    if st.session_state.get("manual_trigger"):
        manual_data = st.session_state.get("manual_input", {})
        param_summary = "\n".join(f"{k}: {v}" for k, v in manual_data.items() if v)
        summary_msg = f"Manual input submitted:\n{param_summary}"
        handle_user_input(summary_msg)
        _maybe_rerun()

    with right:
        display_chat_history()
        user_input = st.chat_input("Type a query or just say hi…")
        if user_input:
            handle_user_input(user_input)
            _maybe_rerun()


if __name__ == "__main__":
    main()
