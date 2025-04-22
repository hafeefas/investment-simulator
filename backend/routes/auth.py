# Import necessary FastAPI components for routing and error handling
from fastapi import APIRouter, HTTPException, Depends, Header
# Import Firebase Admin SDK for authentication
from firebase_admin import auth as firebase_auth
from firebase_admin import firestore
# Import our custom user models from the models directory
from models.user import UserCreate, User

from services.firebase_service import get_db, init_firebase
# Import typing for type hints
from typing import Dict
# Import datetime for timestamp creation
from datetime import datetime
# Import services
from fastapi.responses import JSONResponse

# Create a router instance to group all authentication-related endpoints. it's a fastapi component that allows us to group related routes together
router = APIRouter()


async def verify_token(authorization: str = Header(...)):
    try:
        #firebase verifies the token and returns the decoded data
        # this will fail is the token is invalid or expired
        decoded_token = auth.verify_id_token(authorization)

        # if the token is valid, return the user's UID
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


# Define the signup endpoint
# POST /api/auth/signup
# Takes a UserCreate model as input and returns a dictionary
@router.post("/signup", response_model=Dict) #the dictionary is the response model, the response_model will basically have an output that's a dictionary
async def signup(user: UserCreate): #user is the input model, it's a UserCreate model
    try:
        # Create a new user in Firebase Authentication
        # This will generate a unique user ID (uid)
        user_record = auth.create_user(
            email=user.email,
            password=user.password
        )


#  example return:
#    {
#        "message": "User created successfully",
#        "uid": user_record.uid
#    }
        
        # Prepare user data for Firestore
        # This will be the document structure in the database
        user_data = {
            "id": user_record.uid,  # Unique Firebase Auth ID
            "email": user.email,     # User's email address
            "initial_balance": user.initial_balance,  # Starting balance ($500)
            "portfolio": {},         # Empty portfolio for stocks
            "transactions": [],      # Empty list for transaction history
            "created_at": datetime.now()  # Timestamp of account creation
        }
        
        # This is where we'll store the user_data in Firestore
        # db = firestore.client() -> not needed because we already have get_db() in firebase_service.py 
        db = get_db()
        print("Database connection successful in signup route!")
        db.collection("users").document(user_record.uid).set(user_data)
        #   ^ collection is the name of the collection in the database
        #   ^ document is the name of the document in the collection which is user_record.uid since it's unique in the firebase auth
        #   ^ set is the function that we use to create the document
        #   ^ data is the data that we want to store in the document
        
        # Return success message and user ID
        return {"message": "User created successfully", "uid": user_record.uid}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Define the signin endpoint
# POST /api/auth/signin
# Takes email and password as input and returns a dictionary
@router.post("/signin", response_model=Dict)
async def signin(email: str, password: str):
    try:
        # Implemented Firebase sign in
        # This will be handled by Firebase Auth on the frontend
        # The frontend will use Firebase SDK to handle the actual authentication
        # and then send the token to our backend for verification
        user_record = auth.get_user_by_email(email)
        if not user_record:
            raise HTTPException(status_code=401, detail="Invalid username credentials")

        # Verify the password
        if not auth.verify_password(password, user_record.password): 
            raise HTTPException(status_code=401, detail="Invalid password credentials")

        # For now, just return a success message
        return {"message": "Sign in successful"}
    except Exception as e:
        # If authentication fails, raise an HTTP exception
        # with status code 401 (Unauthorized)
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register")
async def register_user(user: UserCreate):
    try:
        # Create user in Firebase
        user_record = auth.create_user(
            email=user.email,
            password=user.password
        )
        
        return JSONResponse({
            "message": "User created successfully",
            "uid": user_record.uid
        })
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login_user(
    user: UserCreate,
    authorization: str = Header(None)  # Optional header for token
):
    try:
        # If we have a token, verify it
        if authorization:
            decoded_token = auth.verify_id_token(authorization)
            return JSONResponse({
                "message": "Login successful",
                "uid": decoded_token['uid']
            })
        
        # If no token, try email/password (for testing in docs)
        user_record = auth.get_user_by_email(user.email)
        return JSONResponse({
            "message": "Login successful",
            "uid": user_record.uid
        })
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 