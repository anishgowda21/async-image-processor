from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseOperations:
    def __init__(self, connection_string):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.image_processor

    async def insert_job(self, job_data):
        return await self.db.jobs.insert_one(job_data)

    async def update_job_status(self, request_id, updateItem):
        return await self.db.jobs.update_one(
            {"requestId": request_id},
            {"$set": updateItem}
        )

    async def get_job_status(self, request_id):
        job = await self.db.jobs.find_one({"requestId": request_id})
        return job if job else None

mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_ops = DatabaseOperations(mongo_url)