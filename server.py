from flask import Flask
from firebase_admin import credentials, firestore, initialize_app
import json, os

from app.routes.auth import auth_bp

app = Flask(__name__)

# Firebase setup
firebase_config = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(firebase_config)
initialize_app(cred)
db = firestore.client()

import app
app.db = db

# Register Routes
app.register_blueprint(auth_bp, url_prefix="/api/auth")

@app.route("/")
def index():
    return {"status": "success", "message": "Server running"}

if __name__ == "__main__":
    app.run(debug=True)
