from fastapi import FastAPI, APIRouter, HTTPException, Depends
from services.stock_service import get_multiple_stocks_data, get_stocks_data
from typing import Dict
import yfinance as yf

router = APIRouter()

@router.get("/stocks", response_model=Dict)
async def get_stocks(stock_symbols: list[str]):
    try:
        stock_data = get_stocks_data(stock_symbols)
        return stock_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/stocks/{symbol}", response_model=Dict)
async def get_stocks_data(symbol: str):
    try:    
        stock_data = get_multiple_stocks_data(symbol)
        return stock_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-stock")
async def search(symbol: str):
   try:
       stock = yf.Ticker(symbol)
       stock_info = stock.info
       print(f"Debug - Retrieved stock info for {symbol}")  # Debug print
       
       return {
            "symbol": stock_info.get("symbol"),          # e.g., "AAPL"
            "name": stock_info.get("shortName"),         # e.g., "Apple Inc."
            "currentPrice": stock_info.get("currentPrice"),  # e.g., 188.38
            "marketCap": stock_info.get("marketCap"),    # Company's market value
            "volume": stock_info.get("regularMarketVolume"),  # Trading volume
            "sector": stock_info.get("sector"),          # e.g., "Technology"
            "industry": stock_info.get("industry"),      # e.g., "Consumer Electronics"
            "dayHigh": stock_info.get("dayHigh"),        # Today's high
            "dayLow": stock_info.get("dayLow"),          # Today's low
            "previousClose": stock_info.get("previousClose")  # Previous day's close
       }
   except Exception as e:
       print(f"Error fetching stock data: {str(e)}")  # Debug print
       raise HTTPException(status_code=500, detail=str(e))