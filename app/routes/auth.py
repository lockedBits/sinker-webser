from flask import Blueprint, request
from app.services.auth_service import signup_user, login_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    return signup_user(data)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    return login_user(data)
