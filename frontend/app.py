import requests
import streamlit as st
import base64
import re

st.markdown("""
    <style>
        /* Remove top padding */
        .block-container {
            padding-top: 0rem;
        }

        /* Hide the main menu, footer, and deploy button area */
        header[data-testid="stHeader"] {
            display: none !important;
        }

        div[data-testid="stToolbar"] {
            display: none !important;
        }

        [data-testid="stDecoration"] {
            display: none !important;
        }

        footer {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Email Summarizer — Daily Digest")

if "digest_data" not in st.session_state:
    st.session_state.digest_data = None
if "summary_clean" not in st.session_state:
    st.session_state.summary_clean = ""

if st.button("Fetch Digest"):
    with st.spinner("Generating summary..."):
        r = requests.get("http://localhost:8009/daily-digest")
        if r.ok:
            st.session_state.digest_data = r.json()
            st.session_state.summary_clean = re.sub(r"\[.*?\]", "", st.session_state.digest_data["summary"])
        else:
            st.error("Failed to fetch digest. Is backend running?")

data = st.session_state.digest_data

if data:
    st.subheader("AI Summary")
    st.write(st.session_state.summary_clean)
    print(st.session_state.summary_clean)

    if st.button("Speak Summary"):
        with st.spinner("Generating voice..."):
            r_audio = requests.post("http://localhost:8009/synthesize", json={"text": data["summary"], "history_prompt":"v2/en_speaker_9"})
            if r_audio.ok:
                audio_base64 = base64.b64encode(r_audio.content).decode()
                audio_html = f"""
                                <audio autoplay>
                                    <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                                </audio>
                            """
                st.markdown(audio_html, unsafe_allow_html=True)
            else:
                st.error("Failed to generate audio.")

    st.subheader("Emails")
    for e in data["emails"]:
        st.markdown(f"**{e['subject']}** — _{e['from']}_")
        st.write(e["snippet"])
