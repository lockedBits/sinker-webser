from flask import Blueprint, request, jsonify
from firebase_api import db
from helpers import generate_uuid, get_timestamp_after_days, current_timestamp, standard_response

auth_bp = Blueprint('auth', __name__)

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
    if key_data.get("used"):
        return jsonify(standard_response(False, "Activation key already used"))

    user_ref = db.collection("users").document(username)
    if user_ref.get().exists:
        return jsonify(standard_response(False, "User already exists"))

    expiry = get_timestamp_after_days(key_data.get("valid_days", 30))
    user_ref.set({
        "username": username,
        "password": password,
        "expires_at": expiry.isoformat()
    })

    key_ref.update({"used": True})
    return jsonify(standard_response(True, "Signup successful", {"expires_at": expiry.isoformat()}))


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return jsonify(standard_response(False, "User not found"))

    user_data = user_doc.to_dict()

    if user_data["password"] != password:
        return jsonify(standard_response(False, "Incorrect password"))

    if current_timestamp() > datetime.fromisoformat(user_data["expires_at"]):
        return jsonify(standard_response(False, "Account expired"))

    return jsonify(standard_response(True, "Login successful", {"username": username}))
