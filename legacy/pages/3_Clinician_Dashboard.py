import streamlit as st
from utils.ui import load_css

st.set_page_config(page_title="Clinician Dashboard | Cogniscan", page_icon="🧠", layout="wide")
load_css()

if not st.session_state.get("logged_in") or st.session_state.get("role") != "clinician":
    st.error("Access denied. Please log in as a clinician.")
    st.stop()

st.title("Clinician Dashboard")
st.caption("Upload an MRI scan, run AI analysis, and send patient-friendly results.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='cogniscan-card'>", unsafe_allow_html=True)
    st.subheader("Upload MRI Scan")
    uploaded = st.file_uploader("Upload MRI image (PNG/JPG)", type=["png", "jpg", "jpeg"])
    run_btn = st.button("Run Analysis")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='cogniscan-card'>", unsafe_allow_html=True)
    st.subheader("Results (Clinician View)")
    st.info("Model results will appear here (class + probabilities).")

    st.subheader("Doctor’s Note")
    note = st.text_area("Write a patient-friendly note")
    send_btn = st.button("Send Results to Patient")
    st.markdown("</div>", unsafe_allow_html=True)