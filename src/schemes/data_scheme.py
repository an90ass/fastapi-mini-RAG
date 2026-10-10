from pydantic import BaseModel, Field
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: str = Field(..., description="The ID of the project to process.")
    chunk_size:Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset : Optional[bool] = False
