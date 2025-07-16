import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "itinerary_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

async def connect_to_mongo():
    """Initialize MongoDB connection"""
    try:
        await client.admin.command('ping')
        print("Connected to MongoDB successfully!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")


async def close_mongo_connection():
    """Close MongoDB connection"""
    client.close()