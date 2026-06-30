from contextlib import asynccontextmanager
from fastapi import FastAPI
from schedule.scheduler import start_scheduler, scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)