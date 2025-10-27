# Checking if the database is connected
from prisma import Prisma
import os
from dotenv import load_dotenv
from redis.asyncio import redis
# Load environment variables
load_dotenv()

prisma_client = Prisma()

redis_client = redis.from_url(
    os.getenv("API_REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

async def check_db_connection():
    # Check if database URL is configured
    database_url = os.getenv("API_DATABASE_URL")
    if not database_url:
        print("Error: API_DATABASE_URL environment variable is not set")
        return False
    
    try:
        await prisma_client.connect()
        await prisma_client.poll.find_first()
        await redis_client.ping()
        print("Database connection successful")
        return True
    except Exception as e:
        error_message = str(e)
        print(f"Database connection failed: {error_message}")
        return False

async def disconnect_db():
    try:
        await prisma_client.disconnect()
        await redis_client.aclose()
    except Exception as e:
        error_message = str(e)
        print(f"Database disconnection failed: {error_message}")
        return False