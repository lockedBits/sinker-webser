from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from srv.firebase.firebase_api import db
from srv.utils.helpers import generate_uuid, get_timestamp_after_days, current_timestamp, standard_response

from srv.session.sessionManager import *

def generate_unique_uuid():
    while True:
        new_uuid = str(generate_uuid())
        existing = db.collection("users").where("uuid", "==", new_uuid).stream()
        if not any(existing):
            return new_uuid


def signup(request):
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    activation_key = data.get("activation_key")

    if not all([username, password, activation_key]):
        return jsonify(standard_response(False, "Missing fields"))

    key_ref = db.collection("keys").document(activation_key)
    key_doc = key_ref.get()

    if not key_doc.exists:
        return jsonify(standard_response(False, "Invalid key"))

    key_data = key_doc.to_dict()
    duration_days = key_data.get("duration_days")
    key_type = key_data.get("type")

    if not duration_days or not key_type:
        return jsonify(standard_response(False, "Invalid key: missing duration or type"))

    now = current_timestamp()
    additional_expiry = timedelta(days=duration_days)

    existing_user_query = db.collection("users").where("username", "==", username).limit(1).stream()
    existing_user_doc = next(existing_user_query, None)

    activation_entry = {
        "key": activation_key,
        "duration_days": duration_days,
        "type": key_type,
        "used_at": now.isoformat()
    }

    if existing_user_doc:
        if key_type != "topup":
            return jsonify(standard_response(False, "Only 'topup' keys can be used for existing accounts"))

        user_data = existing_user_doc.to_dict()

        if user_data.get("credentials", {}).get("password") != password:
            return jsonify(standard_response(False, "Incorrect password"))

        key_ref.delete()

        access_data = user_data.get("access", {})
        current_expiry_str = access_data.get("expires_at")
        current_expiry = datetime.fromisoformat(current_expiry_str) if current_expiry_str else now
        new_expiry = current_expiry + additional_expiry if current_expiry > now else now + additional_expiry

        activation_history = access_data.get("activation_history", [])
        activation_history.append(activation_entry)

        user_ref = db.collection("users").document(user_data["uuid"])
        user_ref.update({
            "access.expires_at": new_expiry.isoformat(),
            "access.activation_history": activation_history
        })

        return jsonify(standard_response(True, "Account access extended", {
            "expires_at": new_expiry.isoformat(),
            "uuid": user_data.get("uuid")
        }))

    else:
        if key_type != "activation":
            return jsonify(standard_response(False, "Only 'activation' keys can be used for new accounts"))

        unique_uuid = generate_unique_uuid()
        new_expiry = now + additional_expiry

        key_ref.delete()

        user_ref = db.collection("users").document(unique_uuid)
        user_ref.set({
            "uuid": unique_uuid,
            "username": username,
            "credentials": {
                "password": password
            },
            "access": {
                "expires_at": new_expiry.isoformat(),
                "activation_history": [activation_entry]
            },
            "session": {
                "active_token": None,
                "created_at": None,
                "token_history": []
            }
        })

        return jsonify(standard_response(True, "Signup successful", {
            "expires_at": new_expiry.isoformat(),
            "uuid": unique_uuid
        }))


def login(request):
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not all([username, password]):
        return jsonify(standard_response(False, "Missing fields"))

    user_query = db.collection("users").where("username", "==", username).limit(1).stream()
    user_doc = next(user_query, None)

    if not user_doc:
        return jsonify(standard_response(False, "User not found"))

    user_data = user_doc.to_dict()

    if user_data.get("credentials", {}).get("password") != password:
        return jsonify(standard_response(False, "Incorrect password"))

    access_data = user_data.get("access", {})
    expires_at_str = access_data.get("expires_at")

    if not expires_at_str:
        return jsonify(standard_response(False, "Missing account expiry info"))

    if current_timestamp() > datetime.fromisoformat(expires_at_str):
        return jsonify(standard_response(False, "Account expired"))

    token = create_session_token(user_data["uuid"])

    return jsonify(standard_response(True, "Login successful", {
        "token": token
    }))

def logout():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify(standard_response(False, "Missing token"))

    uuid = validate_session_token(token)

    if not uuid:
        return jsonify(standard_response(False, "Invalid or expired session"))

    invalidate_user_session(uuid)
    return jsonify(standard_response(True, "Logout successful"))
