import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from lib.session import is_logged_in, logout, get_user
from lib import api

st.set_page_config(page_title="Favorites — TWD", layout="wide")
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

st.title("⭐ Favorites")

favs = api.get_favorites()
if not favs:
    st.info("No favorites yet. Star a project from the Priority List.")
    st.stop()

active  = [f for f in favs if f.get("projects")]
removed = [f for f in favs if not f.get("projects")]

st.caption(f"{len(active)} active · {len(removed)} removed")

for fav in active:
    p = fav["projects"]
    val = p.get("project_value_usd")
    header = f"★ **{p.get('name','')}** — {p.get('company_name','')} · {p.get('country','')} · {'$'+f\"{val/1e6:.1f}M\" if val else '—'}"
    with st.expander(header):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Stage:** {p.get('stage_normalized') or '—'}")
            st.markdown(f"**Region:** {p.get('world_region') or '—'}")
            st.markdown(f"**Execution:** {p.get('execution_date') or '—'}")
            if p.get("project_url"):
                st.markdown(f"[View on GlobalData →]({p['project_url']})")
            if p.get("description"):
                with st.spinner("Summarising…"):
                    try:
                        st.info(api.summarize(p["description"]))
                    except Exception:
                        st.write(p["description"][:400])
        with col2:
            if st.button("Remove from favorites", key=f"rem_{fav['id']}"):
                api.toggle_favorite(p["id"], fav["globaldata_id"], fav.get("project_name",""), fav.get("company_name",""))
                st.rerun()
            if st.button("📋 Prep card", key=f"prep_{fav['id']}"):
                with st.spinner("Generating…"):
                    try:
                        st.markdown(api.meeting_prep(p["id"]))
                    except Exception as e:
                        st.error(str(e))
            if st.button("🔍 Research", key=f"res_{fav['id']}"):
                with st.spinner("Researching…"):
                    try:
                        res = api.research(p["id"])
                        st.markdown(res.get("research_card",""))
                    except Exception as e:
                        st.error(str(e))

if removed:
    st.markdown("---")
    st.markdown("### Removed from GlobalData")
    st.caption("These projects no longer appear in your imported data. Kept until you manually remove.")
    for fav in removed:
        col1, col2 = st.columns([4,1])
        with col1:
            st.markdown(f"★ ~~{fav.get('project_name','Unknown')}~~ — {fav.get('company_name','')} 🔴 REMOVED")
        with col2:
            if st.button("Remove", key=f"del_{fav['id']}"):
                api.toggle_favorite("", fav["globaldata_id"], "", "")
                st.rerun()
