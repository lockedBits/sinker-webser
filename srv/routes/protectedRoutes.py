from flask import Blueprint, request
from srv.auth.auth_decorators import require_auth

from srv.protectedFetchHandler import get_wallet_info_handler  # adjust path if different

protected_bp = Blueprint("protected", __name__)


@protected_bp.route("/get_wallet_info", methods=["GET"])
@require_auth
def get_wallet_info_route(uuid):
    return get_wallet_info_handler(uuid)
