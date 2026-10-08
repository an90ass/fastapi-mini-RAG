import os

from .BaseController import BaseController
from .ProjectController import ProjectController

from langchain_community.document_loaders import (
    TextLoader,
    PyMuPDFLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

from models import ProcessingEnum


class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(
            project_id=project_id
        )

    def get_file_extension(self, filename: str) -> str:
        return os.path.splitext(filename)[1].lower()

  
    def get_file_loader(
        self,
        file_id: str,
        file_path: str = None,
    ):
        file_extension = self.get_file_extension(file_id)

        if file_path is None:
            file_path = os.path.join(self.project_path, file_id)

        # If the file path does not exist, try supported extensions.
        if not os.path.isfile(file_path):
            for extension in (
                ProcessingEnum.PDF.value,
                ProcessingEnum.TXT.value,
            ):
                candidate_path = file_path + extension

                if os.path.isfile(candidate_path):
                    file_path = candidate_path
                    file_extension = extension
                    break
            else:
                raise FileNotFoundError(
                    f"File not found: {file_path}"
                )

        if file_extension == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")

        if file_extension == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)

        raise ValueError(
            f"Unsupported file extension: {file_extension}"
        )



    def get_file_content(self, file_id: str):
        file_path = os.path.join(
            self.project_path,
            file_id,
        )

        file_loader = self.get_file_loader(
            file_id=file_id,
            file_path=file_path,
        )

        return file_loader.load()

    def process_file_content(
        self,
        file_content: list,
        file_id: str,
        chunk_size: int = 100,
        chunk_overlap_size: int = 20,
    ):
        if not file_content:
            raise ValueError(
                f"No content extracted from file: {file_id}"
            )

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0"
            )

        if chunk_overlap_size < 0:
            raise ValueError(
                "chunk_overlap_size cannot be negative"
            )

        if chunk_overlap_size >= chunk_size:
            raise ValueError(
                "chunk_overlap_size must be smaller than chunk_size"
            )

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap_size,
            length_function=len,
        )

        file_content_texts = [
            record.page_content
            for record in file_content
        ]

        file_content_metadata = [
            record.metadata
            for record in file_content
        ]

        chunks = text_splitter.create_documents(
            texts=file_content_texts,
            metadatas=file_content_metadata,
        )

        return chunks

