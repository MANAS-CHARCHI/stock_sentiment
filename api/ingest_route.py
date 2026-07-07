from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import SessionLocal, get_db
from tasks.ingest_watched_stock import ingest_stock, get_or_create_watched_stock, ingest_stock_from_info
import yfinance as yf

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/{ticker}")
def trigger_ingest(ticker: str, db: Session = Depends(get_db)):
    try:
        ingest_stock(db, ticker)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")
 
    return {"status": "ok", "ticker": ticker}

@router.post("/{ticker}/async")
def trigger_ingest_background(
    ticker: str,
    background_tasks: BackgroundTasks,
):
    from db.database import SessionLocal
 
    def _run(ticker: str):
        session = SessionLocal()
        try:
            ingest_stock(session, ticker)
        finally:
            session.close()
 
    background_tasks.add_task(_run, ticker)
    return {"status": "queued", "ticker": ticker}



@router.post("/{watched_stock}")
def trigger_ingest_watched_stock(
    body: IngestRequest
):
    
    ticker = _normalize_nse_ticker(body.ticker)
    info = yf.Ticker(ticker).info
    if not info or not info.get("exchange"):
        raise HTTPException(status_code=404, detail=f"'{ticker}' not found on Yahoo Finance")
 
    session = SessionLocal()
    try:
        ingest_stock_from_info(session, ticker, info)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")
    finally:
        session.close()
 
    return {"status": "ok", "ticker": ticker}
    