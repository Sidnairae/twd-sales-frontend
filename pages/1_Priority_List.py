import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from lib.session import is_logged_in, logout, get_user
from lib import api

st.set_page_config(page_title="Priority List — TWD", layout="wide")

if not is_logged_in():
    st.switch_page("app.py")

# ── Sidebar ───────────────────────────────────────────────────────────────────
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

st.title("📊 Priority List")

# Load data
@st.cache_data(ttl=60, show_spinner="Loading priorities…")
def load(_token):
    return api.get_projects()

data = load(st.session_state.get("access_token"))
scores = data.get("scores", [])
last_sync = data.get("last_sync")

if last_sync:
    st.caption(f"Last sync: {last_sync[:19].replace('T', ' ')}")

if not scores:
    st.info("No data yet. Go to Settings to import your Excel files, then run Sync.")
    st.stop()

# ── Filters ───────────────────────────────────────────────────────────────────
all_categories = sorted({s["projects"]["sector"] for s in scores if s.get("projects")})
all_regions    = sorted({s["projects"].get("world_region") for s in scores if s.get("projects") and s["projects"].get("world_region")})
all_stages     = sorted({s["projects"].get("stage_normalized") for s in scores if s.get("projects") and s["projects"].get("stage_normalized")})

CATEGORY_LABELS = {
    "1": "Pier & Berth", "2": "Breakwater", "3": "Dolphin & Mooring",
    "4": "Diffuser & Outfall", "5": "Caisson", "7": "Tunnel, Lock & Dyke",
    "9": "Terminal", "10": "Loading Facilities", "12": "Bridge", "13": "Heavy Lift",
}

with st.expander("🔽 Filters", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        cat_filter = st.multiselect("Category", options=all_categories,
                                    format_func=lambda x: CATEGORY_LABELS.get(x, x))
    with col2:
        region_filter = st.multiselect("Region", options=all_regions)
    with col3:
        stage_filter = st.multiselect("Stage", options=all_stages)

    col4, col5, col6, col7 = st.columns(4)
    with col4: fid_only          = st.checkbox("FID ✓ only")
    with col5: contractor_sel    = st.checkbox("Contractor selected")
    with col6: contractor_known  = st.checkbox("Contractor known")
    with col7: hubspot_ready     = st.checkbox("🏆 HubSpot Ready only")

search = st.text_input("🔍 Search projects, companies…", placeholder="Search…")

# ── Filter logic ──────────────────────────────────────────────────────────────
def is_hubspot_ready(row) -> bool:
    if not row.get("is_favorite"):           return False
    main = next((c for c in (row.get("contacts") or []) if c.get("is_main_contact")), None)
    if not main:                             return False
    return main.get("outreach_sentiment") == "positive"

filtered = []
for row in scores:
    p = row.get("projects") or {}
    if cat_filter and p.get("sector") not in cat_filter: continue
    if region_filter and p.get("world_region") not in region_filter: continue
    if stage_filter and p.get("stage_normalized") not in stage_filter: continue
    if fid_only and not p.get("fid_detected"): continue
    if contractor_sel and not p.get("contractor_detected"): continue
    if contractor_known and not p.get("contractor_name"): continue
    if hubspot_ready and not is_hubspot_ready(row): continue
    if search:
        q = search.lower()
        if not any(q in str(p.get(f, "")).lower() for f in ["name", "company_name", "country"]):
            continue
    filtered.append(row)

st.caption(f"Showing {len(filtered)} of {len(scores)} projects")

# ── Project rows ──────────────────────────────────────────────────────────────
for idx, row in enumerate(filtered):
    p = row.get("projects") or {}
    score = row.get("score", 0)
    rank  = idx + 1
    contacts = row.get("contacts") or []
    breakdown = row.get("breakdown") or {}
    fav = row.get("is_favorite", False)
    hubspot = is_hubspot_ready(row)

    # Header line
    star     = "★" if fav else "☆"
    fid_tag  = " 🟢FID" if p.get("fid_detected") else ""
    con_tag  = f" 🟠{p.get('contractor_name') or 'Contractor sel.'}" if p.get("contractor_detected") else ""
    hs_tag   = " 🏆HubSpot Ready" if hubspot else ""
    header   = f"#{rank} · **{p.get('name', 'Unknown')}** {star}{fid_tag}{con_tag}{hs_tag}"
    subhead  = f"{p.get('company_name','')} · {p.get('country','')} · {p.get('world_region','')} · Score: **{score:.0f}** · {p.get('stage_normalized','')}"

    with st.expander(header, expanded=False):
        st.caption(subhead)

        col_left, col_right = st.columns(2)

        with col_left:
            val = p.get("project_value_usd")
            st.markdown(f"**Value:** ${val/1e6:.1f}M" if val else "**Value:** —")
            st.markdown(f"**Execution:** {p.get('execution_date') or '—'}")
            st.markdown(f"**Status:** {p.get('status') or '—'}")
            if p.get("project_url"):
                st.markdown(f"[View on GlobalData →]({p['project_url']})")

            st.markdown("**Score Breakdown**")
            for label, key, max_val in [
                ("Past work", "past_work", 25),
                ("Execution urgency", "execution_date", 25),
                ("Project value", "project_value", 20),
                ("Project phase", "project_phase", 20),
                ("Relationship", "relationship", 10),
            ]:
                val_s = breakdown.get(key, 0)
                st.markdown(f"{label}: **{val_s:.1f}** / {max_val}")
                st.progress(val_s / max_val)

            # Description
            if p.get("description"):
                with st.spinner("Summarising…"):
                    try:
                        summary = api.summarize(p["description"])
                        st.info(summary)
                    except Exception:
                        with st.expander("Full description"):
                            st.write(p["description"])

        with col_right:
            # Actions
            btn1, btn2, btn3, btn4 = st.columns(4)
            with btn1:
                fav_label = "★ Unfav" if fav else "☆ Fav"
                if st.button(fav_label, key=f"fav_{row['id']}"):
                    api.toggle_favorite(p["id"], p.get("globaldata_id",""), p.get("name",""), p.get("company_name",""))
                    st.cache_data.clear()
                    st.rerun()
            with btn2:
                if st.button("📋 Prep", key=f"prep_{row['id']}"):
                    st.session_state[f"show_prep_{row['id']}"] = True
            with btn3:
                if st.button("🔍 Research", key=f"res_{row['id']}"):
                    st.session_state[f"show_research_{row['id']}"] = True
            with btn4:
                if st.button("🔄 Sync", key=f"sync_{row['id']}"):
                    with st.spinner("Syncing…"):
                        result = api.sync_scores()
                    st.success(f"Synced {result.get('synced',0)} projects")
                    st.cache_data.clear()
                    st.rerun()

            # Meeting prep card
            if st.session_state.get(f"show_prep_{row['id']}"):
                with st.spinner("Generating prep card…"):
                    try:
                        card = api.meeting_prep(p["id"])
                        st.markdown("---")
                        st.markdown("**📋 Meeting Prep Card**")
                        st.markdown(card)
                    except Exception as e:
                        st.error(str(e))

            # Research card
            if st.session_state.get(f"show_research_{row['id']}"):
                with st.spinner("Researching…"):
                    try:
                        res = api.research(p["id"])
                        st.markdown("---")
                        st.markdown("**🔍 Research**" + (" *(cached)*" if res.get("cached") else ""))
                        st.markdown(res.get("research_card",""))
                    except Exception as e:
                        st.error(str(e))

            # Contacts
            st.markdown("**Key Contacts**")
            contractor_contacts = [c for c in contacts if c.get("is_contractor_contact")]
            other_contacts      = [c for c in contacts if not c.get("is_contractor_contact")]
            sorted_contacts     = contractor_contacts + other_contacts

            if not sorted_contacts:
                st.caption("No contacts yet.")
            else:
                for c in sorted_contacts:
                    tags = []
                    if c.get("is_main_contact"):       tags.append("⭐ MAIN")
                    if c.get("is_contractor_contact"): tags.append("🏗 CONTRACTOR")
                    sentiment = c.get("outreach_sentiment", "neutral")
                    sent_icon = {"positive": "✅", "negative": "❌", "neutral": "➖"}.get(sentiment, "➖")

                    with st.container(border=True):
                        st.markdown(f"**{c.get('name','')}** {' '.join(tags)}")
                        st.caption(c.get("title",""))
                        if c.get("email"):    st.markdown(f"✉ {c['email']}")
                        if c.get("linkedin_url"): st.markdown(f"[LinkedIn]({c['linkedin_url']})")

                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if st.button("⭐ Main", key=f"main_{c['id']}"):
                                api.update_contact(c["id"], {"is_main_contact": True})
                                st.cache_data.clear(); st.rerun()
                        with c2:
                            new_sent = st.selectbox(
                                "Outreach",
                                ["neutral", "positive", "negative"],
                                index=["neutral","positive","negative"].index(sentiment),
                                key=f"sent_{c['id']}",
                                label_visibility="collapsed",
                            )
                            if new_sent != sentiment:
                                api.update_contact(c["id"], {"outreach_sentiment": new_sent})
                                st.cache_data.clear(); st.rerun()
                        with c3:
                            if st.button("🏗 Contractor", key=f"con_{c['id']}"):
                                api.update_contact(c["id"], {"is_contractor_contact": not c.get("is_contractor_contact", False)})
                                st.cache_data.clear(); st.rerun()

                        notes = st.text_area("Notes", value=c.get("outreach_notes",""), key=f"notes_{c['id']}", height=60, label_visibility="collapsed", placeholder="Add notes…")
                        if notes != (c.get("outreach_notes") or ""):
                            if st.button("Save notes", key=f"save_notes_{c['id']}"):
                                api.update_contact(c["id"], {"outreach_notes": notes})
                                st.cache_data.clear(); st.rerun()
