import yfinance as yf

def fetch_stock_data(ticker: str):
    stock = yf.Ticker(ticker)

    return {
        "stock": stock,
        "info": stock.info,
        "history": stock.history(period="1d"),
        "news": stock.news,
        "price_targets": stock.analyst_price_targets,
        "recommendations": stock.recommendations_summary,
    }

print(fetch_stock_data(""))