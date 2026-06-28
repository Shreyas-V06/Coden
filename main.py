import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from workers.matchmaker import matchmaker  
from services.redis_pubsub import listen_to_matches  
from api.websockets.routes import router as matchmaking_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(matchmaker())
    listener_task = asyncio.create_task(listen_to_matches())
    yield  
    worker_task.cancel()
    listener_task.cancel()

app = FastAPI(lifespan=lifespan)
app.include_router(matchmaking_router)