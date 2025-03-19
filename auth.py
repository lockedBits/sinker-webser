from flask import Blueprint, request, jsonify
from firebase_api import db
from helpers import generate_uuid, get_timestamp_after_days, current_timestamp, standard_response
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def generate_unique_uuid():
    while True:
        new_uuid = str(generate_uuid())
        existing = db.collection("users").where("uuid", "==", new_uuid).stream()
        if not any(existing):
            return new_uuid


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    activation_key = data.get("activation_key")

    if not all([username, password, activation_key]):
        return jsonify(standard_response(False, "Missing fields"))

    key_ref = db.collection("activation_keys").document(activation_key)
    key_doc = key_ref.get()

    if not key_doc.exists:
        return jsonify(standard_response(False, "Invalid activation key"))

    key_data = key_doc.to_dict()
    duration_days = key_data.get("duration_days")
    key_type = key_data.get("type")

    if not duration_days or not key_type:
        return jsonify(standard_response(False, "Invalid key: missing duration or type"))

    now = current_timestamp()
    additional_expiry = timedelta(days=duration_days)

    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()

    activation_entry = {
        "key": activation_key,
        "duration_days": duration_days,
        "type": key_type,
        "used_at": now.isoformat()
    }

    # Delete the activation key from DB
    key_ref.delete()

    if user_doc.exists:
        # Existing user: only allow topup keys
        if key_type != "topup":
            return jsonify(standard_response(False, "Only 'topup' keys can be used for existing accounts"))

        user_data = user_doc.to_dict()

        # Check if password matches
        if user_data.get("password") != password:
            return jsonify(standard_response(False, "Incorrect password"))

        current_expiry = datetime.fromisoformat(user_data["expires_at"])
        new_expiry = current_expiry + additional_expiry if current_expiry > now else now + additional_expiry

        user_ref.update({
            "expires_at": new_expiry.isoformat(),
            "activation_history": user_data.get("activation_history", []) + [activation_entry]
        })

        return jsonify(standard_response(True, "Account access extended", {
            "expires_at": new_expiry.isoformat(),
            "uuid": user_data.get("uuid")
        }))

    else:
        # New user: only allow activation keys
        if key_type != "activation":
            return jsonify(standard_response(False, "Only 'activation' keys can be used for new accounts"))

        unique_uuid = generate_unique_uuid()
        new_expiry = now + additional_expiry

        user_ref.set({
            "username": username,
            "password": password,
            "uuid": unique_uuid,
            "expires_at": new_expiry.isoformat(),
            "activation_history": [activation_entry]
        })

        return jsonify(standard_response(True, "Signup successful", {
            "expires_at": new_expiry.isoformat(),
            "uuid": unique_uuid
        }))


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not all([username, password]):
        return jsonify(standard_response(False, "Missing fields"))

    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return jsonify(standard_response(False, "User not found"))

    user_data = user_doc.to_dict()

    if user_data["password"] != password:
        return jsonify(standard_response(False, "Incorrect password"))

    if current_timestamp() > datetime.fromisoformat(user_data["expires_at"]):
        return jsonify(standard_response(False, "Account expired"))

    return jsonify(standard_response(True, "Login successful", {
        "username": username,
        "uuid" : user_data["uuid"]
    }))
