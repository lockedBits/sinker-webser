import uuid
from datetime import datetime, timedelta

def generate_uuid():
    return str(uuid.uuid4())

def get_timestamp_after_days(days):
    return datetime.utcnow() + timedelta(days=days)

def current_timestamp():
    return datetime.utcnow()

def standard_response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data if data else {}
    }


