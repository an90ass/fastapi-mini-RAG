from .base_data_model import BaseDataModel
from .db_schemes import Project
from .enums.db_enum import DataBaseEnum
class ProjectModel(BaseDataModel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def create_project(self, project: Project) -> str:
        # by_alias=True writes `_id` (Mongo's key), not `id`.
        # exclude_none=True omits `_id` when unset so Mongo generates it.
        project_dict = project.dict(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(project_dict)
        project.id = result.inserted_id
        return project


    async def get_or_create_project(self, project_id:str) -> Project:
        existing_project = await self.collection.find_one({"project_id": project_id})
        if existing_project:
            return Project(**existing_project)
        else:    
            return await self.create_project(
              Project(project_id=project_id)
            )
    async def get_all_projects(self,page:int=1,page_size :int=10) -> list[Project]:
        # count total numbers of documents
        total_documents = await self.collection.count_documents({})
        total_pages = total_documents // page_size 
        if total_documents % page_size > 0:
            total_pages += 1  
        cursor = self.collection.find().skip((page-1)*page_size).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        return projects ,total_pages