# srv/routes/authRoutes.py
from flask import Blueprint, request
from srv.auth.auth import signup, login, logout

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup_route():
    return signup(request)

@auth_bp.route("/login", methods=["POST"])
def login_route():
    return login(request)

@auth_bp.route("/logout", methods=["POST"])
def logout_route():
    return logout(request)
