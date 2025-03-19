from datetime import datetime, timedelta
import uuid
from app.services.firebase_service import get_db

db = get_db()

def create_activation_key(duration_days, created_by="admin"):
    key = str(uuid.uuid4()).replace("-", "")[:10].upper()
    doc_ref = db.collection("activation_keys").document(key)
    doc_ref.set({
        "duration_days": duration_days,
        "created_by": created_by,
        "created_at": datetime.utcnow()
    })
    return key

def validate_key(key):
    key_ref = db.collection("activation_keys").document(key)
    doc = key_ref.get()
    return doc if doc.exists else None

def mark_key_as_used(key, username):
    key_ref = db.collection("activation_keys").document(key)
    key_ref.update({
        "used_by": username,
        "used_on": datetime.utcnow()
    })

def list_keys():
    keys = db.collection("activation_keys").stream()
    return [doc.to_dict() | {"key": doc.id} for doc in keys]
