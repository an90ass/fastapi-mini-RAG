from enum import Enum

class ResponseSignal(Enum):
    FileValidatedSuccess = "file_validated_success"
    FileValidationFailed = "file_validation_failed"
    FileTypeNotAllowed = "file_type_not_allowed"
    FileSizeExceeded = "file_size_exceeded"
    FileValid = "file_valid"
    FileUploadSuccess = "file_upload_success"
    FileUploadFailed = "file_upload_failed"
    ProjectNotFoundError = "project_not_found"

    # For processing
    FileProcessedSuccess = "file_processed_success"
    FileProcessingFailed = "file_processing_failed"
    FileNotFound = "file_not_found"
    NoFilesError = "no_files_error"
    FileIdError = "no_file_found_with_this_id"

    # For NLP
    InsertIntoDataBaseVectorError = "insert_into_vector_db_error"
    InsertIntoDataBaseVectorSuccess = "insert_into_vector_db_success"
    GetCollectionInfoSuccess = "get_collection_info_success"
    GetCollectionInfoError = "get_collection_info_error"
    DbVectorSearchError = "db_vector_search_error"
    DbVectorSearchSuccess = "db_vector_search_success"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"