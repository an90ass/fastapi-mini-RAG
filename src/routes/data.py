import os

from bson import ObjectId
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
from models.db_schemes import DataChunk,Asset
from models.asset_model import AssetModel
from models.enums.asset_type_enum import AssetTypeEnum
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
    project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)
    
    # Store the file information in the database
    asset_model = await AssetModel.create_instance(db_client=request.app.state.db_client)
    asset_resource = Asset(
        asset_project_id = project.id,
        asset_type = AssetTypeEnum.FILE.value,
        asset_name = file_id,
        asset_size = os.path.getsize(file_path),
        
    )
    asset_record = await asset_model.create_asset(asset_resource)
    

   
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": is_valid,
            "message": result_signal,
            "file_id": str( asset_record.id),
   } )

@data_router.post("/process/{project_id}")
async def process_file(request: Request,process_request: ProcessRequest, project_id: str):
    chunk_size = process_request.chunk_size 
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)
    asset_model = await AssetModel.create_instance(db_client=request.app.state.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)

    project_file_ids = {}
    if process_request.file_id is not None:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id

          )
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": False,
                    "message": ResponseSignal.FileIdError.value,
                },
            )
        project_file_ids = {
            asset_record.id : asset_record.asset_name
        }
    else: # process all files
        
        project_files = await asset_model.get_all_project_assets(asset_project_id=project.id,asset_type=AssetTypeEnum.FILE.value)
        project_file_ids = {
            record.id : record.asset_name
            for record in project_files
}
    if len(project_file_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": False,
                "message": ResponseSignal.NoFilesError.value,
            },
        )
    
    process_controller = ProcessController(project_id=project_id)
    inserted_chunks_count,processed_files = await process(
        request=request,
        process_controller=process_controller,
        project_file_ids=project_file_ids,
        project_id=project.id,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
        do_reset=do_reset
    )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": True,
            "message": ResponseSignal.FileProcessedSuccess.value,
            "inserted_chunks_count": inserted_chunks_count,
            "processed_files": processed_files
        },
    )   


async def process(request: Request, process_controller: ProcessController, project_file_ids: dict, project_id: str, chunk_size: int, overlap_size: int, do_reset: bool,):   
    chunk_model = await ChunkModel.create_instance(db_client=request.app.state.db_client)
            
    if do_reset:
        await chunk_model.delete_chunks_by_project_id(project_id=project_id)
              
    
    inserted_chunks_count = 0
    processed_files = 0
    for asset_id, file_id, in project_file_ids.items():  
            file_content = process_controller.get_file_content(file_id=file_id)
            if file_content is None:
                logger.error(f"File content is None: {file_id}")
                continue
    
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
                    chunk_project_id=project_id,
                    chunk_asset_id=ObjectId(asset_id)
                )
    
                for i,chunk in enumerate(file_chunks)
            ]
    
            inserted_chunks_count += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
            processed_files += 1
    return inserted_chunks_count, processed_files
