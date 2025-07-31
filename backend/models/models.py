# backend/models/models.py (Fully Updated, Complete, and Corrected)

from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict
import datetime

# --- Settings Models ---
class CollegeInfo(BaseModel):
    college_name: str = Field(default="Demo College of Technology")
    college_logo_url: Optional[str] = Field(default=None)

class Position(BaseModel):
    id: str
    title: str
    gender_requirement: Optional[Literal["boy", "girl"]] = None

class StreamConfig(BaseModel):
    stream_name: str
    divisions: List[str]

class ElectionSettings(BaseModel):
    college_info: CollegeInfo = Field(default_factory=CollegeInfo)
    positions: List[Position] = Field(default=[
        Position(id="cr_boy", title="Class Representative (Boy)", gender_requirement="boy"),
        Position(id="cr_girl", title="Class Representative (Girl)", gender_requirement="girl"),
    ])
    academic_structure: List[StreamConfig] = Field(default=[
        StreamConfig(stream_name="Science", divisions=["A", "B", "C", "D", "E"]),
        StreamConfig(stream_name="Commerce", divisions=["A", "B", "C", "D", "E", "F"]),
        StreamConfig(stream_name="Arts", divisions=[]),
    ])
    identification_mode: Literal["name_and_id", "id_only"] = Field(default="name_and_id")
    voting_status: Literal["OPEN", "CLOSED"] = Field(default="CLOSED")


# --- Candidate Models ---
class Candidate(BaseModel):
    name: str
    position_id: str
    gender: Literal["boy", "girl"]
    photo_url: Optional[str] = None


# --- Student and Voting Models ---
class Student(BaseModel):
    name: str
    roll_number: int
    stream: str
    division: Optional[str] = None

class StudentIdentifierForm(BaseModel):
    name: Optional[str] = None
    roll_number: int
    stream: str
    division: Optional[str] = None

class Vote(BaseModel):
    selections: Dict[str, str]
    student_identifier: str


# --- General API Models ---
class AdminRequest(BaseModel):
    password: str

class BulkUploadResponse(BaseModel):
    students_added: int
    duplicates_found: int
    errors: List[str]

class AuditLog(BaseModel):
    timestamp: datetime.datetime
    actor: str
    action: str
    details: str

# --- NEW: Specific Request Body Models (THIS WAS MISSING) ---
# This model is specifically for the update settings endpoint to avoid ambiguity.
class SettingsUpdateRequest(BaseModel):
    settings: ElectionSettings
    request: AdminRequest