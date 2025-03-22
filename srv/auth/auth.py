from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from srv.firebase.firebase_api import db
from srv.utils.helpers import generate_uuid, get_timestamp_after_days, current_timestamp, standard_response

from srv.session.sessionManager import *

from srv.sol.solanaHelper import SolanaHelper

def generate_unique_uuid():
    while True:
        new_uuid = str(generate_uuid())
        existing = db.collection("users").where("uuid", "==", new_uuid).stream()
        if not any(existing):
            return new_uuid


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    activation_key = data.get('activation_key')

    if not email or not password or not activation_key:
        return jsonify(standard_response(False, "Missing fields"))

    try:
        # Check if user already exists
        existing_user = auth.get_user_by_email(email)
        user_uuid = existing_user.uid
        user_doc = db.collection('users').document(user_uuid).get()
        
        # Check if account already activated (top-up mode)
        if user_doc.exists:
            user_data = user_doc.to_dict()
            key_ref = db.collection('activation_keys').document(activation_key)
            key_doc = key_ref.get()

            if not key_doc.exists:
                return jsonify(standard_response(False, "Invalid activation key"))

            key_data = key_doc.to_dict()
            duration_days = key_data.get("duration_days", 30)

            current_expiry = user_data.get("expires_at")
            current_expiry = datetime.fromisoformat(current_expiry) if current_expiry else datetime.utcnow()

            if current_expiry < datetime.utcnow():
                current_expiry = datetime.utcnow()

            new_expiry = current_expiry + timedelta(days=duration_days)

            # Update user expiry
            db.collection('users').document(user_uuid).update({
                "expires_at": new_expiry.isoformat(),
                "activation_history": firestore.ArrayUnion([{
                    "key": activation_key,
                    "used_at": datetime.utcnow().isoformat(),
                    "duration_days": duration_days
                }])
            })

            key_ref.delete()

            return jsonify(standard_response(True, "Account topped up successfully", {
                "expires_at": new_expiry.isoformat(),
                "uuid": user_uuid
            }))

        else:
            return jsonify(standard_response(False, "Account already exists but no user record found"))  # should not happen

    except auth.UserNotFoundError:
        pass  # continue with signup flow

    # New signup flow
    try:
        key_ref = db.collection('activation_keys').document(activation_key)
        key_doc = key_ref.get()

        if not key_doc.exists:
            return jsonify(standard_response(False, "Invalid activation key"))

        key_data = key_doc.to_dict()
        duration_days = key_data.get("duration_days", 30)
        new_expiry = datetime.utcnow() + timedelta(days=duration_days)

        # Create Firebase Auth User
        user = auth.create_user(email=email, password=password)
        unique_uuid = user.uid

        # Generate Solana Wallet
        wallet = SolanaHelper.generate_wallet()
        if not wallet:
            return jsonify(standard_response(False, "Failed to generate wallet"))

        # Store user in Firestore
        db.collection('users').document(unique_uuid).set({
            "email": email,
            "expires_at": new_expiry.isoformat(),
            "activation_history": [{
                "key": activation_key,
                "used_at": datetime.utcnow().isoformat(),
                "duration_days": duration_days
            }],
            "solana": {
                "privateKey": wallet["private_key"],
                "publicKey": wallet["public_key"]
            },
            "session": {
                "active_token": None,
                "created_at": None,
                "token_history": []
            },
            "coins": 0
        })

        # Delete the activation key
        key_ref.delete()

        # Generate a session token
        token = create_session_token(unique_uuid)

        return jsonify(standard_response(True, "Signup successful", {
            "expires_at": new_expiry.isoformat(),
            "token": token,
            "uuid": unique_uuid
        }))

    except Exception as e:
        return jsonify(standard_response(False, f"Signup failed: {str(e)}"))


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

def logout(request):
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify(standard_response(False, "Missing token"))

    uuid = validate_session_token(token)

    if not uuid:
        return jsonify(standard_response(False, "Invalid or expired session"))

    invalidate_user_session(uuid)
    return jsonify(standard_response(True, "Logout successful"))


def validate_token(request):
    data = request.get_json()
    token = data.get("token")
    if not token:
        return jsonify(standard_response(False, "Missing token"))

    uuid = validate_session_token(token)
    if not uuid:
        return jsonify(standard_response(False, "Invalid or expired session"))

    return jsonify(standard_response(True, "Token valid", {"uuid": uuid}))
