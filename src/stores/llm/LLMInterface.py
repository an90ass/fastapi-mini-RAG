from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def set_generation_model(self, model_id:str):
        pass 
    
    @abstractmethod
    def set_embedding_model(self, model_id:str, embedding_size: int):
        pass
    
    @abstractmethod
    def generate_text(self, prompt:str, chat_history:list = [], max_output_tokens:int = None, temperature:float = None):
        pass
    
    @abstractmethod
    def embed_text(self, text:str, document_type:str = None):
        pass

    def embed_texts(self, texts:list, document_type:str = None):
        # default fallback: one call per text; providers should override with a real batch call
        return [self.embed_text(text=t, document_type=document_type) for t in texts]

    @abstractmethod
    def construct_prompt(self, prompt:str, role:str):
        pass
