from fastapi import APIRouter,Depends,UploadFile,status
from fastapi.responses import JSONResponse
from dependencies.SettingsDependency import get_app_settings
from controllers import DataController,ProcessController
from models import ResponseSignal
from schemes import ProcessRequest
import aiofiles
import logging
logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"],
    responses={404: {"description": "Not found"}},
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id:str, file : UploadFile = None, app_settings=Depends(get_app_settings)):
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
    file_path = data_controller.generate_unique_filename(
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

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": is_valid,
            "message": result_signal,
         
   } )

@data_router.post("/process/{project_id}")
async def process_file(request: ProcessRequest, project_id: str):
    file_id = request.file_id
    chunk_size = request.chunk_size 
    overlap_size = request.overlap_size 
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

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": True,
            "message": ResponseSignal.FileProcessedSuccess.value,
            "data": file_chunks,
        },
    )   