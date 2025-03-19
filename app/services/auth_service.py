import uuid
from flask import jsonify
from datetime import datetime
from solders.keypair import Keypair
import base58
from app.utils.helpers import success_response, error_response
from app import db

def signup_user(data):
    activation_key = data.get("activation_key")
    username = data.get("username")
    password = data.get("password")

    if not activation_key or not username or not password:
        return error_response("Missing required fields", 400)

    key_ref = db.collection("activation_keys").document(activation_key)
    key_doc = key_ref.get()

    if not key_doc.exists:
        return error_response("Invalid activation key", 400)

    key_data = key_doc.to_dict()
    access_valid_until = key_data.get("valid_until")

    if not access_valid_until or datetime.utcnow() > access_valid_until:
        return error_response("Activation key has expired", 403)

    user_uuid = str(uuid.uuid4())
    wallet = Keypair()
    public_key = str(wallet.pubkey())
    private_key = base58.b58encode(wallet.to_bytes()).decode("utf-8")

    user_ref = db.collection("users").document(username)

    user_ref.set({
        "uuid": user_uuid,
        "username": username,
        "password": password,
        "public_key": public_key,
        "private_key": private_key,
        "access_valid_until": access_valid_until
    })

    key_ref.delete()

    return success_response({
        "uuid": user_uuid,
        "username": username,
        "public_key": public_key
    }, "Signup successful")


def login_user(data):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return error_response("Missing username or password", 400)

    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return error_response("Invalid username or password", 401)

    user_data = user_doc.to_dict()

    if user_data.get("password") != password:
        return error_response("Invalid username or password", 401)

    access_valid_until = user_data.get("access_valid_until")
    if access_valid_until and datetime.utcnow() > access_valid_until:
        return error_response("Account access expired. Please activate again.", 403)

    return success_response({
        "uuid": user_data["uuid"],
        "username": user_data["username"],
        "public_key": user_data["public_key"]
    }, "Login successful")
