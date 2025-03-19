import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

db = None

def init_firebase():
    global db
    config = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
    cred = credentials.Certificate(config)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

def get_db():
    return db
