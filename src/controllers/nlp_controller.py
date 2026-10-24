from .base_controller import BaseController
from typing import List
from models.db_schemes import DataChunk, Project
from stores.llm.LLMEnums import DocumnetTypeEnum
import json
class NLPController(BaseController):
    def __init__(self, vector_db_client: object, generation_client: object, embedding_client: object):
        super().__init__()

        self.vector_db_client = vector_db_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client

    def create_collection_name(self, project_id: str) -> str:
        return f"collection_{project_id}".strip()
    def rest_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vector_db_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vector_db_client.get_collection_info(collection_name=collection_name)
        return json.loads(
           json.dumps(collection_info, default=lambda o: o.__dict__)
        ) 
    def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                             chunks_ids: List[int], do_reset: bool = False):
        # step 1 : get collection name 
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step 2: manage items 
        texts = [c.chunk_text for c in chunks ]
        metadata = [c.chunk_metadata for c in chunks]

        vectors = self.embedding_client.embed_texts(
            texts=texts, document_type=DocumnetTypeEnum.DOCUMENT.value
        )
        if not vectors or len(vectors) != len(texts) or any(v is None for v in vectors):
            return False


         # step 3: create collection to vector db if not exist 
        _ = self.vector_db_client.create_collection(
            collection_name=collection_name, 
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset)
        
         # step 4: insert into vector db
        _ = self.vector_db_client.insert_many(
            record_ids=chunks_ids,
            collection_name=collection_name,
            texts=texts, vectors=vectors, metadata=metadata,
            batch_size=50)

        return True
    def search_vector_db_collecrion(self, project: Project, query: str, limit: int = 10):
        # step 1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step 2: get text embedding vector
        vector = self.embedding_client.embed_text(text = query, document_type = DocumnetTypeEnum.QUERY.value)

        if not vector or len(vector) == 0: 
            return [], False
        # step 3: search vector db 
        results = self.vector_db_client.search_by_vector(
            collection_name=collection_name, 
            vector=vector,
            limit=limit)

        if not results or len(results) == 0:
            return False
        return json.loads(
                   json.dumps(results, default=lambda o: o.__dict__)
                ) 
