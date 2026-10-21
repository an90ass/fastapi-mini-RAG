from fastapi import FastAPI
from routes.data import data_router
from routes.base import base_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory


app = FastAPI(
    title="mini-RAG",
    version="0.1",
    openapi_tags=[
        {"name": "data", "description": "File upload and data operations"},
        {"name": "base", "description": "App welcome and metadata"},
    ],
)

async def startup_db_client():
    
    settings = get_settings()
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(config=settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.EMBEDDING_MODEL_ID)
    
    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)

async def shutdown_db_client():
    app.state.mongo_conn.close()


app.router.lifespan.on_startup.append(startup_db_client)
app.router.lifespan.on_shutdown.append(shutdown_db_client)
    
app.include_router(data_router)
app.include_router(base_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run( "main:app", host="127.0.0.1", port=8000, reload=True)