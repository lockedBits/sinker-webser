# srv/firebase/user_manager.py

from srv.firebase.firebase_api import db

def get_user_by_uuid(uuid):
    try:
        doc_ref = db.collection("users").document(uuid)
        user_doc = doc_ref.get()
        if not user_doc.exists:
            return None
        return user_doc.to_dict()
    except Exception as e:
        print(f"[user_manager] Error fetching user by UUID: {e}")
        return None
        
def update_user_field(uuid, field, value):
    db.collection("users").document(uuid).set({field: value}, merge=True)
