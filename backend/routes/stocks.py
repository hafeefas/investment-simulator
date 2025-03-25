from fastapi import FastAPI, APIRouter, HTTPException, Depends
from services.stock_service import get_multiple_stocks_data, get_stocks_data
from typing import Dict

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