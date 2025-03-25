from datetime import datetime
from srv.sol.solanaHelper import SolanaHelper
from srv.firebase.userManager import get_user_by_uuid, update_user_nested_field

def handle_send_sol(uuid, data):
    recipient = data.get("recipient")
    amount = data.get("amount")

    if not recipient or not amount:
        return {"success": False, "message": "Missing required fields"}, 400

    user_data = get_user_by_uuid(uuid)
    solana_data = user_data.get("solana", {})  # Default to an empty dict if missing
    private_key = solana_data.get("privateKey")

    if not private_key:
        return {"success": False, "message": "Sender wallet private key not found"}, 400

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
