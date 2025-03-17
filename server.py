import os
import json
import base58
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from solders.keypair import Keypair

app = Flask(__name__)

# Load Firebase credentials from environment variables
firebase_config = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    activation_key = data.get("activation_key")
    username = data.get("username")

    if not activation_key or not username:
        return jsonify({"error": "Missing activation key or username"}), 400

    # Check if activation key exists
    key_ref = db.collection("activation_keys").document(activation_key)
    key_doc = key_ref.get()
    
    if not key_doc.exists:
        return jsonify({"error": "Invalid activation key"}), 400

    # Create a Solana wallet
    wallet = Keypair()
    public_key = str(wallet.pubkey())
    private_key = base58.b58encode(wallet.to_bytes()).decode("utf-8")  # 🔥 FIXED 🔥

    # Store user details in Firebase
    user_ref = db.collection("users").document(username)
    
    try:
        user_ref.set({
            "username": username,
            "public_key": public_key,
            "private_key": private_key
        })
        
        # 🔥 Delete activation key only after user is created successfully
        key_ref.delete()

        return jsonify({
            "message": "Signup successful",
            "username": username,
            "public_key": public_key
        })

    except Exception as e:
        return jsonify({"error": "Failed to create user", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
