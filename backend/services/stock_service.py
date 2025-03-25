
import yfinance as yf
from pydantic import BaseModel

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

# print(get_stocks_data(["AAPL", "MSFT", "SPX", "^GSPC", "NVDA", "META"]))