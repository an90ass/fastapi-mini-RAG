from .providers import QdrantDbProvider
from .VectorDbEnums import VectorDbEnums
from controllers.base_controller import BaseController
class VectorDbProviderFactory:
    def __init__ (self, config: dict):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str):
        if provider == VectorDbEnums.QDRANT.value:
            db_path = self.base_controller.get_database_path(self.config.VECTOR_DB_PATH)
            return QdrantDbProvider(
                db_path = db_path, 
                distance_method = self.config.VECTOR_DB_DISTANCE_METHOD)

        raise ValueError(
            f"Unsupported VECTOR_DB_BACKEND '{provider}'. "
            f"Supported: {[e.value for e in VectorDbEnums]}"
        )