# Checking if the database is connected
from prisma import Prisma
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_db_connection():
    # Check if database URL is configured
    database_url = os.getenv("API_DATABASE_URL")
    if not database_url:
        print("Error: API_DATABASE_URL environment variable is not set")
        return False
    
    prisma = Prisma()
    try:
        await prisma.connect()
        await prisma.poll.find_first()
        await prisma.disconnect()
        print("Database connection successful")
        return True
    except Exception as e:
        error_message = str(e)
        print(f"Database connection failed: {error_message}")
        
        try:
            await prisma.disconnect()
        except:
            pass
        return False