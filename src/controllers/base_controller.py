from helpers.config import Settings, get_settings
import os
import random
import string
class BaseController:
    def __init__(self,):
        self.app_settings = get_settings()
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_path, "assets", "files")
        self.databsae_dir = os.path.join(self.base_path, "assets", "database")

    def generate_random_string(self, length: int = 12) -> str:
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))
    def get_database_path(self, database_name: str ):
        db_path = os.path.join(self.databsae_dir, database_name)
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        return db_path