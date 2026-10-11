from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    OPENAI_API_URL: Optional[str] = None

    FILE_ALLOWED_TYPES: List[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    MONGODB_URI: str
    MONGODB_DATABASE: str

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str
    COHERE_API_KEY: str

    GENERATION_MODEL_ID_LITERAL: List[str]
    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int

    INPUT_DAFAULT_MAX_CHARACTERS: int
    GENERATION_DAFAULT_MAX_TOKENS: int
    GENERATION_DAFAULT_TEMPERATURE: float

    VECTOR_DB_BACKEND_LITERAL: List[str]
    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METHOD: str
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: Optional[int] = None

    PRIMARY_LANG: str
    DEFAULT_LANG: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_TASK_SERIALIZER: str
    CELERY_TASK_TIME_LIMIT: int
    CELERY_TASK_ACKS_LATE: bool
    CELERY_WORKER_CONCURRENCY: int
    CELERY_FLOWER_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("OPENAI_API_URL", "VECTOR_DB_PGVEC_INDEX_THRESHOLD", mode="before")
    @classmethod
    def empty_str_to_none(cls, value):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        return value

def get_settings() -> Settings:
    return Settings()
