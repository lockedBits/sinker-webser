import hashlib
from datetime import datetime

# 🔐 Hash password (simple SHA256 for now — can switch to bcrypt later)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 🔐 Compare hashed password
def verify_password(plain, hashed):
    return hash_password(plain) == hashed

# ⏳ Check if access is expired
def is_access_expired(access_expiry):
    if not access_expiry:
        return True
    if isinstance(access_expiry, str):
        access_expiry = datetime.fromisoformat(access_expiry)
    return datetime.utcnow() > access_expiry

# 🔎 ISO string converter (safe for JSON)
def to_iso(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)

# 📅 Extend access expiry by days
def extend_expiry(current_expiry, extra_days):
    now = datetime.utcnow()
    current_expiry = (
        datetime.fromisoformat(current_expiry)
        if isinstance(current_expiry, str)
        else current_expiry
    )
    base_time = max(now, current_expiry)
    return base_time.replace(microsecond=0) + timedelta(days=extra_days)
