import streamlit as st
import os
from supabase import create_client

def get_supabase():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])

def is_logged_in() -> bool:
    return bool(st.session_state.get("access_token"))

def get_token() -> str | None:
    return st.session_state.get("access_token")

def get_user() -> dict | None:
    return st.session_state.get("user")

def login(email: str, password: str) -> tuple[bool, str]:
    try:
        sb = get_supabase()
        result = sb.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state["access_token"] = result.session.access_token
        st.session_state["user"] = {"id": result.user.id, "email": result.user.email}
        return True, ""
    except Exception as e:
        return False, str(e)

def logout():
    st.session_state.clear()
