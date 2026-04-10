import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from lib.session import is_logged_in, login, logout, get_user

st.set_page_config(
    page_title="TWD Sales Assistant",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
    .twd-logo { font-family: sans-serif; font-weight: 900; font-size: 22px; color: #00ADEF; letter-spacing: -0.5px; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
    .badge-fid { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
    .badge-contractor { background: #fff7ed; color: #ea580c; border: 1px solid #fed7aa; }
    .badge-hubspot { background: #e0f5fe; color: #00ADEF; border: 1px solid #bae6fd; }
    .badge-main { background: #e0f5fe; color: #00ADEF; border: 1px solid #bae6fd; }
    .badge-removed { background: #fff5f5; color: #E31F26; border: 1px solid #fecaca; }
</style>
""", unsafe_allow_html=True)

if not is_logged_in():
    st.markdown('<div class="twd-logo">TWD</div>', unsafe_allow_html=True)
    st.title("Sales Assistant")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.subheader("Sign in")
        email    = st.text_input("Email", placeholder="you@twd.nl")
        password = st.text_input("Password", type="password")
        if st.button("Sign in", use_container_width=True, type="primary"):
            ok, err = login(email, password)
            if ok:
                st.rerun()
            else:
                st.error(f"Login failed: {err}")
else:
    user = get_user()
    with st.sidebar:
        st.markdown('<div class="twd-logo">TWD</div>', unsafe_allow_html=True)
        st.markdown(f"**{user['email']}**")
        st.markdown("---")
        st.page_link("pages/1_Priority_List.py", label="Priority List", icon="📊")
        st.page_link("pages/2_Favorites.py",     label="Favorites",      icon="⭐")
        st.page_link("pages/3_Settings.py",      label="Settings",       icon="⚙️")
        st.markdown("---")
        if st.button("Sign out", use_container_width=True):
            logout()
            st.rerun()

    st.switch_page("pages/1_Priority_List.py")
