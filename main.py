import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from workers.matchmaker import matchmaker  
from utils.redis_pubsub import listen_to_matches  
from api.websockets.routes import router as matchmaking_router
from api.http.routes import router as http_router
from utils.redis import clearQueue
from core.database import db_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_manager.connect()
    await clearQueue()
    worker_task = asyncio.create_task(coro=matchmaker())
    listener_task = asyncio.create_task(coro=listen_to_matches())
    yield  
    worker_task.cancel()
    listener_task.cancel()
    await db_manager.disconnect()

app = FastAPI(lifespan=lifespan)
app.include_router(router=matchmaking_router)
app.include_router(router=http_router)