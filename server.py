from flask import Flask
from app.services.firebase_service import init_firebase
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp

app = Flask(__name__)

# Initialize Firebase
init_firebase()

# Register Routes
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(admin_bp, url_prefix="/admin")

@app.route("/")
def index():
    return {"status": "Server is running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
