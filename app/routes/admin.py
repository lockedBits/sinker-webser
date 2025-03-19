
from flask import Blueprint, request, jsonify
from app.services.key_service import create_activation_key, list_keys

admin_bp = Blueprint("admin", __name__)

def check_admin(auth):
    return auth == config = json.loads(os.getenv("ADMIN_SECRET"))

@admin_bp.route("/create-key", methods=["POST"])
def create_key():
    auth = request.headers.get("Authorization")
    if not check_admin(auth):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    duration = data.get("duration_days", 30)
    key = create_activation_key(duration)
    return jsonify({"message": "Key created", "key": key})

@admin_bp.route("/list-keys", methods=["GET"])
def list_all_keys():
    auth = request.headers.get("Authorization")
    if not check_admin(auth):
        return jsonify({"error": "Unauthorized"}), 403

    keys = list_keys()
    return jsonify({"keys": keys})
