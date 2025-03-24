# auth_decorators.py

from functools import wraps
from flask import request, jsonify

from srv.session.sessionManager import validate_session_token
from srv.utils.helpers import standard_response

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify(standard_response(False, "Authorization token missing")), 401

        token = auth_header.split(" ")[1]
        uuid = validate_session_token(token)

        if not uuid:
            return jsonify(standard_response(False, "Invalid or expired session token")), 401

        return func(uuid=uuid, *args, **kwargs)

    return wrapper




#example
#this is how we use it
'''
from flask import Blueprint, jsonify
from firebase_config import db
from utils import standard_response

from auth_decorators import require_auth

protected_routes = Blueprint("protected_routes", __name__)

@protected_routes.route("/dashboard", methods=["GET"])
@require_auth
def dashboard(uuid):
    user_doc = db.collection("users").document(uuid).get()
    if not user_doc.exists:
        return jsonify(standard_response(False, "User not found"))

    user_data = user_doc.to_dict()
    return jsonify(standard_response(True, "Welcome to your dashboard", {
        "uuid": uuid,
        "coins": user_data.get("coins", 0),
        "expires_at": user_data.get("expires_at")
    }))
'''