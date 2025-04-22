import yfinance as yf
from pydantic import BaseModel
from services.firebase_service import get_db
from routes.auth import verify_token
from datetime import datetime
from fastapi import HTTPException

def get_multiple_stocks_data(stock_symbol):
    # Fetch stock data using yfinance
    try:
        stock = yf.Ticker(stock_symbol)
        data = stock.history(interval="1mo", start="2024-01-01", end="2024-01-31")
        return data
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {e}")
        return None

class StockData(BaseModel):
    stock_symbol: str
    stock_data: dict

def get_stocks_data(stock_symbols: str):
    try:
        print(f"Attempting to fetch data for symbol: {stock_symbols}")
        # Get the stock info
        stock = yf.Ticker(stock_symbols)
        info = stock.info
        
        if not info:
            print(f"No data found for symbol {stock_symbols}")
            raise HTTPException(status_code=404, detail=f"No data found for symbol {stock_symbols}")
            
        # Extract the data we want
        stock_data = {
            "symbol": stock_symbols,
            "price": info.get("currentPrice"),
            "change": info.get("regularMarketChange"),
            "changePercent": info.get("regularMarketChangePercent"),
            "open": info.get("regularMarketOpen"),
            "high": info.get("regularMarketDayHigh"),
            "low": info.get("regularMarketDayLow"),
            "volume": info.get("regularMarketVolume"),
            "marketCap": info.get("marketCap"),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"Debug - Stock data: {stock_data}")
        return stock_data
    
    except Exception as e:
        print(f"Error fetching stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")

async def buy_stock(user_id: str, stock_symbol: str, quantity: int, price: float):
    """
    Function to handle stock purchase. Takes user_id, stock symbol, quantity, and price as parameters.
    Returns success/failure and updates user's portfolio in Firestore.
    """
    try:
        # Initialize Firestore database connection from firebase_service.py
        db = get_db()
        
        # Get user document from Firestore using user_id
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get current user data
        user_data = user_doc.to_dict()
        
        # Calculate total cost of purchase
        total_cost = quantity * price
        
        # Check if user has enough balance
        if user_data['initial_balance'] < total_cost:
            raise HTTPException(
                status_code=400, 
                detail="Insufficient funds for purchase"
            )
        
        # Get current portfolio or create empty one if doesn't exist
        portfolio = user_data.get('portfolio', {})
        
        # Update or create stock position in portfolio
        if stock_symbol in portfolio:
            # If user already owns this stock, update quantity and average price
            current_quantity = portfolio[stock_symbol]['quantity']
            current_avg_price = portfolio[stock_symbol]['average_buy_price']
            
            # Calculate new average price
            new_total_quantity = current_quantity + quantity
            new_avg_price = ((current_quantity * current_avg_price) + (quantity * price)) / new_total_quantity
            
            portfolio[stock_symbol] = {
                'quantity': new_total_quantity,
                'average_buy_price': new_avg_price,
                'last_updated': datetime.now().isoformat()
            }
        else:
            # If this is a new stock position
            portfolio[stock_symbol] = {
                'quantity': quantity,
                'average_buy_price': price,
                'last_updated': datetime.now().isoformat()
            }
        
        # Create transaction record
        transaction = {
            'type': 'BUY',
            'symbol': stock_symbol,
            'quantity': quantity,
            'price': price,
            'total_cost': total_cost,
            'timestamp': datetime.now().isoformat()
        }
        
        # Update user document in Firestore
        user_ref.update({
            'initial_balance': user_data['initial_balance'] - total_cost,  # Subtract cost from balance
            'portfolio': portfolio,  # Update portfolio
            'transactions': firestore.ArrayUnion([transaction])  # Add new transaction to history
        })
        
        return {
            'status': 'success',
            'message': f'Successfully purchased {quantity} shares of {stock_symbol}',
            'transaction': transaction,
            'new_balance': user_data['initial_balance'] - total_cost
        }
        
    except HTTPException as http_error:
        # Re-raise HTTP exceptions
        raise http_error
    except Exception as e:
        # Handle any other errors
        print(f"Error in buy_stock: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing purchase: {str(e)}")

async def sell_stock(user_id: str, stock_symbol: str, quantity: int, price: float):
    """
    Function to handle stock sale. Takes user_id, stock symbol, quantity, and price as parameters.
    Returns success/failure and updates user's portfolio in Firestore. first checks if the user has enough stock to sell.
    """
    try:
        db = get_db()

        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        user_data = user_doc.to_dict() #to_dict -> converts the firestore document to a dictionary
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        #get current portfolio
        portfolio = user_data.get("portfolio", {})
        if stock_symbol not in portfolio:
            raise HTTPException(status_code=400, detail="Stock not found in portfolio")

        #check if user has enough stock to sell
        current_quanitity = portfolio[stock_symbol]["quantity"]
        if current_quanitity < quantity: #quantity came from the buy stock function
            raise HTTPException(status_code=400, detail="Insufficient stock quantity")
        
        #calculate the total sale amount
        stock = yf.Ticker(stock_symbol)
        stock_info = stock.info
        current_price = stock_info("currentPrice")
        total_sale_amount = quantity * current_price

        avg_buy_price = portfolio[stock_symbol]["average_buy_price"]
        profit_loss = (current_price - avg_buy_price) * quantity
        profit_loss_percentage = ((current_price - avg_buy_price) / avg_buy_price) * 100

        #update the user's balance
        user_ref.update({
            "initial_balance": user_data["initial_balance"] + total_sale_amount,
            "profit_loss": profit_loss,
            "profit_loss_percentage": profit_loss_percentage
        })

        #update the user's portfolio
        portfolio[stock_symbol]["quantity"] -= quantity 
        #^^ shorthand for portfolio[stock_symbol]["quantity"] = portfolio[stock_symbol]["quantity"] - quantity
        if portfolio[stock_symbol]["quantity"] == 0:
            del portfolio[stock_symbol]
            
        #create the transaction record. transaction is from user.py in the user model
        transaction = {
            "type": "SELL",
            "symbol": stock_symbol,
            "quantity": quantity,
            "price": current_price,
            "total_sale_amount": total_sale_amount,
            "timestamp": datetime.now().isoformat()
        }
        
        #update user document in firestore
        user_ref.update({
            "portfolio": portfolio,
            "transactions": firestore.ArrayUnion([transaction])
        })
        
        return {
            'status': 'success',
            'message': f'Successfully sold {quantity} shares of {stock_symbol}',
            'transaction': transaction,
            'new_balance': user_data['initial_balance'] + total_sale_amount
        }
        
    except HTTPException as http_error:
        # Re-raise HTTP exceptions
        raise http_error
    except Exception as e:
        # Handle any other errors
        print(f"Error in sell_stock: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing sale: {str(e)}")


''' Notes
    # read data
    # user_doc = db.collection("users").document(user_id).get()
    # user_data = user_doc.to_dict()

    # # Write data
    # db.collection("users").document(user_id).set(data)

    # # Update data
    # db.collection("users").document(user_id).update({"field": "new_value"})

# User document in Firestore looks like this:
{
    "initial_balance": 500000.0,
    "portfolio": {
        "AAPL": {                    # Stock symbol as key
            "quantity": 10,          # Number of shares owned
            "average_buy_price": 185.50,
            "last_updated": "2024-03-20"
        },
        "GOOGL": {
            "quantity": 5,
            "average_buy_price": 140.25,
            "last_updated": "2024-03-20"
        }
    }

sell function notes
# If a user owns 10 shares of AAPL and sells 3:
portfolio = {
    "AAPL": {
        "quantity": 10,  # Current shares owned
        # ... other data ...
    }
}

quantity = 3  # Selling 3 shares
portfolio["AAPL"]["quantity"] -= quantity  # Now quantity becomes 7
'''

# print(get_stocks_data(["AAPL", "MSFT", "SPX", "^GSPC", "NVDA", "META"]))