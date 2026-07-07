from contextlib import asynccontextmanager
from fastapi import FastAPI
from schedule.scheduler import start_scheduler, scheduler
import logging
from api.routes.watch_stocks import router as watched_stocks_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()   # also prints to console
    ]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(watched_stocks_router)