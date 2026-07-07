import os
import requests
from datetime import datetime
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from db.models import AllNSEStocks
import logging

logger = logging.getLogger("nse_stock_update")

def get_new_stock_list(link: str="https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv", save_dir: str = "stock_data")->None:
    os.makedirs(save_dir, exist_ok=True)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/static/market-data/securities-available-for-trading",
    }
    session = requests.Session()
    session.headers.update(headers)
    # NSE requires an initial visit to set cookies before file downloads work
    session.get("https://www.nseindia.com", timeout=10)
    response = session.get(link, timeout=15)
    response.raise_for_status()
    
    ext = os.path.splitext(link.split("/")[-1])[1] or ".csv"
    timestamp = datetime.now().strftime("%Y_%m_%d")
    filename = f"{timestamp}{ext}"
    filepath = os.path.abspath(os.path.join(save_dir, filename))
    with open(filepath, "wb") as f:
        f.write(response.content)

    logger.info(f"Downloaded today's NSE file {filename} to {filepath}")

    return filepath

def prepare_stock_records(csv_path: str) -> list[dict]:
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    
    df = df.rename(columns={
        "SYMBOL": "symbol",
        "NAME OF COMPANY": "name",
        "DATE OF LISTING": "date_of_listing",
        "ISIN NUMBER": "isin_number",
        "FACE VALUE": "face_value",
    })
    df["date_of_listing"] = pd.to_datetime(df["date_of_listing"], format="%d-%b-%Y")
    df["symbol"] = df["symbol"].str.strip()
    df["name"] = df["name"].str.strip()
    df["isin_number"] = df["isin_number"].str.strip()
    records = df[["symbol", "name", "date_of_listing", "isin_number", "face_value"]].to_dict(orient="records")
    logger.info(f"Read {len(records)} records from {csv_path} & prepared them to update the DB")
    return records

def sync_stock_record(records: list[dict], db: Session) -> dict:
    if not records:
        return {"total_in_csv": 0, "deleted": 0}
    incoming_symbols = [r["isin_number"] for r in records]
    
    stmt = insert(AllNSEStocks).values(records)
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["isin_number"],
        set_={
            "name": stmt.excluded.name,
            "date_of_listing": stmt.excluded.date_of_listing,
            "face_value": stmt.excluded.face_value,
        },
    )
    db.execute(upsert_stmt)
    
    deleted = (
        db.query(AllNSEStocks)
        .filter(~AllNSEStocks.isin_number.in_(incoming_symbols))
        .delete(synchronize_session=False)
    )
    db.commit()
    
    logger.info(f"Upserted {len(records)} records & deleted {deleted} records")

    return {
        "total_in_csv": len(records),
        "deleted": deleted,
    }