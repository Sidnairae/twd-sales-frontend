import streamlit as st
import os
import requests

def _base() -> str:
    try:
        return "".join(str(st.secrets["API_BASE_URL"]).split())
    except Exception:
        return os.environ.get("API_BASE_URL", "http://localhost:8000")

def is_logged_in() -> bool:
    return bool(st.session_state.get("access_token"))

def get_token() -> str | None:
    return st.session_state.get("access_token")

def get_user() -> dict | None:
    return st.session_state.get("user")

def login(email: str, password: str) -> tuple[bool, str]:
    try:
        r = requests.post(f"{_base()}/api/login", json={"email": email, "password": password}, timeout=15)
        r.raise_for_status()
        data = r.json()
        st.session_state["access_token"] = data["access_token"]
        st.session_state["user"] = data["user"]
        return True, ""
    except requests.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return False, detail
    except Exception as e:
        return False, str(e)

def logout():
    st.session_state.clear()
