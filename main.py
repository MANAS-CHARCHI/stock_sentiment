from contextlib import asynccontextmanager
from fastapi import FastAPI
from schedule.scheduler import start_scheduler, scheduler
from api.ingest_route import router as ingest_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(ingest_router)
