from flask import Blueprint, request
from srv.auth.authDecorator import require_auth

from srv.protectedFetch.walletInfoHandler import getWalletInfo  # adjust path if different

protected_bp = Blueprint("protected", __name__)


@protected_bp.route("/get_wallet_info", methods=["GET"])
@require_auth
def get_wallet_info_route(uuid):
    return getWalletInfo(uuid)
