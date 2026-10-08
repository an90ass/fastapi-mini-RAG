

from fileinput import filename
import os

from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models import ProcessingEnum
class ProcessController(BaseController):
    def __init__(self,project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, filename: str) -> str:
        return os.path.splitext(filename)[1].lower()

    def get_file_loader(self, file_id: str,file_path: str):
        # Implementation for getting file loader based on file ID
        file_extension = self.get_file_extension(file_id)
        file_path = os.path.join(self.project_path, file_id)
        if file_extension == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        if file_extension == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        return None
    def get_file_content(self, file_id: str):
        file_loader = self.get_file_loader(file_id=file_id,file_path=self.project_path)
        if file_loader:
            return file_loader.load()
        return None
    def process_file_content(self, file_content:list , file_id: str, chunk_size: int = 100, chunk_overlap_size: int = 20):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap_size,
            length_function=len,
        )
        file_content_texts = [record.page_content for record in file_content]
        file_content_metadata = [record.metadata for record in file_content]
        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_metadata
        )
        return chunks