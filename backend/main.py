from fastapi import FastAPI
from routes import auth, stocks
from dotenv import load_dotenv
from fastapi.responses import JSONResponse


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

@app.route('/api/protected', methods=['GET'])
def protected(): #this is a protected route, it's a route that requires a token to access
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Missing token'}), 401

    try:
        # Verify the token
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        #Now you can use the users UID to grab user data from Firestore
        # user = firestore.get_user(uid)
        return JSONResponse({'message': 'You have access!', 'uid': uid}), 200
    except auth.InvalidIdTokenError:
        return JSONResponse({'message': 'Invalid token'}), 403

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
