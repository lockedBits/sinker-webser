from flask import Flask
from flask_cors import CORS

from srv.auth.auth import auth_bp

app = Flask(__name__)
CORS(app)  # <-- This enables CORS globally
app.register_blueprint(auth_bp, url_prefix='/api/auth')

if __name__ == "__main__":
    app.run(debug=True)
