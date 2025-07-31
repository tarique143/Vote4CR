# ui/api.py (Fully Updated and Corrected for Final Backend Auth)

import streamlit as st
import requests

API_URL = "https://tarique123.pythonanywhere.com" # Use your PythonAnywhere URL when deployed

def handle_request(method, url, json_payload=None, **kwargs):
    """
    A robust, centralized function to handle all API requests.
    """
    try:
        response = requests.request(method, url, json=json_payload, timeout=30, **kwargs)
        response.raise_for_status()
        if response.headers.get('content-type') == 'text/csv':
            return response
        return response.json() if response.content else {"status": "success"} # Return success for actions with no body
    except requests.exceptions.HTTPError as err:
        try:
            error_detail = err.response.json().get("detail", err.response.text)
            st.toast(f"❌ Error: {error_detail}", icon="🔥")
        except:
            st.toast(f"❌ HTTP Error: {err.response.status_code} {err.response.reason}", icon="🔥")
        return None
    except requests.exceptions.ConnectionError:
        st.toast(f"🔌 Connection Error: Could not connect to the server at {API_URL}.", icon="🔌")
        return None
    except requests.exceptions.RequestException as e:
        st.toast(f"❌ An unexpected request error occurred: {e}", icon="🔥")
        return None

# --- Public API Functions (No Auth Needed) ---

def get_election_settings():
    return handle_request("get", f"{API_URL}/api/settings")

def get_candidates():
    return handle_request("get", f"{API_URL}/api/candidates") or []

def identify_student(payload):
    return handle_request("post", f"{API_URL}/api/student/identify", json_payload=payload)

def submit_vote(selections, student_identifier):
    payload = {"selections": selections, "student_identifier": student_identifier}
    return handle_request("post", f"{API_URL}/api/vote", json_payload=payload)

# --- Admin API Functions (All now send the correct password format) ---

def update_election_settings(settings_data, password):
    # This endpoint has a special model, so its structure is different and correct.
    payload = {
        "settings": settings_data,
        "request": {"password": password}
    }
    return handle_request("post", f"{API_URL}/api/admin/settings", json_payload=payload)

def add_candidate(candidate_data, password):
    # This endpoint also has a special model structure.
    payload = {"candidate": candidate_data, "request": {"password": password}}
    return handle_request("post", f"{API_URL}/api/admin/candidate", json_payload=payload)

def upload_candidate_photo(name, position_id, file, password):
    # File uploads use 'data' for form fields, not JSON.
    data = {"password": password}
    files = {"file": (file.name, file, file.type)}
    return handle_request("post", f"{API_URL}/api/admin/candidate/photo?name={name}&position_id={position_id}", data=data, files=files)

def delete_candidate(candidate_data, password):
    # This endpoint also has a special model structure.
    payload = {"candidate": candidate_data, "request": {"password": password}}
    return handle_request("post", f"{API_URL}/api/admin/candidate/delete", json_payload=payload)

def bulk_upload_students(file, password):
    # File uploads use 'data' for form fields.
    data = {"password": password}
    files = {"file": (file.name, file, file.type)}
    return handle_request("post", f"{API_URL}/api/admin/student/bulk-upload", data=data, files=files)

def get_all_students(password):
    # FIXED: The payload should be {"password": password} directly.
    payload = {"password": password}
    return handle_request("post", f"{API_URL}/api/admin/students", json_payload=payload) or []

def get_results(password):
    # FIXED: The payload should be {"password": password} directly.
    payload = {"password": password}
    return handle_request("post", f"{API_URL}/api/admin/results", json_payload=payload)

def export_results_as_csv(password):
    # FIXED: The payload should be {"password": password} directly.
    payload = {"password": password}
    return handle_request("post", f"{API_URL}/api/admin/results/export", json_payload=payload)

def reset_election(password):
    # FIXED: The payload should be {"password": password} directly.
    payload = {"password": password}
    return handle_request("post", f"{API_URL}/api/admin/reset-election", json_payload=payload)

def clear_student_roster(password):
    # FIXED: The payload should be {"password": password} directly.
    payload = {"password": password}
    return handle_request("post", f"{API_URL}/api/admin/clear-students", json_payload=payload)

def clear_candidate_list(password):
    # FIXED: The payload should be {"password": password} directly.
    payload = {"password": password}
    return handle_request("post", f"{API_URL}/api/admin/clear-candidates", json_payload=payload)

def get_audit_logs(password):
    # FIXED: The payload should be {"password": password} directly.
    payload = {"password": password}
    return handle_request("post", f"{API_URL}/api/admin/audit-logs", json_payload=payload) or []
