import os
from .base import LLMService
from .deepseek import DeepseekLLMService

def get_llm_service() -> LLMService:
    provider = os.getenv("LLM_PROVIDER", "deepseek").lower()

    if provider == "deepseek":
        return DeepseekLLMService()
    else:
        raise ValueError(f"不支持的 LLM provider: {provider}")
