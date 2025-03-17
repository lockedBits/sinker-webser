import os
import json
import base58
import uuid
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
    password = data.get("password")
    
    if not activation_key or not username or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if activation key exists
    key_ref = db.collection("activation_keys").document(activation_key)
    key_doc = key_ref.get()
    
    if not key_doc.exists:
        return jsonify({"error": "Invalid activation key"}), 400

    # Generate UUID for the user
    user_uuid = str(uuid.uuid4())

    # Create a Solana wallet
    wallet = Keypair()
    public_key = str(wallet.pubkey())
    private_key = base58.b58encode(wallet.to_bytes()).decode("utf-8")

    # Store user details in Firebase
    user_ref = db.collection("users").document(username)
    
    try:
        user_ref.set({
            "uuid": user_uuid,
            "username": username,
            "password": password,
            "public_key": public_key,
            "private_key": private_key
        })
        
        # Delete activation key only after successful user creation
        key_ref.delete()

        return jsonify({
            "message": "Signup successful",
            "uuid": user_uuid,
            "username": username,
            "public_key": public_key
        })
    except Exception as e:
        return jsonify({"error": "Failed to create user", "details": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        return jsonify({"error": "Invalid username or password"}), 401
    
    user_data = user_doc.to_dict()
    
    if user_data["password"] != password:
        return jsonify({"error": "Invalid username or password"}), 401
    
    return jsonify({
        "message": "Login successful",
        "username": user_data["username"],
        "uuid": user_data["uuid"],
        "public_key": user_data["public_key"]
    })

if __name__ == "__main__":
    app.run(debug=True)
