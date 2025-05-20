import streamlit as st
import json
import os

def render_manual_input():
    st.sidebar.markdown("### Tool Selection")
    selected_tool = st.sidebar.radio(
        "Choose a tool",
        ["Google Ads Transparency", "Naver Search Ads"],
        key="tool_selection"
    )

    if selected_tool == "Google Ads Transparency":
        st.sidebar.markdown("#### Manual Parameters")
        with st.sidebar.form(key="manual_input_form"):
            # Load available countries
            country_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "country_codes.json"))
            with open(country_path) as f:
                code_map = json.load(f)
                countries = sorted(code_map.values())

            advertiser_id = st.text_input("Advertiser ID (comma-separated)", key="advertiser_id")
            text = st.text_input("Text Search", key="text")
            region = st.selectbox("Region", [""] + countries, index=0, key="region")
            platform = st.selectbox("Platform", ["", "PLAY", "MAPS", "SEARCH", "SHOPPING", "YOUTUBE"], key="platform")
            start_date = st.text_input("Start Date (YYYYMMDD)", key="start_date")
            end_date = st.text_input("End Date (YYYYMMDD)", key="end_date")
            creative_format = st.selectbox("Creative Format", ["", "text", "image", "video"], key="creative_format")
            num = st.number_input("Number of Results", min_value=1, max_value=100, value=10, key="num")

            submitted = st.form_submit_button("Send to Assistant")
            if submitted:
                st.session_state["manual_input"] = {
                    "advertiser_id": advertiser_id,
                    "text": text,
                    "region": region,
                    "platform": platform,
                    "start_date": start_date,
                    "end_date": end_date,
                    "creative_format": creative_format,
                    "num": num,
                }
                st.session_state["manual_trigger"] = True
                st.session_state["manual_tool"] = "google"

    elif selected_tool == "Naver Search Ads":
        st.sidebar.markdown("#### Naver Ads Parameters")
        with st.sidebar.form(key="naver_input_form"):
            query = st.text_input("Query (required)", key="naver_query")
            page = st.number_input("Page (starts from 1)", min_value=1, value=1, key="naver_page")
            where = st.selectbox("Search Type", ["nexearch", "web", "news", "image", "video"], key="naver_where")

            # Only show num if user selects image (API supports `num` only for images)
            if where == "image":
                num = st.number_input("Number of Results (only for images)", min_value=1, max_value=100, value=50, key="naver_num")
            else:
                num = None

            submitted = st.form_submit_button("Send to Assistant")
            if submitted:
                # Calculate start if needed (optional logic)
                if where == "web":
                    start = (page * 15) - 29
                else:
                    start = (page * 10) - 9

                payload = {
                    "query": query,
                    "page": page,
                    "start": start,
                    "where": where
                }
                if num:
                    payload["num"] = num

                st.session_state["manual_input"] = payload
                st.session_state["manual_trigger"] = True
                st.session_state["manual_tool"] = "naver"
