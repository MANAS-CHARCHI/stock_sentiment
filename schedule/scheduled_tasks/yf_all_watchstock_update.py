import logging
from apscheduler.triggers.cron import CronTrigger
from concurrent.futures import ThreadPoolExecutor, as_completed

from db.database import SessionLocal
from db.models import WatchedStock
from api.helpers.watch_stocks_helper import sync_stock

logger = logging.getLogger("yf_stock_update")

MAX_WORKERS = 10

def run_yf_stock_sync():
    db = SessionLocal()

    try:
        logger.info("Starting YF stock sync job")

        stocks = db.query(WatchedStock).all()
        logger.info(f"Found {len(stocks)} stocks to sync")

        def _run(stock):
            try:
                sync_stock(stock)
            except Exception as e:
                logger.exception(f"Failed {stock.ticker}: {e}")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(_run, stock) for stock in stocks]

            for future in as_completed(futures):
                future.result()

        logger.info("YF stock sync finished")

    except Exception as e:
        logger.exception(f"YF stock sync failed: {e}")
        db.rollback()

    finally:
        db.close()

JOB = {
    "id": "yf_stock_sync",
    "func": run_yf_stock_sync,
    "trigger": CronTrigger(
        hour=10,
        minute=14,
        timezone="Asia/Kolkata"
    ),
    "misfire_grace_time": 3600,
}