# backend/routers/admin.py (Fully Updated, Complete, and Corrected)

from fastapi import APIRouter, HTTPException, Body, Depends, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Dict
import pandas as pd
import os
import csv
import io

# Import models, db collections, and helper functions
from models.models import (
    ElectionSettings, Candidate, Student, AdminRequest, BulkUploadResponse, 
    AuditLog, SettingsUpdateRequest
)
from database.connection import (
    settings_collection,
    candidate_collection,
    student_collection,
    vote_collection,
    voted_student_collection,
    audit_log_collection
)
from services.image_uploader import save_upload_file, get_file_url
from services.audit_logger import log_activity

router = APIRouter()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "teacher123")

# --- Standardized Dependency for Password Checking ---
async def verify_admin_password(request: AdminRequest = Body(...)):
    if request.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect admin password.")
    return True

# === Settings Management Endpoints ===
@router.post("/api/admin/settings")
async def update_election_settings(payload: SettingsUpdateRequest):
    """Updates the global election settings."""
    if payload.request.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect admin password.")
    
    settings_data = payload.settings
    await settings_collection.update_one(
        {"_id": "global_settings"},
        {"$set": settings_data.dict()},
        upsert=True
    )
    await log_activity("Admin", "Updated Election Settings")
    return {"message": "Settings updated successfully."}

# === Candidate Management Endpoints ===
@router.post("/api/admin/candidate", response_model=Candidate)
async def add_candidate(candidate: Candidate, request: AdminRequest = Body(...)):
    if request.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect admin password.")
    if await candidate_collection.find_one({"name": candidate.name, "position_id": candidate.position_id}):
        raise HTTPException(status_code=400, detail="A candidate with this name already exists for this position.")
    await candidate_collection.insert_one(candidate.dict())
    await log_activity("Admin", "Added Candidate", f"Name: {candidate.name}, Position ID: {candidate.position_id}")
    return candidate

@router.post("/api/admin/candidate/photo")
async def upload_candidate_photo(
    name: str = Body(...),
    position_id: str = Body(...),
    password: str = Body(...),
    file: UploadFile = File(...)
):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect admin password.")
    candidate = await candidate_collection.find_one({"name": name, "position_id": position_id})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    file_path = save_upload_file(file, "candidate_photos")
    photo_url = get_file_url(file_path)
    await candidate_collection.update_one({"_id": candidate["_id"]}, {"$set": {"photo_url": photo_url}})
    await log_activity("Admin", "Uploaded Photo", f"For candidate: {name}")
    return {"message": "Photo uploaded successfully.", "photo_url": photo_url}

@router.post("/api/admin/candidate/delete", dependencies=[Depends(verify_admin_password)])
async def delete_candidate(candidate: Candidate):
    result = await candidate_collection.delete_one({"name": candidate.name, "position_id": candidate.position_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    await log_activity("Admin", "Deleted Candidate", f"Name: {candidate.name}")
    return {"message": "Candidate deleted successfully."}

# === Student Roster Management Endpoints ===
@router.post("/api/admin/student/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_students(
    password: str = Body(...),
    file: UploadFile = File(...)
):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect admin password.")
    students_to_add = []
    duplicates_found = 0
    errors = []
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8'))) if file.filename.endswith('.csv') else pd.read_excel(io.BytesIO(content))
        df.columns = [col.strip().lower() for col in df.columns]
        required_columns = ["name", "roll_number", "stream", "division"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"File must contain columns: {', '.join(required_columns)}")
        for index, row in df.iterrows():
            student_data = {"name": str(row["name"]).strip(), "roll_number": int(row["roll_number"]), "stream": str(row["stream"]).strip(), "division": str(row["division"]).strip() if pd.notna(row["division"]) and str(row["division"]).strip() else None}
            if not await student_collection.find_one({"roll_number": student_data["roll_number"], "stream": student_data["stream"]}):
                students_to_add.append(Student(**student_data).dict())
            else:
                duplicates_found += 1
    except Exception as e:
        errors.append(f"Error processing file: {e}")
        return BulkUploadResponse(students_added=0, duplicates_found=0, errors=errors)
    if students_to_add:
        await student_collection.insert_many(students_to_add)
        await log_activity("Admin", "Bulk Upload", f"Added {len(students_to_add)} new students.")
    return BulkUploadResponse(students_added=len(students_to_add), duplicates_found=duplicates_found, errors=[])

@router.post("/api/admin/students", response_model=List[Student], dependencies=[Depends(verify_admin_password)])
async def get_all_students():
    """Fetches the complete student roster."""
    students_cursor = student_collection.find({}, {"_id": 0})
    return [Student(**doc) for doc in await students_cursor.to_list(10000)]
    
# === Results, Stats, and Danger Zone Endpoints ===
@router.post("/api/admin/results", dependencies=[Depends(verify_admin_password)])
async def get_results():
    """Fetches comprehensive election results and stats."""
    settings = await settings_collection.find_one({"_id": "global_settings"}) or {}
    positions = settings.get("positions", [])
    total_students = await student_collection.count_documents({})
    total_votes_cast = await vote_collection.count_documents({})
    results = {}
    for pos in positions:
        pos_id, pos_title = pos["id"], pos["title"]
        candidates = await candidate_collection.find({"position_id": pos_id}).to_list(100)
        vote_counts = {cand["name"]: 0 for cand in candidates}
        async for vote in vote_collection.find({f"selections.{pos_id}": {"$exists": True}}):
            selection = vote["selections"].get(pos_id)
            if selection in vote_counts: vote_counts[selection] += 1
        winner = "N/A"
        if any(vote_counts.values()) and (max_votes := max(vote_counts.values())) > 0:
            tied_winners = [name for name, count in vote_counts.items() if count == max_votes]
            winner = " & ".join(tied_winners) + (" (TIE!)" if len(tied_winners) > 1 else "")
        results[pos_id] = {"position_title": pos_title, "vote_counts": vote_counts, "winner": winner}
    return {"voter_turnout": {"total_students": total_students, "total_votes_cast": total_votes_cast}, "results": results}

@router.post("/api/admin/results/export", dependencies=[Depends(verify_admin_password)])
async def export_results_as_csv():
    """Exports the final results to a CSV file."""
    data = await get_results()
    filepath = "election_results.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Election Results Export"]); writer.writerow([])
        writer.writerow(["Voter Turnout"]); writer.writerow(["Total Students", data["voter_turnout"]["total_students"]]); writer.writerow(["Votes Cast", data["voter_turnout"]["total_votes_cast"]]); writer.writerow([])
        for _, pos_data in data["results"].items():
            writer.writerow([f"Position: {pos_data['position_title']}"]); writer.writerow(["Candidate", "Votes"])
            for name, count in pos_data["vote_counts"].items(): writer.writerow([name, count])
            writer.writerow(["Winner(s)", pos_data["winner"]]); writer.writerow([])
    return FileResponse(path=filepath, media_type='text/csv', filename=filepath)

@router.post("/api/admin/reset-election", dependencies=[Depends(verify_admin_password)])
async def reset_election():
    await vote_collection.delete_many({})
    await voted_student_collection.delete_many({})
    await log_activity("Admin", "Election Reset", "All votes have been cleared.")
    return {"message": "Election has been reset successfully."}

@router.post("/api/admin/clear-students", dependencies=[Depends(verify_admin_password)])
async def clear_students():
    result = await student_collection.delete_many({})
    await log_activity("Admin", "Cleared Student Roster", f"Deleted {result.deleted_count} students.")
    return {"message": "The entire student roster has been cleared."}

@router.post("/api/admin/clear-candidates", dependencies=[Depends(verify_admin_password)])
async def clear_candidates():
    result = await candidate_collection.delete_many({})
    await log_activity("Admin", "Cleared Candidate List", f"Deleted {result.deleted_count} candidates.")
    return {"message": "The entire candidate list has been cleared."}

@router.post("/api/admin/audit-logs", response_model=List[AuditLog], dependencies=[Depends(verify_admin_password)])
async def get_audit_logs():
    """Fetches all activity logs from the database, newest first."""
    logs_cursor = audit_log_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(200)
    return [AuditLog(**log) for log in await logs_cursor.to_list(200)]