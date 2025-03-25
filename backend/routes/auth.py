# Import necessary FastAPI components for routing and error handling
from fastapi import APIRouter, HTTPException, Depends
# Import Firebase Admin SDK for authentication
from firebase_admin import auth
# Import our custom user models from the models directory
from models.user import UserCreate, User
# Import typing for type hints
from typing import Dict
# Import datetime for timestamp creation
from datetime import datetime
# Import services
from fastapi.responses import JSONResponse

# Create a router instance to group all authentication-related endpoints. it's a fastapi component that allows us to group related routes together
router = APIRouter()

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
        
        # TODO: Add Firestore document creation
        # This is where we'll store the user_data in Firestore
        
        # Return success message and user ID
        return {"message": "User created successfully", "uid": user_record.uid}
    except Exception as e:
        # If anything goes wrong, raise an HTTP exception
        # with status code 400 (Bad Request)
        raise HTTPException(status_code=400, detail=str(e))

# Define the signin endpoint
# POST /api/auth/signin
# Takes email and password as input and returns a dictionary
@router.post("/signin", response_model=Dict)
async def signin(email: str, password: str):
    try:
        # TODO: Implement Firebase sign in
        # This will be handled by Firebase Auth on the frontend
        # The frontend will use Firebase SDK to handle the actual authentication
        # and then send the token to our backend for verification
        
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
async def login_user(user: UserCreate):
    try:
        # Sign in with Firebase
        user_record = auth.get_user_by_email(user.email)
        # In a real application, you would verify the password here
        # and generate a custom token or session
        
        return JSONResponse({
            "message": "Login successful",
            "uid": user_record.uid
        })
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 