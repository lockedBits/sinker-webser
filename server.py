# server.py
from flask import Flask
from app.routes.auth import auth_bp
from app import init_firebase

app = Flask(__name__)
init_firebase()  # ← Initialize Firebase

app.register_blueprint(auth_bp, url_prefix="/api/auth")

if __name__ == "__main__":
    app.run(debug=True)
