import firebase_admin
from firebase_admin import credentials, firestore
import os
from pathlib import Path

# We need to find where our serviceAccountKey.json is located
# __file__ is this file's location
# .resolve() gets the absolute path
# .parent.parent goes up two directories (from services/ to backend/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Join the paths to get the full path to our service account key
# This will create: backend/firebase/serviceAccountKey.json
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "firebase", "serviceAccountKey.json")

# Function to set up Firebase when our app starts
def init_firebase():
    try:
        # Firebase can only be initialized once
        # _apps is a list of initialized Firebase apps
        if not firebase_admin._apps:
            # Create credentials using our service account key
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            # Initialize Firebase with these credentials
            firebase_admin.initialize_app(cred)
            print(f"Firebase connected successfully using {SERVICE_ACCOUNT_PATH}")
        else:
            # If Firebase is already running, just let us know
            print("Firebase already initialized")

    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise e

# Function to get the Firestore database client
def get_db():
    # Make sure Firebase is initialized before getting the database
    if not firebase_admin._apps:
        init_firebase()
    # Return the database client for Firestore operations
    return firestore.client()

# When this file is imported, initialize Firebase right away
init_firebase()
