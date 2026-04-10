import os
import requests
import streamlit as st
from lib.session import get_token

def _base() -> str:
    return os.environ.get("API_BASE_URL", "http://localhost:8000")

def _headers() -> dict:
    return {"Authorization": f"Bearer {get_token()}"}

def get_projects() -> dict:
    r = requests.get(f"{_base()}/api/projects", headers=_headers())
    r.raise_for_status()
    return r.json()

def sync_scores() -> dict:
    r = requests.post(f"{_base()}/api/sync", headers=_headers())
    r.raise_for_status()
    return r.json()

def import_files(files: list) -> dict:
    file_tuples = [("files", (f.name, f.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")) for f in files]
    r = requests.post(f"{_base()}/api/import", headers=_headers(), files=file_tuples)
    r.raise_for_status()
    return r.json()

def clear_data() -> dict:
    r = requests.delete(f"{_base()}/api/clear", headers=_headers())
    r.raise_for_status()
    return r.json()

def summarize(description: str) -> str:
    r = requests.post(f"{_base()}/api/summarize", headers=_headers(), json={"description": description})
    r.raise_for_status()
    return r.json()["summary"]

def meeting_prep(project_id: str) -> str:
    r = requests.post(f"{_base()}/api/meeting-prep/{project_id}", headers=_headers())
    r.raise_for_status()
    return r.json()["prep_card"]

def research(project_id: str) -> dict:
    r = requests.post(f"{_base()}/api/research", headers=_headers(), json={"project_id": project_id})
    r.raise_for_status()
    return r.json()

def get_favorites() -> list:
    r = requests.get(f"{_base()}/api/favorites", headers=_headers())
    r.raise_for_status()
    return r.json().get("favorites", [])

def toggle_favorite(project_id: str, globaldata_id: str, project_name: str, company_name: str) -> dict:
    r = requests.post(f"{_base()}/api/favorites", headers=_headers(), json={
        "project_id": project_id,
        "globaldata_id": globaldata_id,
        "project_name": project_name,
        "company_name": company_name,
    })
    r.raise_for_status()
    return r.json()

def update_contact(contact_id: str, fields: dict) -> dict:
    r = requests.patch(f"{_base()}/api/contacts/{contact_id}", headers=_headers(), json=fields)
    r.raise_for_status()
    return r.json()
