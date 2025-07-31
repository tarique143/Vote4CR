# backend/main.py (Fully Updated and Refactored)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

# Import the routers we created
from routers import student, admin

# Create the main FastAPI application instance
app = FastAPI(
    title="E-Voting API",
    description="A flexible and dynamic API for managing school and college elections.",
    version="2.0.0"
)

# --- Include Routers ---
# This adds all the API endpoints from our router files to the main application.
app.include_router(student.router)
app.include_router(admin.router)


# --- Mount Static Files Directory ---
# This is crucial. It tells FastAPI that any request starting with "/static"
# should be served from the "static" directory. This is how candidate photos
# will be accessible to the browser.
# We create the directory if it doesn't exist to prevent errors on startup.
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


# --- Root Endpoint ---
# A simple endpoint to confirm that the API is running.
@app.get("/")
def read_root():
    return {"message": "Welcome to the E-Voting API v2.0"}