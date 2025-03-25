from datetime import datetime
from srv.sol.solanaHelper import SolanaHelper
from srv.firebase.userManager import get_user_by_uuid, update_user_nested_field

def handle_send_sol(uuid, data):
    recipient = data.get("recipient")
    amount = data.get("amount")

    if not recipient or not amount:
        return {"success": False, "message": "Missing required fields"}, 400

    # Retrieve sender's private key from Firestore using UUID
    user_data = get_user_by_uuid(uuid)
    if not user_data or "wallet_private_key" not in user_data:
        return {"success": False, "message": "Sender wallet not found"}, 400

    private_key = user_data.get("solana", {}).get("last_balance_value")

    # Send SOL transaction
    result = SolanaHelper.send_sol(private_key, recipient, float(amount))

    if result.get("success"):
        # Log transaction in Firestore
        transaction_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "recipient": recipient,
            "amount": amount,
            "signature": result["signature"],
        }

        # Append transaction to Firestore using arrayUnion
        update_user_nested_field(uuid, {
            "transactions": db.ArrayUnion([transaction_log])
        })

    return result
