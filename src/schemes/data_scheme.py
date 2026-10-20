from pydantic import BaseModel, Field
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: Optional[str] = None
    chunk_size:Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset : Optional[bool] = False
