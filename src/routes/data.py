from fastapi import APIRouter,Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from dependencies.settings_dependency import get_app_settings
from controllers import DataController,ProcessController
from models import ResponseSignal
from schemes import ProcessRequest
import aiofiles
import logging
from models.project_model import ProjectModel
from models.chunk_model import ChunkModel
from models.db_schemes import DataChunk
logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"],
    responses={404: {"description": "Not found"}},
)

@data_router.post("/upload/{project_id}")
async def upload_file(request: Request,project_id:str, file : UploadFile = None, app_settings=Depends(get_app_settings)):

    
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": is_valid,
                "message": result_signal,
                          },
        )
    file_path,file_id = data_controller.generate_unique_filepath(
        original_filename=file.filename,
        project_id=project_id,
    )
    try:

        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):  # Read the file in chunks
                await out_file.write(chunk)  # Write the chunk to the destination file
        
    except Exception as e:
        logger.error(f"An error occurred while saving the file: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": False,
                "message": ResponseSignal.FileUploadFailed.value,
            },
        )
    result_signal = ResponseSignal.FileUploadSuccess.value
    # create project after file upload
    project_model = ProjectModel(db_client=request.app.state.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": is_valid,
            "message": result_signal,
            "file_id": file_id,
   } )

@data_router.post("/process/{project_id}")
async def process_file(request: Request,process_request: ProcessRequest, project_id: str):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size 
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = ProjectModel(db_client=request.app.state.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)


    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        chunk_overlap_size=overlap_size
    )
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": False,
                "message": ResponseSignal.FileProcessingFailed.value,
            },
        )

    file_chunks_records = [
        DataChunk(
            chunk_text= chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id
        )

          for i,chunk in enumerate(file_chunks)
    ]

    chunk_model = ChunkModel(db_client=request.app.state.db_client)
 
    if do_reset:
        await chunk_model.delete_chunks_by_project_id(project_id=project.id)
    inserted_chunks_count = await chunk_model.insert_many_chunks(chunks=file_chunks_records)
   
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": True,
            "message": ResponseSignal.FileProcessedSuccess.value,
            "inserted_chunks_count": inserted_chunks_count,
        },
    )   



