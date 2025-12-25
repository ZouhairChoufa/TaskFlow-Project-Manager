import firebase_admin
from firebase_admin import credentials, firestore
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Return None if no credentials found
            print("Warning: Firebase credentials not found. Some features may not work.")
            return None
    
    return firestore.client()

# Initialize Firestore client
db = None

def get_firestore_client():
    """Get Firestore client"""
    global db
    if db is None:
        db = initialize_firebase()
    return db