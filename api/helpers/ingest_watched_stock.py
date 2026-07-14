import yfinance as yf
from datetime import datetime, date

from db.database import SessionLocal
from db.models import (
    WatchedStock, 
    StocksAnalyticsInfo, 
    YFSummary, 
    AllNSEStocks, AnalystRecommendation
    )
def _normalize_nse_ticker(ticker: str) -> str:
    ticker = ticker.strip().upper()
    return ticker if "." in ticker else f"{ticker}.NS"

def get_or_create_watched_stock(session, ticker: str, info: dict) -> WatchedStock:
    stock_row = session.query(WatchedStock).filter_by(ticker=ticker).first()
    if stock_row is None:
        symbol = ticker.split(".")[0]
        master_stock = (
            session.query(AllNSEStocks)
            .filter_by(symbol=symbol)
            .first()
        )
        stock_row = WatchedStock(
            ticker=ticker,
            master_stock_isin=master_stock.isin_number if master_stock else None,
            exchange=info.get("exchange"),
            name=info.get("longName") or info.get("shortName") or ticker,
            short_name=info.get("shortName"),
            country=info.get("country"),
            industry=info.get("industry"),
            description=info.get("longBusinessSummary"),
        )
        session.add(stock_row)
        session.flush()
    return stock_row

def ingest_stock_from_info(session, ticker: str, info: dict, news: list) -> None:
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

    # ---------------- Existing news ----------------

    existing_news = {
        (title, pub_date)
        for title, pub_date in (
            session.query(YFSummary.title, YFSummary.pub_date)
            .filter_by(stock_id=watched_stock.id)
            .all()
        )
    }

    news_rows = []
    
    # ---------------- News summaries ----------------
    for item in news or []:
        content = item.get("content", {})
        
        title = content.get("title")
        if not title:
            continue
        
        summary = content.get("summary")
        pub_date_raw = content.get("pubDate")

        pub_date = date.today()
        if pub_date_raw:
            try:
                pub_date = datetime.fromisoformat(
                    pub_date_raw.replace("Z", "+00:00")
                ).date()
            except ValueError:
                pass
            
        if (title, pub_date) in existing_news:
            continue
        
        news_rows.append(
            YFSummary(
                stock_id=watched_stock.id,
                title=title,
                summary=summary,
                pub_date=pub_date,
            )
        )
        
        if news_rows:
            session.add_all(news_rows)
        
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise

def ingest_stock(session, ticker: str) -> None:
    ticker = _normalize_nse_ticker(ticker)
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info
    news = yf_ticker.news
    if not info or info.get("exchange") is None:
        raise ValueError(f"{ticker} not found on Yahoo Finance")
    ingest_stock_from_info(session, ticker, info, news)