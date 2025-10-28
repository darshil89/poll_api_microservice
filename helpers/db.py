# Checking if the database is connected
from prisma import Prisma
import os
from dotenv import load_dotenv
import redis.asyncio as redis

# Load environment variables
load_dotenv()

prisma_client = Prisma()

async def check_db_connection():
    # Check if database URL is configured
    database_url = os.getenv("API_DATABASE_URL")
    if not database_url:
        print("Error: API_DATABASE_URL environment variable is not set")
        return False
    
    try:
        await prisma_client.connect()
        await prisma_client.poll.find_first()
        redis_client.ping()
        print("Database connection successful")
        return True
    except Exception as e:
        error_message = str(e)
        print(f"Database connection failed: {error_message}")
        return False

async def connect_redis():
    try:
        redis_client = redis.Redis(host=os.getenv("API_REDIS_HOST"), port=os.getenv("API_REDIS_PORT"), password=os.getenv("API_REDIS_PASSWORD"))
        redis_client.ping()
        print("Redis connection successful")
        return redis_client
    except Exception as e:
        error_message = str(e)
        print(f"Redis connection failed: {error_message}")

redis_client = redis.Redis(host=os.getenv("API_REDIS_HOST"), port=os.getenv("API_REDIS_PORT"), password=os.getenv("API_REDIS_PASSWORD"))


async def disconnect_db():
    try:
        await prisma_client.disconnect()
        redis_client.aclose()
    except Exception as e:
        error_message = str(e)
        print(f"Database disconnection failed: {error_message}")
        return False