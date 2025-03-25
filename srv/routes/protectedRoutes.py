from flask import Blueprint, request
from srv.auth.authDecorator import require_auth

from srv.protectedHandlers.walletInfoHandler import getWalletInfo  # adjust path if different
from srv.protectedHandlers.sendSolHandler import handle_send_sol

protected_bp = Blueprint("protected", __name__)


@protected_bp.route("/get_wallet_info", methods=["GET"])
@require_auth
def get_wallet_info_route(uuid):
    return getWalletInfo(uuid)

@protected_bp.route("/send_sol", methods=["POST"])  # Change to POST
@require_auth
def send_sol_route(uuid):
    data = request.json  # Get request data
    return handle_send_sol(uuid, data)  # Pass uuid and request data