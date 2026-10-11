from pydantic import BaseModel, Field, validator
from typing import Optional
from bson import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: str = Field(...,min_length=1)

    @validator("project_id")
    def validate_project_id(cls, v):
        if not v:
            raise ValueError("project_id must not be empty")
        return v

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        populate_by_name = True