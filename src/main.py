from fastapi import FastAPI
from routes.data import data_router
from routes.base import base_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings



app = FastAPI(
    title="mini-RAG",
    version="0.1",
    openapi_tags=[
        {"name": "data", "description": "File upload and data operations"},
        {"name": "base", "description": "App welcome and metadata"},
    ],
)
@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.mongo_conn.close()

    
app.include_router(data_router)
app.include_router(base_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run( "main:app", host="127.0.0.1", port=8000, reload=True)