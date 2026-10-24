from fastapi import FastAPI
from routes.data import data_router
from routes.base import base_router
from routes.nlp import nlp_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDbProviderFactory import VectorDbProviderFactory

app = FastAPI(
    title="mini-RAG",
    version="0.1",
    openapi_tags=[
        {"name": "data", "description": "File upload and data operations"},
        {"name": "base", "description": "App welcome and metadata"},
    ],
)

async def startup_span():
    
    settings = get_settings()
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(config=settings)
    vector_db_provider_factory = VectorDbProviderFactory(config=settings)

    # generation client
    app.state.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.state.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    
    # embedding client
    app.state.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.state.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)

    # vector db client
    app.state.vector_db_client = vector_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    # connect to the database
    app.state.vector_db_client.connect()
async def shutdown_span():
    app.state.mongo_conn.close()
    app.state.vector_db_client.disconnect()
    


app.router.on_startup.append(startup_span)
app.router.on_shutdown.append(shutdown_span)
    
app.include_router(data_router)
app.include_router(base_router)
app.include_router(nlp_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run( "main:app", host="127.0.0.1", port=8000, reload=True)