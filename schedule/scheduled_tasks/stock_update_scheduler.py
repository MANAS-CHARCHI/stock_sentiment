import logging
from apscheduler.triggers.cron import CronTrigger
import os
from db.database import SessionLocal

from tasks.update_latest_stocks import (
    get_new_stock_list, 
    prepare_stock_records, 
    sync_stock_record
)
logger = logging.getLogger("nse_stock_update")


def run_nse_stock_sync():
    """The actual job that runs on schedule."""
    db = SessionLocal()
    filepath = None
    try:
        logger.info("Starting NSE stock sync job")
        filepath = get_new_stock_list()
        logger.info("Got the Latest NSE File")
        records = prepare_stock_records(filepath)
        logger.info("Prepared the record to update if any")
        result = sync_stock_record(records, db)
        logger.info(f"NSE stock sync finished")
    except Exception as e:
        logger.exception(f"NSE stock sync failed: {e}")
        db.rollback()
    finally:
        db.close()
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Removed temporary file: {filepath}")

JOB = {
    "id": "nse_stock_sync",
    "func": run_nse_stock_sync,
    "trigger": CronTrigger(hour=13, minute=29, timezone="Asia/Kolkata"),
    "misfire_grace_time": 3600,
}