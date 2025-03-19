from flask import Flask
from auth import auth_bp

app = Flask(__name__)
app.register_blueprint(auth_bp, url_prefix='/api/auth')

if __name__ == "__main__":
    app.run(debug=True)
