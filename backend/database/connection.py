# backend/database/connection.py (New File)

import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the backend directory
load_dotenv()

# --- MongoDB Connection Setup ---
MONGO_DETAILS = os.getenv("MONGO_URI")
if not MONGO_DETAILS:
    raise ValueError("FATAL ERROR: MONGO_URI environment variable is not set. Please check your .env file.")

# Create a single, reusable client instance
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.voting_system

# --- Database Collections ---
# We define all our collections here so they can be imported easily elsewhere.
candidate_collection = database.get_collection("candidates_v2")
vote_collection = database.get_collection("votes_v2")
settings_collection = database.get_collection("settings_v2")
student_collection = database.get_collection("students_v2")
voted_student_collection = database.get_collection("voted_students_v2")
audit_log_collection = database.get_collection("audit_logs")

# Note: We use '_v2' to avoid conflicts with your old data.
# You can safely delete the old collections later.