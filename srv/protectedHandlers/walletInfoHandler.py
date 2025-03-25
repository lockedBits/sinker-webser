from flask import jsonify
from datetime import datetime, timezone

from srv.firebase.userManager import get_user_by_uuid, update_user_nested_field
from srv.sol.solanaHelper import SolanaHelper
from srv.utils.solUtils import get_sol_price_usd
from srv.utils.helpers import standard_response


def format_time_elapsed(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def getWalletInfo(uuid):
    user_data = get_user_by_uuid(uuid)
    if not user_data:
        return jsonify(standard_response(False, "User not found")), 404

    solana_data = user_data.get("solana", {})
    public_key = solana_data.get("publicKey")
    private_key = solana_data.get("privateKey")  # Hide in production
    username = user_data.get("username", "Unknown")

    if not public_key:
        return jsonify(standard_response(False, "Public key not found for user")), 400

    current_balance = SolanaHelper.get_balance(public_key)
    sol_price_usd = get_sol_price_usd()
    netMode = SolanaHelper.getMode()

    # Historical info
    prev_balance = solana_data.get("last_balance_value")
    prev_checked_at_str = solana_data.get("last_balance_check")

    percent_change = None
    time_elapsed_readable = None

    if prev_balance is not None and prev_balance > 0:
        try:
            percent_change = round(((current_balance - prev_balance) / prev_balance) * 100, 2)
        except Exception as e:
            print("Error calculating percent change:", e)

    if prev_checked_at_str:
        try:
            prev_time = datetime.fromisoformat(prev_checked_at_str)
            now = datetime.now(timezone.utc)
            seconds_elapsed = (now - prev_time).total_seconds()
            time_elapsed_readable = format_time_elapsed(seconds_elapsed)
        except Exception as e:
            print("Error calculating time elapsed:", e)

    update_user_nested_field(uuid, {
        "solana.last_balance_value": float(current_balance),  # Explicitly force float
        "solana.last_balance_check": datetime.now(timezone.utc).isoformat()
    })


    response_data = {
        "wallet_public_key": public_key,
        "wallet_private_key": private_key,
        "username": username,
        "balance": round(current_balance, 4),
        "solPriceUSD": round(sol_price_usd, 2),
        "net": netMode
    }

    if percent_change is not None:
        response_data["percent_change"] = percent_change
    else:
        response_data["percent_change"] = 0


    if time_elapsed_readable:
        response_data["time_elapsed_readable"] = time_elapsed_readable
    else:
        response_data["time_elapsed_readable"] = "0s"

    return jsonify(standard_response(True, "Wallet info fetched", response_data))
