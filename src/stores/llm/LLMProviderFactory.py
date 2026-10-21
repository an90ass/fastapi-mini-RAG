from .LLMEnums import LLMEnums
from .providers.cohere_provider import CohereProvider,OpenAIProvider

class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider:str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key =  self.config.OPENAI_API_KEY,
                api_url = self.config.OPENAI_API_URL,
                defult_input_max_characters = self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                defult_generation_max_output_tokens = self.config.GENERATION_DAFAULT_MAX_TOKENS,
                defult_generation_temperature = self.config.GENERATION_DAFAULT_TEMPERATURE
                
                )
        elif provider == LLMEnums.COHERE.value:
            return CohereProvider(
                self.config.COHERE_API_KEY,
                defult_input_max_characters = self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                defult_generation_max_output_tokens = self.config.GENERATION_DAFAULT_MAX_TOKENS,
                defult_generation_temperature = self.config.GENERATION_DAFAULT_TEMPERATURE             
                )

        return None