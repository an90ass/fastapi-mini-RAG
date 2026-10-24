from pydantic import BaseModel


class PushRequest(BaseModel):
    do_reset: bool = False

class IndexSearchRequest(BaseModel):
    query: str
    limit: int = 10