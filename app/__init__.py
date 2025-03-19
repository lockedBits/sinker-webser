# app/__init__.py
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

db = None  # ← Global Firestore client

def init_firebase():
    global db
    if not firebase_admin._apps:
        # Load Firebase credentials from environment variable
        firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")
        if not firebase_credentials_json:
            raise Exception("FIREBASE_CREDENTIALS not set in environment variables")

        cred = credentials.Certificate(json.loads(firebase_credentials_json))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
