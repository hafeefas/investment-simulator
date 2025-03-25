from dotenv import load_dotenv
import os
from firebase_admin import credentials, initialize_app

# Load environment variables
load_dotenv()

# Use environment variables dynamically
key_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")  # Path to the JSON key
api_key = os.getenv("FIREBASE_CREDENTIALS")    # Firebase API key

# Initialize Firebase with the service account key
cred = credentials.Certificate(key_path)
initialize_app(cred) 