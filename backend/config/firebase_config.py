from firebase_admin import credentials, initialize_app

# Initialize Firebase with the service account key file
cred = credentials.Certificate("../firebase/serviceAccountKey.json")

# Initialize Firebase with the credentials
initialize_app(cred) 