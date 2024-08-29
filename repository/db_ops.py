from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class DatabaseOperations:
    def __init__(self, connection_string):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.image_processor

    async def insert_job(self, job_data):
        return await self.db.jobs.insert_one(job_data)

    async def update_job_status(self, request_id, status):
        return await self.db.jobs.update_one(
            {"requestId": request_id},
            {"$set": {"status": status}}
        )

    async def get_job_status(self, request_id):
        print({"requestId": request_id})
        job = await self.db.jobs.find_one({"requestId": request_id})
        return job if job else None

    async def insert_product(self, product_data):
        return await self.db.products.insert_one(product_data)

    async def get_webhooks(self):
        cursor = self.db.webhooks.find()
        return await cursor.to_list(length=None)

db_ops = DatabaseOperations("mongodb://localhost:27017")