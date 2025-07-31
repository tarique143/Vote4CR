# backend/services/audit_logger.py (New File)

import datetime
from database.connection import audit_log_collection

async def log_activity(actor: str, action: str, details: str = ""):
    """
    Logs an important activity to the audit_logs collection in the database.
    """
    log_entry = {
        "timestamp": datetime.datetime.utcnow(),
        "actor": actor,
        "action": action,
        "details": details
    }
    await audit_log_collection.insert_one(log_entry)