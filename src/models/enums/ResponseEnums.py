from enum import Enum

class ResponseSignal(Enum):
    FileValidatedSuccess = "file_validated_success"
    FileValidationFailed = "file_validation_failed"
    FileTypeNotAllowed = "file_type_not_allowed"
    FileSizeExceeded = "file_size_exceeded"
    FileValid = "file_valid"
    FileUploadSuccess = "file_upload_success"
    FileUploadFailed = "file_upload_failed"


    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"