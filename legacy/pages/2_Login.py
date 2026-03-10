import streamlit as st
from utils.ui import load_css

st.set_page_config(page_title="Login | Cogniscan", page_icon="🧠", layout="centered")
load_css()

st.markdown("<div class='auth-circle-top'></div>", unsafe_allow_html=True)
st.markdown("<div class='auth-circle-bottom'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="auth-page">
  <div class="auth-card">
    <div class="auth-card-top">
      <h1>Welcome Back</h1>
      <p>Access your MRI analysis dashboard</p>
    </div>
    <div class="auth-card-body">
""", unsafe_allow_html=True)

role = st.radio(
    "Login as",
    ["Clinician", "Patient"],
    horizontal=True,
    label_visibility="collapsed"
)

page_heading = "Clinician Login" if role == "Clinician" else "Patient Login"
helper = "Enter your credentials to continue." if role == "Clinician" else "Enter your patient credentials to continue."

st.markdown(f"""
<div style="text-align:center; margin: 0.7rem 0 1rem 0;">
  <div style="font-weight:700; font-size:1.05rem;">{page_heading}</div>
  <div style="font-size:0.82rem; color:#888;">{helper}</div>
</div>
<div class="section-label">Email or ID</div>
""", unsafe_allow_html=True)

email = st.text_input("Email or ID", placeholder="Enter your ID or email", label_visibility="collapsed")

st.markdown("""<div class="section-label">Password</div>""", unsafe_allow_html=True)
password = st.text_input("Password", placeholder="••••••••", type="password", label_visibility="collapsed")

submitted = st.button("Login")

if submitted:
    st.session_state["logged_in"] = True
    st.session_state["role"] = role.lower()
    st.session_state["email"] = email
    st.success("Logged in successfully.")

    if st.session_state["role"] == "clinician":
        st.switch_page("pages/3_Clinician_Dashboard.py")
    else:
        st.switch_page("pages/4_Patient_Portal.py")

st.markdown("""
      <div class="secondary-link">Don’t have an account? <span>Create Account</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)