from flask import jsonify
from datetime import datetime, timezone

from srv.firebase.userManager import get_user_by_uuid, update_user_field
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
    if secs > 0 or not parts:  # Always show seconds if it's the only unit
        parts.append(f"{secs}s")

    return " ".join(parts)


def getWalletInfo(uuid):
    user_data = get_user_by_uuid(uuid)
    if not user_data:
        return jsonify(standard_response(False, "User not found")), 404

    solana_data = user_data.get("solana", {})
    public_key = solana_data.get("publicKey", None)
    private_key = solana_data.get("privateKey", None)  # hide if needed
    username = user_data.get("username", "Unknown")

    if not public_key:
        return jsonify(standard_response(False, "Public key not found for user")), 400

    current_balance = SolanaHelper.get_balance(public_key)
    sol_price_usd = get_sol_price_usd()
    netMode = SolanaHelper.getMode()

    # Get previous balance and check time if they exist
    prev_balance = solana_data.get("last_balance")
    prev_checked_at_str = solana_data.get("last_checked_at")

    percentage_change = None
    time_elapsed = None
    time_elapsed_human = None

    if prev_balance is not None:
        try:
            if prev_balance != 0:
                percentage_change = ((current_balance - prev_balance) / prev_balance) * 100
            else:
                percentage_change = 100.0
        except Exception as e:
            print("Error calculating % change:", e)

    if prev_checked_at_str:
        try:
            prev_time = datetime.fromisoformat(prev_checked_at_str)
            now_time = datetime.now(timezone.utc)
            time_elapsed = (now_time - prev_time).total_seconds()
            time_elapsed_human = format_time_elapsed(time_elapsed)
        except Exception as e:
            print("Error calculating time difference:", e)

    # Update Firestore fields (create them if missing)
    update_user_field(uuid, {
        "solana.last_balance": current_balance,
        "solana.last_checked_at": datetime.now(timezone.utc).isoformat()
    })

    response_data = {
        "wallet_public_key": public_key,
        "wallet_private_key": private_key,
        "username": username,
        "balance": round(current_balance, 4),
        "solPriceUSD": round(sol_price_usd, 2),
        "net": netMode,
        "percent_change": round(percentage_change, 2) if percentage_change is not None else None,
        "time_elapsed_seconds": int(time_elapsed) if time_elapsed is not None else None,
        "time_elapsed_readable": time_elapsed_human
    }

    return jsonify(standard_response(True, "Wallet info fetched", response_data))
