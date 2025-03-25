from flask import jsonify
from datetime import datetime, timezone

from srv.firebase.userManager import update_user_nested_field, get_user_by_uuid
from srv.sol.solanaHelper import SolanaHelper
from srv.utils.helpers import standard_response


def handle_send_sol(uuid, data):
    try:
        # Extract data
        from_private_key = data.get("from_private_key")
        to_public_key = data.get("to_public_key")
        amount_sol = data.get("amount_sol")

        # Validate input
        if not from_private_key or not to_public_key or amount_sol is None:
            return jsonify(standard_response(False, "Missing required parameters")), 400

        # Ensure amount_sol is a float
        try:
            amount_sol = float(amount_sol)
        except ValueError:
            return jsonify(standard_response(False, "Invalid amount format")), 400

        # Get user info
        user_data = get_user_by_uuid(uuid)
        if not user_data:
            return jsonify(standard_response(False, "User not found")), 404

        # Send SOL using SolanaHelper
        send_result = SolanaHelper.send_sol(from_private_key, to_public_key, amount_sol)
        
        if not send_result["success"]:
            return jsonify(standard_response(False, "Transaction failed", send_result["error"])), 400

        # Prepare transaction log
        transaction_log = {
            "to": to_public_key,
            "amount": amount_sol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signature": send_result.get("signature", "N/A")
        }

        # Update Firestore transaction history
        update_user_nested_field(uuid, {"solana.transactions": transaction_log})

        return jsonify(standard_response(True, "Transaction successful", transaction_log))
    
    except Exception as e:
        return jsonify(standard_response(False, f"Encountered an error: {str(e)}"))
