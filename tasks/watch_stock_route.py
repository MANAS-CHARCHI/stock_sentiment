"""
Route to add a new stock to the watchlist and immediately kick off
yfinance ingestion for it — in the background, so the request returns fast.

Mount alongside your other routers, e.g.:
    from api.watched_stocks import router as watched_stocks_router
    app.include_router(watched_stocks_router)
"""

import yfinance as yf
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db, SessionLocal
from db.models import WatchedStock, AllNSEStocks
from tasks.ingest_watched_stock import ingest_stock_from_info

router = APIRouter(prefix="/watched-stocks", tags=["watched-stocks"])


def _to_nse_symbol(ticker: str) -> str:
    """
    yfinance tickers for NSE stocks are suffixed, e.g. 'RELIANCE.NS'.
    AllNSEStocks.symbol is stored without the suffix, e.g. 'RELIANCE'.
    Strip any '.XX' suffix so we can match against it.
    """
    return ticker.split(".")[0].upper()


def _find_master_stock(db: Session, ticker: str) -> AllNSEStocks | None:
    symbol = _to_nse_symbol(ticker)
    return db.query(AllNSEStocks).filter_by(symbol=symbol).first()


def _run_ingest(ticker: str, info: dict):
    """
    Runs in the background AFTER the response has been sent.
    Opens its OWN session — the request's `db` session is already
    closed by the time this executes, so we can't reuse it.

    Takes the already-fetched `info` dict so we don't call
    yfinance's .info endpoint a second time for the same ticker.
    """
    session = SessionLocal()
    try:
        ingest_stock_from_info(session, ticker, info)
    except Exception as exc:
        # Don't crash the background worker — just log it.
        # Swap this for your actual logger.
        print(f"[ingest_stock] failed for {ticker}: {exc}")
    finally:
        session.close()


@router.post("")
def add_watched_stock(
    ticker: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Prevent duplicates
    existing = db.query(WatchedStock).filter_by(ticker=ticker).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"{ticker} is already watched")

    # Fetch metadata ONCE — used both to populate the row below
    # and reused in the background task so we don't fetch it twice.
    info = yf.Ticker(ticker).info
    if not info or not info.get("symbol"):
        raise HTTPException(status_code=404, detail=f"'{ticker}' not found on Yahoo Finance")

    # Find the matching NSE master record so master_stock_id is linked
    # (enables the AnalystRecommendation relationship on AllNSEStocks)
    master_stock = _find_master_stock(db, ticker)

    new_stock = WatchedStock(
        ticker=ticker,
        master_stock_id=master_stock.id if master_stock else None,
        exchange=info.get("exchange"),
        name=info.get("longName") or info.get("shortName") or ticker,
        short_name=info.get("shortName"),
        country=info.get("country"),
        industry=info.get("industry"),
        description=info.get("longBusinessSummary"),
    )
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)

    # Immediately queue the rest of ingestion (analytics + news)
    background_tasks.add_task(_run_ingest, ticker, info)

    return {
        "status": "added",
        "ticker": ticker,
        "id": new_stock.id,
        "master_stock_id": new_stock.master_stock_id,
        "ingest": "queued",
    }