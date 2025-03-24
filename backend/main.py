from dotenv import load_dotenv
import yfinance as yf  # For fetching stock data
import numpy as np  # For numerical computations
from sklearn.linear_model import LinearRegression  # For trend prediction
from textblob import TextBlob  # For sentiment analysis
from fastapi import FastAPI  # For creating the API
from pydantic import BaseModel  # For defining request models
import os
from firebase_admin import credentials, initialize_app

# Load environment variables
load_dotenv()
app = FastAPI()

# Use environment variables dynamically
key_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")  # Path to the JSON key
api_key = os.getenv("FIREBASE_CREDENTIALS")    # Firebase API key
# print("Key Path:", os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY"))  # Should print the path
# print("API Key:", os.getenv("FIREBASE_CREDENTIALS"))     # Should print the API key
# print("Key Path:", key_path)  # Check if it prints correctly
# print("API Key:", api_key)

# Initialize Firebase with the service account key
cred = credentials.Certificate(key_path)
initialize_app(cred)

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

def get_stocks_data(stock_symbols: list[str]):
    stock_data = {}
    for symbol in stock_symbols:
        data = get_multiple_stocks_data(symbol)
        if not data.empty:
            stock_data[symbol] = data
    return stock_data

print(get_stocks_data(["AAPL", "MSFT", "SPX", "^GSPC", "NVDA", "META"]))