import os

from fastapi import UploadFile

from .BaseController import BaseController
from models import ResponseSignal
from .ProjectController import ProjectController
import re
class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_uploaded_file(self, file: UploadFile):
        # Validate the file type
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FileTypeNotAllowed.value
        
        # Validate the file size
        file_size = len(file.file.read()) # bytes
        max_size_bytes = self.app_settings.FILE_MAX_SIZE * 1024 * 1024  # Convert MB to bytes
        if file_size > max_size_bytes:
            return False, ResponseSignal.FileSizeExceeded.value
        # Reset the file pointer after reading
        file.file.seek(0)
        return True, ResponseSignal.FileValid.value

    def generate_unique_filepath(self, original_filename: str, project_id: str) -> str:
        project_dir_path = ProjectController().get_project_path(project_id=project_id)
        cleaned_file_name = self.get_cleaned_filename(original_filename)

        while True:
            random_key = self.generate_random_string(length=12)
            file_id = f"{random_key}_{cleaned_file_name}"
            new_file_path = os.path.join(project_dir_path, file_id)
            if not os.path.exists(new_file_path):
                return new_file_path, file_id
    def get_cleaned_filename(self, original_filename: str) -> str:
        cleaned_file_name = re.sub(r'[^\w.]', '', original_filename.strip())
        cleaned_file_name = cleaned_file_name.replace(' ', '_')
        return cleaned_file_name