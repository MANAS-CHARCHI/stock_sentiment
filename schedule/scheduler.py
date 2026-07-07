import logging
from apscheduler.schedulers.background import BackgroundScheduler
from schedule.scheduled_tasks.stock_update_scheduler import JOB as nse_stock_job
from schedule.scheduled_tasks.yf_all_watchstock_update import JOB as yf_stock_job

logger = logging.getLogger("scheduler")
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

ALL_JOBS = [
    nse_stock_job,
    yf_stock_job
]

def start_scheduler():
    for job in ALL_JOBS:
        scheduler.add_job(
            job["func"],
            trigger=job["trigger"],
            id=job["id"],
            replace_existing=True,
            misfire_grace_time=job.get("misfire_grace_time", 3600),
        )
        logger.info(f"Registered job: {job['id']}")
        
    scheduler.start()
    logger.info(f"Scheduler started with {len(ALL_JOBS)} job(s)")