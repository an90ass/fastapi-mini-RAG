from fastapi import APIRouter, Depends , status , Request
from fastapi.responses import JSONResponse
import logging
from dependencies.settings_dependency import get_app_settings
from models import ResponseSignal
from schemes.nlp_scheme import PushRequest, IndexSearchRequest
from models.project_model import ProjectModel
from models.chunk_model import ChunkModel
from controllers import NLPController
logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp/index",
    tags=["nlp"],
    responses={404: {"description": "Not found"}},
)

@nlp_router.post("/push/{project_id}")
async def process_index(request: Request, project_id:str, push_request:PushRequest ):
    project_model = await ProjectModel.create_instance(db_client = request.app.state.db_client)
    chunk_model = await ChunkModel.create_instance(db_client = request.app.state.db_client)
    
    project = await project_model.get_or_create_project(project_id=project_id)

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": False,
                "singnal": ResponseSignal.ProjectNotFoundError.value
            },
        )

    nlp_controller = NLPController(vector_db_client=request.app.state.vector_db_client, generation_client=request.app.state.generation_client, embedding_client=request.app.state.embedding_client)
    has_records = True
    page_number = 1
    inserted_items_count = 0 # just for debug
    ids = 0
    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_number=page_number, page_size=50)
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunk_ids = list(range(ids, ids + len(page_chunks))
        )
        ids += len(page_chunks)
        # reset the collection only once (first page), otherwise every page would wipe the previous ones
        is_inserted =  nlp_controller.index_into_vector_db(project=project, chunks=page_chunks , chunks_ids=chunk_ids, do_reset=(push_request.do_reset and page_number == 1))
        page_number += 1
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": False,
                    "Signal": ResponseSignal.InsertIntoDataBaseVectorError.value
                },
            )
        inserted_items_count += len(page_chunks)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": True,
            "Signal": ResponseSignal.InsertIntoDataBaseVectorSuccess.value,
            "inserted_items_count": inserted_items_count
        },
    )


@nlp_router.get("/push/{project_id}")
async def get_project_index_info( project_id:str,request: Request):
    project_model = await ProjectModel.create_instance(db_client = request.app.state.db_client)
        
    project = await project_model.get_or_create_project(project_id=project_id)
    nlp_controller = NLPController(vector_db_client=request.app.state.vector_db_client, generation_client=request.app.state.generation_client, embedding_client=request.app.state.embedding_client)

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)
    if collection_info is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": False,
                "Signal": ResponseSignal.GetCollectionInfoError.value
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": True,
            "Signal": ResponseSignal.GetCollectionInfoSuccess.value,
            "collection_info": collection_info
        },
    )
@nlp_router.post("/search/{project_id}")
async def search_index(project_id:str,request: Request, search_request: IndexSearchRequest):
    project_model = await ProjectModel.create_instance(db_client = request.app.state.db_client)
        
    project = await project_model.get_or_create_project(project_id=project_id)
    nlp_controller = NLPController(vector_db_client=request.app.state.vector_db_client, generation_client=request.app.state.generation_client, embedding_client=request.app.state.embedding_client)

    results = nlp_controller.search_vector_db_collecrion(project=project, query=search_request.query, limit=search_request.limit)

    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": False,
                "Signal": ResponseSignal.DbVectorSearchError.value
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": True,
            "Signal": ResponseSignal.DbVectorSearchSuccess.value,
            "results": results
        },
    )