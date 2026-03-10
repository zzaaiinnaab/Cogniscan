import streamlit as st
import streamlit.components.v1 as components


APP_URL = "http://localhost:8000"


st.set_page_config(
    page_title="Cogniscan",
    page_icon="🧠",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Match Flask background and hide Streamlit chrome */
    .stApp {
      background: #f6f3f5;
    }
    header[data-testid="stHeader"], footer {
      visibility: hidden;
      height: 0;
    }

    .launcher-container {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }
    .iframe-wrapper {
      width: 430px;
      max-width: 100%;
      box-shadow: 0 18px 45px rgba(0,0,0,0.10);
      border-radius: 22px;
      overflow: hidden;
      background: #f6f3f5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="launcher-container">
      <div class="iframe-wrapper">
    """,
    unsafe_allow_html=True,
)
components.iframe(APP_URL, height=800, scrolling=True)
st.markdown("</div></div>", unsafe_allow_html=True)

