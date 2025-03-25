from flask import jsonify
from datetime import datetime, timezone

from srv.firebase.userManager import update_user_nested_field, get_user_by_uuid
from srv.sol.solanaHelper import SolanaHelper
from srv.utils.helpers import standard_response


def handle_send_sol(uuid, data):
    try:
        # Extract & Validate input
        from_private_key = data.get("from_private_key")
        to_public_key = data.get("to_public_key")
        amount_sol = data.get("amount_sol")

        if not from_private_key or not to_public_key or amount_sol is None:
            return jsonify(standard_response(False, "Missing required parameters")), 400

        # Ensure amount is valid
        if amount_sol <= 0:
            return jsonify(standard_response(False, "Invalid transaction amount")), 400

        # Get user info
        user_data = get_user_by_uuid(uuid)
        if not user_data:
            return jsonify(standard_response(False, "User not found")), 404

        # Send SOL using SolanaHelper
        send_result = SolanaHelper.send_sol(from_private_key, to_public_key, amount_sol)
        if not send_result["success"]:
            return jsonify(standard_response(False, "Transaction failed", send_result.get("error", "Unknown error"))), 400

        # Ensure transaction signature exists
        signature = send_result.get("signature")
        if not signature:
            return jsonify(standard_response(False, "Transaction failed - No signature returned")), 400

        # Prepare transaction log
        transaction_log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "to": to_public_key,
            "amount_sol": amount_sol,
            "signature": signature
        }

        # Update Firestore transaction history (append instead of overwrite)
        update_result = update_user_nested_field(uuid, {"transactions": transaction_log}, append=True)
        if not update_result["success"]:
            return jsonify(standard_response(False, "Failed to update transaction log", update_result.get("error", "Unknown error"))), 500

        return jsonify(standard_response(True, "Transaction successful", transaction_log))

    except Exception as e:
        return jsonify(standard_response(False, "Unexpected error", str(e))), 500
