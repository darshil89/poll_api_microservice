from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uvicorn
from contextlib import asynccontextmanager
from router.poll import router as poll_router
from helpers.db import check_db_connection, disconnect_db
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await check_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    yield
    await disconnect_db()

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    db = await check_db_connection()
    if not db:
        return {"message": "Database connection failed"}
    return {"message": "API service is running", "database": db}

app.include_router(poll_router)

if __name__ == "__main__":  
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)