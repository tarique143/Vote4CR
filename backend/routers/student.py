# backend/routers/student.py (Fully Updated with Logging)

from fastapi import APIRouter, HTTPException
from typing import List

# Import our models and database collections
from models.models import StudentIdentifierForm, Vote, ElectionSettings, Candidate
from database.connection import (
    settings_collection, 
    student_collection, 
    voted_student_collection, 
    candidate_collection,
    vote_collection
)
# NEW: Import the logger service
from services.audit_logger import log_activity

router = APIRouter()

# --- Helper Function ---
def get_unique_student_identifier(student: StudentIdentifierForm) -> str:
    division_str = student.division if student.division else "NA"
    return f"{student.stream}-{division_str}-{student.roll_number}"

# --- Student-Facing API Endpoints ---

@router.get("/api/settings", response_model=ElectionSettings)
async def get_public_election_settings():
    settings = await settings_collection.find_one({"_id": "global_settings"})
    if not settings:
        default_settings = ElectionSettings()
        await settings_collection.insert_one({"_id": "global_settings", **default_settings.dict()})
        await log_activity("System", "Initialized Default Settings", "First run detected.")
        return default_settings
    return ElectionSettings(**settings)


@router.post("/api/student/identify")
async def identify_student(student_form: StudentIdentifierForm):
    settings = await get_public_election_settings()
    
    query = {"roll_number": student_form.roll_number, "stream": student_form.stream}
    stream_structure = next((s for s in settings.academic_structure if s.stream_name == student_form.stream), None)
    if not stream_structure:
        raise HTTPException(status_code=400, detail="Invalid stream selected.")
    
    if stream_structure.divisions:
        if not student_form.division or student_form.division not in stream_structure.divisions:
            raise HTTPException(status_code=400, detail=f"Invalid division for {student_form.stream} stream.")
        query["division"] = student_form.division
    else:
        query["division"] = None

    if settings.identification_mode == "name_and_id":
        if not student_form.name:
            raise HTTPException(status_code=400, detail="Name is required for identification.")
        query["name"] = student_form.name

    db_student = await student_collection.find_one(query)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found. Please check all details.")

    unique_id = get_unique_student_identifier(student_form)
    if await voted_student_collection.find_one({"student_identifier": unique_id}):
        raise HTTPException(status_code=403, detail="This student has already voted.")

    return {
        "message": "Student identified successfully.", 
        "student_identifier": unique_id, 
        "student_name": db_student.get("name")
    }


@router.get("/api/candidates", response_model=List[Candidate])
async def get_candidates():
    candidates_cursor = candidate_collection.find({}, {"_id": 0})
    return [Candidate(**doc) for doc in await candidates_cursor.to_list(1000)]


@router.post("/api/vote")
async def submit_vote(vote: Vote):
    settings = await get_public_election_settings()
    if settings.voting_status == "CLOSED":
        raise HTTPException(status_code=403, detail="Voting is currently closed.")
    
    if await voted_student_collection.find_one({"student_identifier": vote.student_identifier}):
        raise HTTPException(status_code=403, detail="Your vote has already been submitted.")

    for position_id, candidate_name in vote.selections.items():
        position = next((p for p in settings.positions if p.id == position_id), None)
        if not position:
            raise HTTPException(status_code=400, detail=f"Invalid position ID '{position_id}' in vote.")
        
        candidate_query = {"name": candidate_name, "position_id": position_id}
        if not await candidate_collection.find_one(candidate_query):
            raise HTTPException(status_code=400, detail=f"Candidate '{candidate_name}' is not valid for position '{position.title}'.")

    await vote_collection.insert_one(vote.dict())
    await voted_student_collection.insert_one({"student_identifier": vote.student_identifier})
    
    # --- NEW: Log the successful vote ---
    await log_activity(
        actor="Student", 
        action="Vote Cast", 
        details=f"Identifier: {vote.student_identifier}"
    )
    
    return {"message": "✅ Your vote has been successfully recorded."}