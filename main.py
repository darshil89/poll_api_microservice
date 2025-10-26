from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uvicorn
from router.poll import router as poll_router
from helpers.db import check_db_connection
load_dotenv()

app = FastAPI()

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