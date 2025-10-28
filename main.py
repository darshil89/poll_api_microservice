from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from contextlib import asynccontextmanager
import socketio
import asyncio
import json

from router.poll import router as poll_router
from helpers.db import check_db_connection, disconnect_db, redis_client 

load_dotenv()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[]
)

async def redis_listener_task(sio: socketio.AsyncServer):
    """
    Listens to 'poll-updates' in Redis and emits the
    correct event to all connected Socket.IO clients.
    """
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("poll-updates")
    print("✅ Starting global Redis listener task...")
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=None)
            if message:
                data = json.loads(message["data"])
                
                # Smart router
                if data.get("type") == "like":
                    print(f"Broadcasting 'like-update': {data}")
                    await sio.emit('like-update', data)
                else:
                    print(f"Broadcasting 'vote-update': {data}")
                    await sio.emit('vote-update', data)
                    
    except Exception as e:
        print(f"❌ Redis listener task error: {e}")
    finally:
        print("Stopping Redis listener task...")
        pubsub.unsubscribe()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await check_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    asyncio.create_task(redis_listener_task(sio))
    print("Lifespan startup complete.")
    yield
    await disconnect_db()
    print("Lifespan shutdown complete.")

app = FastAPI(
    lifespan=lifespan,
    title="Poll Service API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio_app = socketio.ASGIApp(
    sio,
    socketio_path="/ws/updates"
)

@app.get("/")
async def read_root():
    return {"message": "API service is running"}


app.include_router(poll_router)

app.mount("/ws/updates", sio_app)



if __name__ == "__main__":  
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)