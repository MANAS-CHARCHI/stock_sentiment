"""
Ingest Yahoo Finance data for a stock and store it via SQLAlchemy models.

IMPORTANT: yfinance data is fetched ONE TIME per stock per run.
  - stock.info  -> called once, result reused for StocksAnalyticsInfo
  - stock.news  -> called once, result reused for YFSummary rows

Assumptions (adjust these three things to match your actual project):
  1. `db.database` exposes a `SessionLocal` sessionmaker.
  2. `WatchedStock` has a `.ticker` column used to look the row up
     (swap for `.symbol` or whatever your schema actually calls it).
  3. Models are importable from `db.models` — change the import path
     to wherever AnalystRecommendation / StockHistory / StocksAnalyticsInfo /
     YFSummary / WatchedStock actually live.
"""

import yfinance as yf
from datetime import datetime, date

from db.database import SessionLocal
from db.models import (
    WatchedStock, 
    StocksAnalyticsInfo, 
    YFSummary, 
    AllNSEStocks, AnalystRecommendation
    )

def _to_nse_symbol(ticker: str) -> str:
    """
    yfinance tickers for NSE stocks are suffixed, e.g. 'RELIANCE.NS'.
    AllNSEStocks.symbol is stored without the suffix, e.g. 'RELIANCE'.
    """
    return ticker.split(".")[0].upper()


def get_or_create_watched_stock(session, ticker: str, info: dict) -> WatchedStock:
    stock_row = session.query(WatchedStock).filter_by(ticker=ticker).first()
    if stock_row is None:
        master_stock = (
            session.query(AllNSEStocks)
            .filter_by(symbol=_to_nse_symbol(ticker))
            .first()
        )
        stock_row = WatchedStock(
            ticker=ticker,
            master_stock_id=master_stock.id if master_stock else None,
            exchange=info.get("exchange"),
            name=info.get("longName") or info.get("shortName") or ticker,
            short_name=info.get("shortName"),
            country=info.get("country"),
            industry=info.get("industry"),
            description=info.get("longBusinessSummary"),
        )
        session.add(stock_row)
        session.flush()  # assigns stock_row.id without committing yet
    return stock_row


def ingest_stock_from_info(session, ticker: str, info: dict) -> None:
    yf_ticker = yf.Ticker(ticker)
    news = yf_ticker.news   # 1 call — reused below, never re-fetched

    watched_stock = get_or_create_watched_stock(session, ticker, info)

    # ---------------- Analytics snapshot ----------------
    ex_div_raw = info.get("exDividendDate")
    dividend_time = None
    if ex_div_raw:
        try:
            dividend_time = datetime.fromtimestamp(int(ex_div_raw))
        except (ValueError, TypeError):
            dividend_time = None

    analytics = StocksAnalyticsInfo(
        stock_id=watched_stock.id,
        dividend_yield=info.get("dividendYield"),
        dividend_rate=info.get("dividendRate"),
        dividend_time=dividend_time,
        marketCap=info.get("marketCap"),
        trailingPE=info.get("trailingPE"),
        priceToBook=info.get("priceToBook"),
        high52Week=info.get("fiftyTwoWeekHigh"),
        low52Week=info.get("fiftyTwoWeekLow"),
        fiftyDayAverage=info.get("fiftyDayAverage"),
        twoHundredDayAverage=info.get("twoHundredDayAverage"),
        currentPrice=info.get("currentPrice") or info.get("previousClose"),
    )
    session.add(analytics)

    # ---------------- News summaries ----------------
    for item in news:
        content = item.get("content", {})
        title = content.get("title")
        summary = content.get("summary")
        pub_date_raw = content.get("pubDate")

        if not title:
            continue

        pub_date = None
        if pub_date_raw:
            try:
                pub_date = datetime.fromisoformat(
                    pub_date_raw.replace("Z", "+00:00")
                ).date()
            except ValueError:
                pub_date = None
        if pub_date is None:
            pub_date = date.today()

        # Avoid duplicate rows on repeated runs (same stock+title+date)
        already_stored = (
            session.query(YFSummary)
            .filter_by(stock_id=watched_stock.id, title=title, pub_date=pub_date)
            .first()
        )
        if already_stored:
            continue

        session.add(
            YFSummary(
                stock_id=watched_stock.id,
                title=title,
                summary=summary,
                pub_date=pub_date,
            )
        )

    session.commit()


def ingest_stock(session, ticker: str) -> None:
    info = yf.Ticker(ticker).info
    ingest_stock_from_info(session, ticker, info)


if __name__ == "__main__":
    db_session = SessionLocal()
    try:
        ingest_stock(db_session, "RHFL.NS")
    finally:
        db_session.close()