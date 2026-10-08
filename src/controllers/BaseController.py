from helpers.config import Settings, get_settings
import os
import random
import string
class BaseController:
    def __init__(self,):
        self.app_settings = get_settings()
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_path, "assets", "files")
    def generate_random_string(self, length: int = 12) -> str:
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))