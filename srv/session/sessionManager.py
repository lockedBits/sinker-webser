import jwt
import os
from datetime import datetime, timedelta

from srv.firebase.firebase_api import db
from srv.utils.helpers import current_timestamp

# Secret key for signing JWTs
SECRET_KEY = os.getenv("JWT_SECRET", "your_secret_key")
TOKEN_EXPIRATION_HOURS = 24

def create_session_token(user_uuid):
    """Generates a JWT and stores it as the active session, archiving old session if any."""

    expiration_time = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS)
    token = jwt.encode(
        {"uuid": user_uuid, "exp": expiration_time.timestamp()},
        SECRET_KEY,
        algorithm="HS256"
    )

    user_ref = db.collection("users").document(user_uuid)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        old_token = user_data.get("session", {}).get("active_token")

        token_history = user_data.get("session", {}).get("token_history", [])
        if old_token:
            # Archive old token
            token_history.append({
                "token": old_token,
                "invalidated_at": current_timestamp().isoformat()
            })

        # Store the new token and archive old one
        user_ref.update({
            "session": {
                "active_token": token,
                "created_at": datetime.utcnow().isoformat(),
                "token_history": token_history
            }
        })
    else:
        raise ValueError(f"[SessionManager] No user found with UUID {user_uuid}")

    return token

def validate_session_token(token):
    """Validates JWT and checks if it matches the active session in Firestore."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        uuid = payload.get("uuid")

        user_doc = db.collection("users").document(uuid).get()
        if not user_doc.exists:
            return None

        active_token = user_doc.to_dict().get("session", {}).get("active_token")
        if active_token != token:
            return None

        return uuid

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def invalidate_user_session(uuid):
    """Archives current active session token and clears active_session field."""
    user_ref = db.collection("users").document(uuid)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return

    user_data = user_doc.to_dict()
    current_token = user_data.get("session", {}).get("active_token")
    token_history = user_data.get("session", {}).get("token_history", [])

    if current_token:
        token_history.append({
            "token": current_token,
            "invalidated_at": current_timestamp().isoformat()
        })

        user_ref.update({
            "session": {
                "active_token": None,
                "created_at": None,
                "token_history": token_history
            }
        })
