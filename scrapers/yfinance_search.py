import yfinance as yf
from datetime import datetime

stock = yf.Ticker("PERSISTENT.NS")

# Company info
info = stock.info
# # 1. Pull the raw values safely
# div_rate = info.get("dividendRate", 0) or 0
# raw_timestamp = info.get("exDividendDate")

# # 2. Safely parse the Timestamp to a human-readable date
# if raw_timestamp:
#     # Handle case where API might pass it as an int or float string
#     clean_date = datetime.fromtimestamp(int(raw_timestamp)).strftime('%Y-%m-%d')
# else:
#     clean_date = "No Date Available"

# # 3. Calculate the TRUE dividend yield yourself using the current price
# # (This completely bypasses Yahoo's broken 'dividendYield' math)
# current_price = info.get("currentPrice") or info.get("previousClose") or 1
# true_yield_percentage = (div_rate / current_price) * 100

# Print your results
# print(f"Last Dividend Money: {div_rate} INR")
# print(f"True Yield %:        {true_yield_percentage:.2f}%")
# print(f"Raw Timestamp:       {raw_timestamp}")

# print(f"Readable Date:       {clean_date}")
# print(info["longName"])           # Reliance Industries Limited
# print(info["sector"])             # Energy
# print(info["industry"])           # Oil & Gas Refining
# print(info["longBusinessSummary"]) # full company description
# print(info["country"])            # India
# print(info["website"])            # https://www.ril.com
# print(info["fullTimeEmployees"])  # 236000

# # Price data
# print(info["currentPrice"])       # 1456.75
# print(info["previousClose"])      # 1448.20
# print(info["open"])               # 1451.00
# print(info["dayHigh"])            # 1462.00
# print(info["dayLow"])             # 1445.00
# print(info["volume"])             # 8234567
# print(info["averageVolume"])      # 6123456

# # Fundamentals
# print(info["marketCap"])          # 1967234500000
# print(info["trailingPE"])         # 28.4
# print(info["priceToBook"])        # 2.1
# print(info["dividendYield"])      # 0.004
# print(info["fiftyTwoWeekHigh"])   # 1608.80
# print(info["fiftyTwoWeekLow"])    # 1201.05
# print(info["fiftyDayAverage"])    # 1389.40
# print(info["twoHundredDayAverage"]) # 1342.10

# # Historical prices
# history = stock.history(period="1d")  # last 30 days
# print(history)                         # DataFrame with OHLCV

# Recent news (built in)
# news = stock.news
# for n in news[:5]:
#     # Extract the inner content dictionary safely
#     content = n.get('content', {})
    
#     # Grab the specific fields
#     title = content.get('title', 'No Title')
#     summary = content.get('summary', 'No Summary')
#     pub_date = content.get('pubDate', 'No Date')
    
#     print(f"Date:    {pub_date}")
#     print(f"Title:   {title}")
#     print(f"Summary: {summary}")
#     print("-" * 40)

# Financials
# print(stock.financials)       # income statement
# print(stock.balance_sheet)    # balance sheet
# print(stock.cashflow)         # cash flow

# # Analyst recommendations
# print(stock.recommendations)  # buy/sell/hold from analysts
print(stock.analyst_price_targets)  # price targets