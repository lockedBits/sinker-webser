import jwt
import os
from datetime import datetime, timedelta
from firebase_api import db
from utils import current_timestamp

# Secret key for signing JWTs
SECRET_KEY = os.getenv("JWT_SECRET", "your_secret_key")
TOKEN_EXPIRATION_HOURS = 24


def create_session_token(uuid):
    """Generates a JWT and stores it as the active session, archiving old session if any."""
    expiration_time = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS)
    token = jwt.encode(
        {"uuid": uuid, "exp": expiration_time.timestamp()},
        SECRET_KEY,
        algorithm="HS256"
    )

    user_ref = db.collection("users").document(uuid)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        old_token = user_data.get("activeSession")
        if old_token:
            # Push old token to token history
            token_history = user_data.get("token_history", [])
            token_history.append({
                "token": old_token,
                "invalidated_at": current_timestamp().isoformat()
            })
            user_ref.update({
                "token_history": token_history
            })

    # Set new token as active session
    user_ref.update({
        "activeSession": token
    })

    return token


def validate_session_token(token):
    """Validates JWT and checks if it matches the active session in Firestore."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        uuid = payload.get("uuid")

        user_doc = db.collection("users").document(uuid).get()
        if not user_doc.exists:
            return None

        active_token = user_doc.to_dict().get("activeSession")
        if active_token != token:
            return None

        return uuid

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def invalidate_user_session(uuid):
    """Archives current active session token and clears activeSession field."""
    user_ref = db.collection("users").document(uuid)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return

    user_data = user_doc.to_dict()
    current_token = user_data.get("activeSession")

    if current_token:
        token_history = user_data.get("token_history", [])
        token_history.append({
            "token": current_token,
            "invalidated_at": current_timestamp().isoformat()
        })

        user_ref.update({
            "token_history": token_history,
            "activeSession": None
        })
