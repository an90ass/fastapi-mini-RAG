import os

from .base_controller import BaseController

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
    def get_project_path(self, project_id: str) -> str:
        project_path  = os.path.join(self.files_dir, project_id)
        
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        return project_path