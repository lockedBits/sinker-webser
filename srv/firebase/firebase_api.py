import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from dotenv import load_dotenv

load_dotenv()

firebase_config = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()
