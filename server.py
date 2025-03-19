from flask import Flask
from firebase_admin import credentials, firestore, initialize_app
import json, os

# ✅ Import blueprint
from app.routes.auth import auth_bp

# ✅ Avoid naming conflict: give a new name to Flask app instance
flask_app = Flask(__name__)

# ✅ Setup Firebase
firebase_config = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(firebase_config)
initialize_app(cred)
firestore_db = firestore.client()

# ✅ Assign Firestore DB globally via app package
import app  # this is the `app/` folder
app.db = firestore_db

# ✅ Register blueprint properly
flask_app.register_blueprint(auth_bp, url_prefix="/api/auth")

# ✅ Sample route
@flask_app.route("/")
def index():
    return {"status": "success", "message": "Server is running!"}

# ✅ Run Flask app
if __name__ == "__main__":
    flask_app.run(debug=True)
