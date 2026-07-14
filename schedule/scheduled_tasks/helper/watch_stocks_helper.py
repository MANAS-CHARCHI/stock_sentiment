from dataclasses import dataclass
from typing import Optional, Any

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.models import WatchedStock, StocksAnalyticsInfo, StockHistory, AllNSEStocks, YFSummary, AnalystRecommendation
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


def _normalize_nse_ticker(ticker: str) -> str:
    ticker = ticker.strip().upper()
    return ticker if "." in ticker else f"{ticker}.NS"

@dataclass
class YFSnapshot:
    """Everything fetched from yfinance for one ticker, fetched exactly once."""
    ticker: str
    info: dict
    news: list
    history: pd.DataFrame
    recommendations: pd.DataFrame
    analyst_price_targets: dict[str, Any]

def fetch_yf_snapshot(ticker: str, history_period: str = "1mo") -> YFSnapshot:
    ticker = _normalize_nse_ticker(ticker)
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info
    news = yf_ticker.news 
    history = yf_ticker.history(period=history_period)
    recommendations = yf_ticker.recommendations
    analyst_price_targets = yf_ticker.analyst_price_targets or {}

    if not info or not info.get("exchange"):
        raise ValueError(f"'{ticker}' not found on Yahoo Finance")
    
    return YFSnapshot(
            ticker=ticker, 
            info=info, 
            news=news, 
            history=history, 
            recommendations=recommendations,
            analyst_price_targets=analyst_price_targets,
        )

def _add_watch_stock(snapshot: YFSnapshot, db: Session) -> WatchedStock:
    stock_row = None
    try:
        stock_row = db.query(WatchedStock).filter_by(ticker=snapshot.ticker).first()
    except Exception as exc:
        print(exc)
    if stock_row is not None:
        return stock_row
    
    symbol = snapshot.ticker.split(".")[0]
    try:
        master_stock = db.query(AllNSEStocks).filter_by(symbol=symbol).first()
    except Exception as exc:
        print(exc)
    
    try:
        stock_row = WatchedStock(
            ticker=snapshot.ticker,
            master_stock_isin=master_stock.isin_number if master_stock else None,
            exchange=snapshot.info.get("exchange"),
            name=snapshot.info.get("longName") or snapshot.info.get("shortName") or snapshot.ticker,
            short_name=snapshot.info.get("shortName"),
            country=snapshot.info.get("country"),
            industry=snapshot.info.get("industry"),
            description=snapshot.info.get("longBusinessSummary"),
        )
    except Exception as exc:
        print(exc)
    db.add(stock_row)
    db.flush()
    return stock_row

def _stock_analytics_update(snapshot: YFSnapshot, stock_id: int, db: Session) -> None:
    info = snapshot.info
    price_targets = snapshot.analyst_price_targets

    analytics = (
        db.query(StocksAnalyticsInfo)
        .filter_by(stock_id=stock_id)
        .first()
    )

    if analytics is None:
        analytics = StocksAnalyticsInfo(stock_id=stock_id)
        db.add(analytics)

    # Yahoo INFO fields
    analytics.dividend_yield = info.get("dividendYield")
    analytics.dividend_rate = info.get("dividendRate")
    analytics.marketCap = info.get("marketCap")
    analytics.trailingPE = info.get("trailingPE")
    analytics.priceToBook = info.get("priceToBook")

    analytics.fiftyTwoWeekHigh = info.get("fiftyTwoWeekHigh")
    analytics.fiftyTwoWeekLow = info.get("fiftyTwoWeekLow")
    analytics.fiftyDayAverage = info.get("fiftyDayAverage")
    analytics.twoHundredDayAverage = info.get("twoHundredDayAverage")

    analytics.currentPrice = (
        info.get("currentPrice") or info.get("previousClose")
    )

    # Analyst price targets
    if price_targets:
        analytics.high52Week = price_targets.get("high")
        analytics.low52Week = price_targets.get("low")
        analytics.mean = price_targets.get("mean")
        analytics.median = price_targets.get("median")

def _stock_history_update(snapshot: YFSnapshot, stock_id: int, db: Session) -> None:
    if snapshot.history.empty:
        return
    incoming_dates = [
        ts.tz_localize(None).to_pydatetime() if ts.tzinfo else ts.to_pydatetime()
        for ts in snapshot.history.index
    ]
    try:
        existing_dates = {
            d for (d,) in db.query(StockHistory.snapshot_date)
            .filter(
                StockHistory.stock_id == stock_id,
                StockHistory.snapshot_date.in_(incoming_dates),
            )
            .all()
        }
    except Exception as exc:
        print(exc)
    for ts, row in zip(incoming_dates, snapshot.history.itertuples(index=False)):
        if ts in existing_dates:
            continue
        try:
            db.add(StockHistory(
                stock_id=stock_id,
                snapshot_date=ts,
                open=row.Open,
                high=row.High,
                low=row.Low,
                close=row.Close,
                volume=row.Volume,
                dividends=row.Dividends,
                stock_splits=getattr(row, "Stock_Splits", None),  # 'Stock Splits' -> Stock_Splits via itertuples
            ))
        except Exception as exc:
            print(exc)

def _yf_news_update(snapshot: YFSnapshot, stock_id: int, db: Session) -> None:
    for item in snapshot.news:
        content = item.get("content", {})
        title = content.get("title")
        if not title:
            continue
 
        pub_date_raw = content.get("pubDate")
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
 
        # Avoid duplicate rows on repeated syncs
        try:
            already_stored = (
                db.query(YFSummary)
                .filter_by(stock_id=stock_id, title=title, pub_date=pub_date)
                .first()
            )
        except Exception as exc:
            print(exc)
        if already_stored:
            continue
 
        db.add(YFSummary(
            stock_id=stock_id,
            title=title,
            summary=content.get("summary"),
            pub_date=pub_date,
        ))

def _analyst_recommendations_update(snapshot: YFSnapshot, stock_id: int, db: Session) -> None:
    recommendations = snapshot.recommendations
    price_targets = snapshot.analyst_price_targets

    if recommendations is not None and not recommendations.empty:
        for _, row in recommendations.iterrows():
            period = row["period"]  # "0m", "-1m", "-2m", ...

            try:
                months_back = abs(int(period.replace("m", "")))
            except ValueError:
                continue

            month = date.today() - relativedelta(months=months_back)
            snapshot_date = month.replace(day=1)
            snapshot_date_int = snapshot_date.strftime("%Y%m%d")
            if not isinstance(snapshot_date, date):
                continue

            recommendation = (
                db.query(AnalystRecommendation)
                .filter_by(
                    all_nse_stock_id=stock_id,
                    snapshot_date=snapshot_date_int,
                )
                .first()
            )

            if recommendation is None:
                recommendation = AnalystRecommendation(
                    all_nse_stock_id=stock_id,
                    snapshot_date=snapshot_date_int,
                )
                db.add(recommendation)

            recommendation.strong_buy = int(row["strongBuy"])
            recommendation.buy = int(row["buy"])
            recommendation.hold = int(row["hold"])
            recommendation.sell = int(row["sell"])
            recommendation.strong_sell = int(row["strongSell"])

    # Update analyst price targets
    analytics = (
        db.query(StocksAnalyticsInfo)
        .filter_by(stock_id=stock_id)
        .first()
    )

    if analytics is not None and price_targets:
        analytics.currentPrice = price_targets.get("current")
        analytics.high52Week = price_targets.get("high")
        analytics.low52Week = price_targets.get("low")
        analytics.mean = price_targets.get("mean")
        analytics.median = price_targets.get("median")

def remove_watch_stock(ticker, db: Session):
    try:
        stock_row = db.query(WatchedStock).filter_by(ticker=ticker).first()
    except Exception as exc:
        print(exc)
    if stock_row:
        db.delete(stock_row)


def sync_watched_stock(ticker: str) -> dict:
    snapshot = fetch_yf_snapshot(ticker)
    db = SessionLocal()
    try:
        stock_row = _add_watch_stock(snapshot, db)
        _stock_analytics_update(snapshot, stock_row.id, db)
        _stock_history_update(snapshot, stock_row.id, db)
        _yf_news_update(snapshot, stock_row.id, db)
        _analyst_recommendations_update(snapshot, stock_row.id, db)
        db.commit()
        return {"status": "ok", "ticker": snapshot.ticker, "stock_id": stock_row.id}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def sync_stock(stock: WatchedStock):
    snapshot = fetch_yf_snapshot(stock.ticker)
    db = SessionLocal()
    try:
        _stock_analytics_update(snapshot, stock.id, db)
        _stock_history_update(snapshot, stock.id, db)
        _yf_news_update(snapshot, stock.id, db)
        _analyst_recommendations_update(snapshot, stock.id, db)

        db.commit()
        print(f"Updated {stock.ticker}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# import asyncio
# MAX_CONCURRENT = 10
# async def _sync_stock_async(stock: WatchedStock, semaphore: asyncio.Semaphore):
#     async with semaphore:
#         try:
#             await asyncio.to_thread(sync_stock, stock)
#         except Exception as e:
#             print(f"{stock.ticker}: {e}")

# async def schadule_to_update():
#     db = SessionLocal()
#     try:
#         stocks = db.query(WatchedStock).all()
#     finally:
#         db.close()
#     semaphore = asyncio.Semaphore(MAX_CONCURRENT)
#     tasks = [
#         asyncio.create_task(_sync_stock_async(stock, semaphore))
#         for stock in stocks
#     ]
#     await asyncio.gather(*tasks)