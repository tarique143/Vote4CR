# backend/services/image_uploader.py (New File)

import os
from fastapi import UploadFile, HTTPException
import shutil
from pathlib import Path

# Define the base directory where static files (like images) will be served from.
# We create a 'static' folder inside the 'backend' directory.
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

def save_upload_file(upload_file: UploadFile, destination_folder: str) -> str:
    """
    Saves an uploaded file to a specific destination folder within the static directory.
    Returns the path of the saved file.
    """
    try:
        # Create the destination folder if it doesn't exist (e.g., 'static/candidate_photos')
        destination_path = STATIC_DIR / destination_folder
        destination_path.mkdir(parents=True, exist_ok=True)
        
        # Define the full path for the file
        file_path = destination_path / upload_file.filename
        
        # Save the file to the path
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"There was an error uploading the file: {e}")
    finally:
        upload_file.file.close()
        
    # Return the relative path (e.g., 'static/candidate_photos/rohan.jpg')
    return str(file_path)

def get_file_url(file_path: str) -> str:
    """
    Converts a local file path to a URL that can be accessed from the browser.
    Example: 'static/candidate_photos/rohan.jpg' becomes '/static/candidate_photos/rohan.jpg'
    """
    # The URL should be relative to the server root.
    # FastAPI will serve files from the 'static' directory at the '/static' URL path.
    return "/" + file_path.replace("\\", "/") # Ensure forward slashes for URLs