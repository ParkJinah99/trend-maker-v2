import streamlit as st
import json
import os


def _load_aux(filename: str):
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, filename)) as f:
        return json.load(f)


def render_manual_input():
    st.sidebar.markdown("### Tool Selection")
    selected_tool = st.sidebar.radio(
        "Choose a tool",
        [
            "Google Ads Transparency",
            "Google Ad Results",
            "YouTube Ads",
            "Naver Ads",
        ],
        key="tool_selection",
    )

    # ─────────────────── Google Ads Transparency Center ────────────────────
    if selected_tool == "Google Ads Transparency":
        st.sidebar.markdown("#### Transparency Parameters")
        with st.sidebar.form(key="transparency_form"):
            with open(os.path.join(os.path.dirname(__file__), "country_codes.json")) as f:
                countries = sorted(json.load(f).values())

            advertiser_id = st.text_input("Advertiser ID (comma‑separated)")
            text = st.text_input("Text Search")
            region = st.selectbox("Region", [""] + countries)
            platform = st.selectbox("Platform", ["", "PLAY", "MAPS", "SEARCH", "SHOPPING", "YOUTUBE"])
            start_date = st.text_input("Start Date (YYYYMMDD)")
            end_date = st.text_input("End Date (YYYYMMDD)")
            creative_format = st.selectbox("Creative Format", ["", "text", "image", "video"])
            num = st.number_input("Number of Results", 1, 100, 10)

            if st.form_submit_button("Send to Assistant"):
                st.session_state.update(
                    manual_input={k: v for k, v in {
                        "advertiser_id": advertiser_id,
                        "text": text,
                        "region": region,
                        "platform": platform,
                        "start_date": start_date,
                        "end_date": end_date,
                        "creative_format": creative_format,
                        "num": num,
                    }.items() if v},
                    manual_trigger=True,
                )

    # ───────────────────── Google Ad Results (Sponsored) ─────────────────────
    elif selected_tool == "Google Ad Results":
        st.sidebar.markdown("#### Google Ad Results Parameters")
        with st.sidebar.form(key="google_ads_form"):
            country_data = _load_aux("google-countries.json")
            lang_data = _load_aux("google-languages.json")

            q = st.text_input("Keywords (required)")

            country_name = st.selectbox("Country (for gl)", [""] + [c["country_name"] for c in country_data])
            lang_name = st.selectbox("Language (hl)", [""] + [l["language_name"] for l in lang_data])
            device = st.selectbox("Device", ["", "desktop", "mobile", "tablet"])
            num = st.number_input("Num Results", 1, 100, 10)

            if st.form_submit_button("Send to Assistant"):
                lang_code = next((l["language_code"] for l in lang_data if l["language_name"] == lang_name), None)
                gl_code = next((c["country_code"] for c in country_data if c["country_name"] == country_name), None)

                payload = {k: v for k, v in {
                    "q": q,
                    "hl": lang_code or None,
                    "gl": gl_code or None,
                    "device": device or None,
                    "num": num,
                }.items() if v}
                st.session_state.update(manual_input=payload, manual_trigger=True)

    # ───────────────────────── YouTube Ads Results ──────────────────────────
    elif selected_tool == "YouTube Ads":
        st.sidebar.markdown("#### YouTube Ads Parameters")
        with st.sidebar.form(key="youtube_ads_form"):
            country_data = _load_aux("google-countries.json")
            lang_data = _load_aux("google-languages.json")

            q = st.text_input("Keywords (required)")
            country_name = st.selectbox("Country (gl)", [""] + [c["country_name"] for c in country_data])
            lang_name = st.selectbox("Language (hl)", [""] + [l["language_name"] for l in lang_data])
            num = st.number_input("Num Results", 1, 100, 20)

            if st.form_submit_button("Send to Assistant"):
                lang_code = next((l["language_code"] for l in lang_data if l["language_name"] == lang_name), None)
                gl_code = next((c["country_code"] for c in country_data if c["country_name"] == country_name), None)

                payload = {k: v for k, v in {
                    "q": q,
                    "hl": lang_code or None,
                    "gl": gl_code or None,
                    "num": num,
                }.items() if v}
                st.session_state.update(manual_input=payload, manual_trigger=True)

    # ───────────────────────────── Naver Ads ────────────────────────────────
    else:
        st.sidebar.markdown("#### Naver Ads Parameters")
        with st.sidebar.form(key="naver_form"):
            query = st.text_input("Query (required)")
            page = st.number_input("Page", 1, None, 1)
            where = st.selectbox("Search Type", ["nexearch", "web", "news", "image", "video"])
            num = st.number_input("Num Results (image only)", 1, 100, 50, disabled=where != "image")

            if st.form_submit_button("Send to Assistant"):
                start = (page * (15 if where == "web" else 10)) - (29 if where == "web" else 9)
                payload = {"query": query, "page": page, "start": start, "where": where}
                if where == "image":
                    payload["num"] = num
                st.session_state.update(manual_input=payload, manual_trigger=True)
