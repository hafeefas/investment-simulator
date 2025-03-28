from fastapi import FastAPI, Depends, HTTPException, Header
from routes import auth, stocks
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from firebase_admin import auth as firebase_auth

# Load environment variables
load_dotenv()
app = FastAPI()

# Root route
@app.get("/")
async def root():
    return {"message": "Welcome to InvestSim API"}

# Include the routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])

async def verify_token(authorization: str = Header(...)):
    try:
        #firebase verifies the token and returns the decoded data
        # this will fail is the token is invalid or expired
        decoded_token = firebase_auth.verify_id_token(authorization)

        # if the token is valid, return the user's UID
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    # example of how to use the verify_token function in a protected route
@app.get("/protected-route")
async def protected_route(uid: str = Depends(verify_token)):
    return {"message": "You have access to this protected route", "uid": uid}
    # Depends(verify_token) means:
    # 1. Run verify_token first
    # 2. Pass the returned uid to this function
    # 3. If verify_token fails, this route won't run


    # Benefits of Depends over the below code:
    # Reusable - same verification for all protected routes
    # Cleaner - no repeated token verification code
    # Consistent - same error handling everywhere
    # FastAPI handles all the header extraction


# @app.route('/api/protected', methods=['GET'])
# def protected(): #this is a protected route, it's a route that requires a token to access
#     token = request.headers.get('Authorization')
#     if not token:
#         return jsonify({'message': 'Missing token'}), 401

#     try:
#         # Verify the token
#         decoded_token = auth.verify_id_token(token)
#         uid = decoded_token['uid']
#         #Now you can use the users UID to grab user data from Firestore
#         # user = firestore.get_user(uid)
#         return JSONResponse({'message': 'You have access!', 'uid': uid}), 200
#     except auth.InvalidIdTokenError:
#         return JSONResponse({'message': 'Invalid token'}), 403

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
