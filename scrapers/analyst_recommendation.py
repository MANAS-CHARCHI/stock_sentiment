from datetime import datetime
from dateutil.relativedelta import relativedelta

# Assuming current execution date is June 2026
current_period = datetime.now().date().replace(day=1) # 2026-06-01

for _, row in df.iterrows():
    # Clean the string "0m" -> 0, "-1m" -> 1
    period_offset = abs(int(str(row['period']).replace('m', '')))
    
    # Calculate the exact calendar period this row describes
    target_period_month = current_period - relativedelta(months=period_offset)
    
    # Example Row Processing Matrix:
    # row['period'] == '0m'  -> target_period_month = 2026-06-01
    # row['period'] == '-1m' -> target_period_month = 2026-05-01
    # row['period'] == '-2m' -> target_period_month = 2026-04-01
    
    record = {
        "all_nse_stock_id": master_stock_id,
        "period_month": target_period_month, # Stored as a pure static historical point
        "strong_buy": int(row['strongBuy']),
        "buy": int(row['buy']),
        "hold": int(row['hold']),
        "sell": int(row['sell']),
        "strong_sell": int(row['strongSell'])
    }