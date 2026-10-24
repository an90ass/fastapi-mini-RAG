from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums,DocumnetTypeEnum
import cohere 
from cohere.errors import TooManyRequestsError
import logging
import time
class CohereProvider(LLMInterface):
     def __init__(
                self,
                api_key: str,
                defult_input_max_characters:int=1000,
                defult_generation_max_output_tokens:int=1000,
                defult_generation_temperature:float=0.2  
                ) :
            self.api_key = api_key
            self.defult_input_max_characters = defult_input_max_characters
            self.defult_generation_max_output_tokens = defult_generation_max_output_tokens
            self.defult_generation_temperature = defult_generation_temperature
    
            self.generation_model_id = None 
            self.embedding_model_id = None
            self.embedding_size = None
    
            self.client = cohere.Client(api_key=self.api_key)
            self.logger = logging.getLogger(__name__)

     def set_generation_model(self, model_id:str):
            self.generation_model_id = model_id
        
     def set_embedding_model(self, model_id:str, embedding_size: int):
            self.embedding_model_id = model_id
            self.embedding_size = embedding_size

     def generate_text(self, prompt:str, chat_history:list = [], max_output_tokens:int = None, temperature:float = None):
        if not self.client:
                     self.logger.error("Cohere client is not initialized")
                     return None
        if not self.generation_model_id:
            self.logger.error("Generation model is not set")
            return None
        max_output_tokens = max_output_tokens if max_output_tokens else self.defult_generation_max_output_tokens
        temperature = temperature if temperature else self.defult_generation_temperature

        response = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt),
            max_tokens = max_output_tokens,
            temperature = temperature
        )

        if response is None or response.text is None:
            self.logger.error("Generation response is empty")
            return None
        return response.text

     def embed_text(self, text, document_type = None):
           if not self.client:
                self.logger.error("Cohere client is not initialized")
                return None
           if not self.embedding_model_id:
               self.logger.error("Embedding model is not set")
               return None
           
           input_type = CohereEnums.DOCUMENT.value
           if document_type == DocumnetTypeEnum.QUERY.value:
               input_type = CohereEnums.QUERY.value
                

           response = self.client.embed(
                 model=self.embedding_model_id,
                 texts = [self.process_text(text)],
                 input_type=input_type,
                 embedding_types=['float']
                 )
           if response is None or response.embeddings is None or not response.embeddings.float_:
               self.logger.error("Embedding response is empty")
               return None
           return response.embeddings.float_[0]

     def embed_texts(self, texts: list, document_type: str = None, batch_size: int = 96, max_retries: int = 5):
           if not self.client:
                self.logger.error("Cohere client is not initialized")
                return None
           if not self.embedding_model_id:
               self.logger.error("Embedding model is not set")
               return None

           input_type = CohereEnums.DOCUMENT.value
           if document_type == DocumnetTypeEnum.QUERY.value:
               input_type = CohereEnums.QUERY.value

           all_vectors = []
           for i in range(0, len(texts), batch_size):
               batch = [self.process_text(t) for t in texts[i:i + batch_size]]

               for attempt in range(max_retries):
                   try:
                       response = self.client.embed(
                           model=self.embedding_model_id,
                           texts=batch,
                           input_type=input_type,
                           embedding_types=['float']
                       )
                       break
                   except TooManyRequestsError:
                       wait = min(60, 2 ** attempt * 5)
                       self.logger.warning(f"Cohere rate limit hit, retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
                       time.sleep(wait)
               else:
                   self.logger.error("Cohere rate limit: max retries exceeded")
                   return None

               if response is None or response.embeddings is None or not response.embeddings.float_:
                   self.logger.error("Embedding response is empty")
                   return None
               all_vectors.extend(response.embeddings.float_)

           return all_vectors


     
     def construct_prompt(self, prompt, role):
           return {
                 "role": role,
                 "text": self.process_text(prompt)  
           }
    
     def process_text(self, text:str):
            return text[:self.defult_input_max_characters].strip()
        
        