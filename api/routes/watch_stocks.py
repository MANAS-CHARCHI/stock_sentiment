from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
 
from api.helpers.watch_stocks_helper import sync_watched_stock, remove_watch_stock

router = APIRouter(prefix="/watched_stocks", tags=["watched_stocks"])

class AddWatchedStockRequest(BaseModel):
    ticker: str

def _run_sync(ticker: str):
    try:
        sync_watched_stock(ticker)
    except Exception as exc:
        print(f"[sync_watched_stock] failed for {ticker}: {exc}")

@router.post("")
def add_watched_stock(body: AddWatchedStockRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_sync, body.ticker)
    return {"status": "queued", "ticker": body.ticker}


@router.post("/{ticker}/sync")
def sync_watched_stock_now(ticker: str):
    try:
        result = sync_watched_stock(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Sync failed: {exc}")
 
    return result
 
 
@router.delete("/{ticker}")
def delete_watched_stock(ticker: str):
    try:
        result = remove_watch_stock(ticker)
    except ValueError as exc:
        # e.g. ticker isn't currently watched
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Remove failed: {exc}")
 
    return result
