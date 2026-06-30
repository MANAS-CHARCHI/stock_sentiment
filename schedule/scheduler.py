import logging
from apscheduler.schedulers.background import BackgroundScheduler
from schedule.scheduled_tasks.stock_update_scheduler import JOB as nse_stock_job

logger = logging.getLogger("scheduler")
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

ALL_JOBS = [
    nse_stock_job,
]

def start_scheduler():
    print(">>> start_scheduler() called")
    for job in ALL_JOBS:
        scheduler.add_job(
            job["func"],
            trigger=job["trigger"],
            id=job["id"],
            replace_existing=True,
            misfire_grace_time=job.get("misfire_grace_time", 3600),
        )
        logger.info(f"Registered job: {job['id']}")
        
    print(">>> Jobs registered:", [j.id for j in scheduler.get_jobs()])

    scheduler.start()
    print(">>> Jobs registered:", [(j.id, j.next_run_time) for j in scheduler.get_jobs()])

    logger.info(f"Scheduler started with {len(ALL_JOBS)} job(s)")