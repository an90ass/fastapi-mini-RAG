from enum import Enum

class ResponseSignal(Enum):
    FileValidatedSuccess = "file_validated_success"
    FileValidationFailed = "file_validation_failed"
    FileTypeNotAllowed = "file_type_not_allowed"
    FileSizeExceeded = "file_size_exceeded"
    FileValid = "file_valid"
    FileUploadSuccess = "file_upload_success"
    FileUploadFailed = "file_upload_failed"

    # For processing
    FileProcessedSuccess = "file_processed_success"
    FileProcessingFailed = "file_processing_failed"
    FileNotFound = "file_not_found"
    NoFilesError = "no_files_error"
    FileIdError = "no_file_found_with_this_id"
    
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"