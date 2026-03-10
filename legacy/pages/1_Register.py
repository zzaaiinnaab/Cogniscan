import streamlit as st
from utils.ui import load_css

st.set_page_config(page_title="Register | Cogniscan", page_icon="🧠", layout="centered")
load_css()

# Background decorations
st.markdown("<div class='auth-circle-top'></div>", unsafe_allow_html=True)
st.markdown("<div class='auth-circle-bottom'></div>", unsafe_allow_html=True)

# Card start
st.markdown("""
<div class="auth-page">
  <div class="auth-card">
    <div class="auth-card-body">
      <h1 class="auth-title">Create Account</h1>
      <p class="auth-subtitle">Choose your role and create your secure Cogniscan account.</p>
      <div class="section-label" style="margin-top: 0.9rem;">Select Role</div>
""", unsafe_allow_html=True)

role = st.radio(
    "Select Role",
    ["Clinician", "Patient"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("""
      <div class="section-label" style="margin-top:0.8rem;">Email</div>
""", unsafe_allow_html=True)

email = st.text_input("Email", placeholder="Enter your email", label_visibility="collapsed")

st.markdown("""
      <div class="section-label">Password</div>
""", unsafe_allow_html=True)

password = st.text_input("Password", placeholder="Create a password", type="password", label_visibility="collapsed")

st.markdown("""
      <div class="section-label">Confirm Password</div>
""", unsafe_allow_html=True)

confirm_password = st.text_input("Confirm Password", placeholder="Repeat your password", type="password", label_visibility="collapsed")

submitted = st.button("Create Account")

if submitted:
    st.success("Registration logic will be connected next.")

st.markdown("""
      <div class="secondary-link">← Back to <span>Login</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)