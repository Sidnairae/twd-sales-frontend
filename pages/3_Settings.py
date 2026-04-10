import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from lib.session import is_logged_in, logout, get_user
from lib import api

st.set_page_config(page_title="Settings — TWD", layout="wide")
if not is_logged_in():
    st.switch_page("app.py")

with st.sidebar:
    st.markdown('<div style="font-weight:900;font-size:22px;color:#00ADEF">TWD</div>', unsafe_allow_html=True)
    st.markdown(f"**{get_user()['email']}**")
    st.markdown("---")
    st.page_link("pages/1_Priority_List.py", label="Priority List", icon="📊")
    st.page_link("pages/2_Favorites.py",     label="Favorites",      icon="⭐")
    st.page_link("pages/3_Settings.py",      label="Settings",       icon="⚙️")
    st.markdown("---")
    if st.button("Sign out"):
        logout(); st.rerun()

st.title("⚙️ Settings")

# ── Import ────────────────────────────────────────────────────────────────────
st.subheader("Import GlobalData Excel files")
st.caption("Export 'Full Profile' from GlobalData saved searches and upload here.")
files = st.file_uploader(
    "Drop Excel files here", type=["xlsx"],
    accept_multiple_files=True, label_visibility="collapsed"
)
if files and st.button("Import", type="primary"):
    with st.spinner(f"Importing {len(files)} file(s)…"):
        try:
            result = api.import_files(files)
            st.success(
                f"✓ Imported {result['imported']} projects · "
                f"{result['sub_projects_removed']} sub-projects removed"
            )
            if result.get("errors"):
                for err in result["errors"]:
                    st.warning(err)
        except Exception as e:
            st.error(str(e))

st.markdown("---")

# ── Sync ──────────────────────────────────────────────────────────────────────
st.subheader("Sync priority scores")
st.caption("Recalculates rankings for all your projects.")
if st.button("Run Sync", type="primary"):
    with st.spinner("Syncing…"):
        try:
            result = api.sync_scores()
            st.success(f"✓ Synced {result.get('synced', 0)} projects for week {result.get('week_start')}")
        except Exception as e:
            st.error(str(e))

st.markdown("---")

# ── Clear data ────────────────────────────────────────────────────────────────
st.subheader("Clear all my data")
st.caption("Removes all your projects, scores, and favorites. Does not affect other users.")
if st.button("Clear all data", type="secondary"):
    st.session_state["confirm_clear"] = True

if st.session_state.get("confirm_clear"):
    st.warning("Are you sure? This cannot be undone.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, clear everything", type="primary"):
            try:
                api.clear_data()
                st.success("All data cleared.")
                st.session_state.pop("confirm_clear", None)
            except Exception as e:
                st.error(str(e))
    with col2:
        if st.button("Cancel"):
            st.session_state.pop("confirm_clear", None)
            st.rerun()
