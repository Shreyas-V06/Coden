import os
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None
    
    #Connection Pooling 
    async def connect(self):
        self.client = AsyncIOMotorClient(
            host=os.getenv(key="MONGO_URI", default="mongodb://localhost:27017"),
            maxPoolSize=100,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000
        )
        self.db = self.client[os.getenv(key="MONGO_DB_NAME", default="coden_game")]

    async def disconnect(self):
        if self.client:
            self.client.close()

db_manager = MongoDBManager()

def get_db():
    return db_manager.db