from .base_data_model import BaseDataModel
from .enums.db_enum import DataBaseEnum
from .db_schemes import DataChunk
from bson import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self,chunk:DataChunk) -> DataChunk:
        chunk_dict = chunk.dict(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(chunk_dict)
        if result is None:
            return None
        chunk.id = result.inserted_id
        return chunk
    async def get_chunk(self,chunk_id:str) -> DataChunk:
        chunk = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        return DataChunk(**chunk)

    async def insert_many_chunks(self,chunks: list,batch_size:int=100):
        for i in range(0,len(chunks),batch_size):
            batch = chunks[i:i+batch_size]
            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_none=True))
                for chunk in batch
                
            ]
            await self.collection.bulk_write(operations)
        return len(chunks)

    async def delete_chunks_by_project_id(self,project_id:ObjectId):
        result=  await self.collection.delete_many({"chunk_project_id":project_id})
        return result.deleted_count