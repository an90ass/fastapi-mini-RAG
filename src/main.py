from fastapi import FastAPI
from routes.data import data_router
from routes.base import base_router

app = FastAPI(
    title="mini-RAG",
    version="0.1",
    openapi_tags=[
        {"name": "data", "description": "File upload and data operations"},
        {"name": "base", "description": "App welcome and metadata"},
    ],
)
app.include_router(data_router)
app.include_router(base_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run( "main:app", host="127.0.0.1", port=8000, reload=True)