from fastapi import FastAPI, Depends, HTTPException, Header, WebSocket
from routes import auth, stocks
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from firebase_admin import auth as firebase_auth
import asyncio
import yfinance as yf
from datetime import datetime
from routes.auth import verify_token
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

# Root route
@app.get("/")
async def root():
    return {"message": "Welcome to InvestSim API"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])

# WebSocket is a protocol that provides full-duplex communication between client and server
# Unlike HTTP, which is request-response based, WebSocket maintains an open connection
# This allows us to send real-time updates from server to client without the client having to request it
# used for REAL TIME DATA and STOCK UPDATES

# Store all active WebSocket connections in a list
# This helps us manage multiple clients connected at the same time
active_connections = []

@app.websocket("/ws/stock-updates/{symbol}")
async def stock_updates(websocket: WebSocket, symbol: str):
    # Accept the WebSocket connection from the client
    await websocket.accept()
    # Add this connection to our list of active connections
    active_connections.append(websocket)
    
    try:
        # Infinite loop to keep sending updates
        # This runs continuously until the client disconnects
        while True:
            # Get real-time stock data using yfinance
            # yfinance makes an API call to Yahoo Finance
            stock = yf.Ticker(symbol)
            stock_info = stock.info
            
            # Send a JSON message to the connected client
            # websocket.send_json automatically converts Python dict to JSON
            await websocket.send_json({
                "symbol": symbol,                                  # Stock symbol (e.g., AAPL)
                "price": stock_info.get("currentPrice"),          # Current stock price
                "timestamp": datetime.now().isoformat(),          # When this update was sent
                "volume": stock_info.get("regularMarketVolume"),  # Trading volume
                "dayHigh": stock_info.get("dayHigh"),            # Highest price today
                "dayLow": stock_info.get("dayLow")               # Lowest price today
            })
            
            # Pause for 6 seconds before sending next update
            # This prevents overwhelming the Yahoo Finance API
            # and reduces unnecessary updates
            await asyncio.sleep(6)
            
    except Exception as e:
        # Handle any errors that occur during the WebSocket connection
        print(f"Error in WebSocket: {str(e)}")
    finally:
        # When connection closes (either due to client disconnecting or error):
        # 1. Remove this connection from our active connections list
        # 2. Close the WebSocket connection properly
        active_connections.remove(websocket)
        await websocket.close()

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
