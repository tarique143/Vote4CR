# ui/api.py (Fully Updated, Complete, and Corrected for Caching Error)

import streamlit as st
import requests

# Ensure your live backend URL is correct
API_URL = "https://tarique123.pythonanywhere.com"

def handle_request(method, url, json_payload=None, **kwargs):
    """
    A robust, centralized function to handle all API requests.
    FIXED: This version removes all Streamlit UI calls (like st.toast) to make it cache-safe.
    It now returns the response object on success and None on failure.
    The UI files are now responsible for showing error messages to the user.
    """
    try:
        response = requests.request(method, url, json=json_payload, timeout=30, **kwargs)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        return response
    except requests.exceptions.RequestException as e:
        # We print the error here for the developer to see in the logs, but don't show it in the UI.
        print(f"API Request Failed: {e}")
        return None

# --- Public API Functions ---

def get_election_settings():
    response = handle_request("get", f"{API_URL}/api/settings")
    return response.json() if response else None

def get_candidates():
    response = handle_request("get", f"{API_URL}/api/candidates")
    return response.json() if response else []

def identify_student(payload):
    response = handle_request("post", f"{API_URL}/api/student/identify", json_payload=payload)
    return response.json() if response else None

def submit_vote(selections, student_identifier):
    payload = {"selections": selections, "student_identifier": student_identifier}
    response = handle_request("post", f"{API_URL}/api/vote", json_payload=payload)
    return response.json() if response else None

# --- Admin API Functions ---

def update_election_settings(settings_data, password):
    payload = {"settings": settings_data, "request": {"password": password}}
    return handle_request("post", f"{API_URL}/api/admin/settings", json_payload=payload)

def add_candidate(candidate_data, password):
    payload = {"candidate": candidate_data, "request": {"password": password}}
    return handle_request("post", f"{API_URL}/api/admin/candidate", json_payload=payload)

def upload_candidate_photo(name, position_id, file, password):
    data = {"password": password}
    files = {"file": (file.name, file, file.type)}
    return handle_request("post", f"{API_URL}/api/admin/candidate/photo?name={name}&position_id={position_id}", data=data, files=files)

def delete_candidate(candidate_data, password):
    payload = {"candidate": candidate_data, "request": {"password": password}}
    return handle_request("post", f"{API_URL}/api/admin/candidate/delete", json_payload=payload)

def bulk_upload_students(file, password):
    data = {"password": password}
    files = {"file": (file.name, file, file.type)}
    response = handle_request("post", f"{API_URL}/api/admin/student/bulk-upload", data=data, files=files)
    return response.json() if response else None

def get_all_students(password):
    payload = {"password": password}
    response = handle_request("post", f"{API_URL}/api/admin/students", json_payload=payload)
    return response.json() if response else []

def get_results(password):
    payload = {"password": password}
    response = handle_request("post", f"{API_URL}/api/admin/results", json_payload=payload)
    return response.json() if response else None

def export_results_as_csv(password):
    payload = {"password": password}
    # For file downloads, we return the entire response object
    return handle_request("post", f"{API_URL}/api/admin/results/export", json_payload=payload)

def reset_election(password):
    payload = {"password": password}
    response = handle_request("post", f"{API_URL}/api/admin/reset-election", json_payload=payload)
    return response.json() if response else None

def clear_student_roster(password):
    payload = {"password": password}
    response = handle_request("post", f"{API_URL}/api/admin/clear-students", json_payload=payload)
    return response.json() if response else None

def clear_candidate_list(password):
    payload = {"password": password}
    response = handle_request("post", f"{API_URL}/api/admin/clear-candidates", json_payload=payload)
    return response.json() if response else None

def get_audit_logs(password):
    payload = {"password": password}
    response = handle_request("post", f"{API_URL}/api/admin/audit-logs", json_payload=payload)
    return response.json() if response else []
