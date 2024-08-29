from motor.motor_asyncio import AsyncIOMotorClient
import sys

def connect_db():
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.image_processor
        return db
    except Exception as err:
        print(err)
        sys.exit(1)