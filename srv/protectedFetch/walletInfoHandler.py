from flask import jsonify

from srv.firebase.userManager import get_user_by_uuid
from srv.sol.solanaHelper import SolanaHelper
from srv.utils.solUtils import get_sol_price_usd
from srv.utils.helpers import standard_response

def getWalletInfo(uuid):
    user_data = get_user_by_uuid(uuid)
    if not user_data:
        return jsonify(standard_response(False, "User not found")), 404

    public_key = user_data.get("solana").private_key
    private_key = user_data.get("solana").public_key  # hide if needed
    username = user_data.get("username", "Unknown")

    sol_balance = SolanaHelper.get_balance(public_key)
    sol_price_usd = get_sol_price_usd()

    return jsonify(standard_response(True, "Wallet info fetched", {
        "wallet_public_key": public_key,
        "wallet_private_key": private_key,
        "username": username,
        "balance": round(sol_balance, 4),
        "solPriceUSD": round(sol_price_usd, 2)
    }))
